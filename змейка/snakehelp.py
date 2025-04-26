import psycopg2
import tabulate
from config import load_config
import csv
import re

# Основные функции для работы с таблицей snake
def data_print(cur):
    """Вывод всех записей из таблицы snake"""
    cur.execute("SELECT * FROM snake")
    print(tabulate.tabulate(
        cur.fetchall(),
        headers=["ID", "Nickname", "Level", "Score"],
        tablefmt="grid"
    ))

def upsert_record(conn, nickname, level, score):
    """Добавление или обновление записи в таблице snake"""
    sql = """
        INSERT INTO snake (nickname, level, score)
        VALUES (%s, %s, %s)
        ON CONFLICT (nickname)
        DO UPDATE SET
            level = EXCLUDED.level,
            score = EXCLUDED.score
        RETURNING id;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (nickname, level, score))
            record_id = cur.fetchone()[0]
            conn.commit()
            return record_id
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Ошибка UPSERT: {e}")
        return None

def add_record(conn):
    """Добавление новой записи через консольный ввод"""
    while True:
        try:
            print("Введите данные (Nickname Level Score):")
            data = input().split()
            if len(data) != 3:
                print("Нужно ввести 3 значения!")
                continue
                
            nickname, level, score = data
            if not check_nickname(nickname):
                print("Некорректный nickname (только буквы и цифры, 3-20 символов)")
                continue
                
            if not level.isdigit() or not score.isdigit():
                print("Level и Score должны быть числами!")
                continue
                
            upsert_record(conn, nickname, int(level), int(score))
            print("Запись добавлена/обновлена!")
            break
            
        except Exception as e:
            print(f"Ошибка: {e}")

# Вспомогательные функции
def check_nickname(nickname):
    """Проверка корректности nickname"""
    return bool(re.match(r'^[a-zA-Z0-9_]{3,20}$', nickname))

def export_to_csv(conn, filename="snake_data.csv"):
    """Экспорт данных в CSV файл"""
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM snake")
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'nickname', 'level', 'score'])
                writer.writerows(cur)
        print(f"Данные экспортированы в {filename}")
    except Exception as e:
        print(f"Ошибка экспорта: {e}")

def import_from_csv(conn, filename):
    """Импорт данных из CSV файла"""
    try:
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Пропускаем заголовок
            with conn.cursor() as cur:
                for row in reader:
                    upsert_record(conn, row[1], int(row[2]), int(row[3]))
        print(f"Данные из {filename} успешно импортированы!")
    except Exception as e:
        print(f"Ошибка импорта: {e}")

def delete_record(conn, nickname):
    """Удаление записи по nickname"""
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM snake WHERE nickname = %s", (nickname,))
            conn.commit()
            print(f"Запись {nickname} удалена!")
    except Exception as e:
        print(f"Ошибка удаления: {e}")

def search_records(conn, pattern):
    """Поиск записей по шаблону"""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM snake 
                WHERE nickname ILIKE %s 
                   OR CAST(level AS TEXT) ILIKE %s 
                   OR CAST(score AS TEXT) ILIKE %s
            """, (f"%{pattern}%", f"%{pattern}%", f"%{pattern}%"))
            
            results = cur.fetchall()
            if results:
                print(tabulate.tabulate(
                    results,
                    headers=["ID", "Nickname", "Level", "Score"],
                    tablefmt="grid"
                ))
            else:
                print("Записи не найдены")
    except Exception as e:
        print(f"Ошибка поиска: {e}")

def get_top_scores(conn, limit=10):
    """Получение топовых результатов"""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM snake 
                ORDER BY score DESC 
                LIMIT %s
            """, (limit,))
            
            print(tabulate.tabulate(
                cur.fetchall(),
                headers=["ID", "Nickname", "Level", "Score"],
                tablefmt="grid"
            ))
    except Exception as e:
        print(f"Ошибка получения топовых результатов: {e}")