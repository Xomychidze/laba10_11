import psycopg2
import tabulate
from config import load_config
import pandas as pd
from tabulate import tabulate
import csv


def data_print(cur):
    cur.execute("SELECT * FROM laba10")
    for person in cur.fetchall():
        print(f"{person[0]} {person[1]} {person[2]} {person[3]} {person[4]}")


#---------------------------------------------------------------------------------------------------------------------------------------------       
def upsert_record(conn, first_name, last_name, phone, age):
    sql = """
        INSERT INTO laba10 (first_name, last_name, phone, age)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (phone) DO UPDATE  -- phone должен быть UNIQUE
        SET 
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            age = EXCLUDED.age
        RETURNING id;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (first_name, last_name, phone, age))
            record_id = cur.fetchone()[0]
            conn.commit()
            load_data_sql(conn)
            return record_id
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Ошибка UPSERT: {e}")
        return None

def add_upsert(conn):
    while True:
        row = input("Write first name, last name, phone and age ").split()
        try:
            if  check_name(row[0]) and check_name(row[1]) and check_phone(row[2]) and len(row) == 4:
                upsert_record(conn, row[0], row[1], row[2],int(row[3]))
                break
            elif not check_name(row[0]): 
                print("Insorect data 1 name")
            elif not check_name(row[1]): 
                print("Insorect data last name")
            elif not check_phone(row[2]): 
                print("Insorect phone")
        except ValueError as e:
            print(f"Incorect age: {e}")

    

#---------------------------------------------------------------------------------------------------------------------------------------------
def csv_data_print(file_name: str):
    """Print CSV data in a formatted table"""
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f, delimiter=' ')
            data = list(csv_reader)
        print(tabulate(
            [(data[i][0], data[i][1], data[i][2], data[i][3]) for i in range(1,len(data))],
            headers=[data[0][0],data[0][1], data[0][2], data[0][3]],
            tablefmt="grid"
        ))
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
        

#---------------------------------------------------------------------------------------------------------------------------------------------
def append_to_csv(FILENAME, conn):
    with open(FILENAME, "a", newline="", encoding='utf-8') as file: 
        writer = csv.writer(file, delimiter=' ')
        
        print("\nEnter new data (format: FirstName LastName Phone Age)")
        print("Type 'quit' to exit")
        
        while True:
            user_input = input("> ").strip()
            
            if user_input.lower() == 'quit':
                print(f"New data appended to {FILENAME}")
                break
                
            row = user_input.split()
            
            if len(row) == 4:
                try:
                    int(row[3]) 
                    if check_name(row[1]) and check_name(row[0]):
                        if check_phone(row[2]) and len(row[2]) == 11 and check_unique_phone(row[2]) == False:
                            writer.writerow(row) 
                            upsert_record(conn, row[0], row[1], row[2], row[3])
                            print("Entry added successfully")
                        else:
                            if row[2] != 11: 
                                print("Phone number shouldn't be more than 11")
                            elif check_unique_phone(row[2]): 
                                change_value()
                            else:
                                print("Error: phone number are misspelled ")
                                print("Example: 8~~~")
                    else: 
                        print("Error: FirstName and Last name are misspelled ")
                        print("Example: Nurik Timuruly")
                except ValueError:
                    print("Error: Age must be a number")
            else:
                print("Invalid format. Use: FirstName LastName Phone Age")
                
                
#---------------------------------------------------------------------------------------------------------------------------------------------       

def change_value(file_name : str, change : list[str]):
    with open(file_name, 'r', encoding='utf-8') as f:
        csv_reader = csv.reader(f, delimiter=' ')
        data = list(csv_reader)
        print(data)

         
#---------------------------------------------------------------------------------------------------------------------------------------------       
def check_name(test_str): # check first and last name are misspelled
    import re
    pattern = r'^[A-Z]+[a-z]+[a-z]$'
    if re.search(pattern, test_str):
        return True
    else:
        return False


#---------------------------------------------------------------------------------------------------------------------------------------------
def check_phone(test_str): # check phone number is misspelled
    import re
    pattern = r'^(\+7|8)\d{10}$'
    if re.search(pattern, test_str):
        return True
    else:
        return False


#---------------------------------------------------------------------------------------------------------------------------------------------

def check_unique_phone(phone : str, file_name : str): # check if phone number exits  then Name change 
    with open(file_name) as f:
        reader = csv.reader(f)
        for row in reader:
            check = row[0].split()
            if check[2] == phone:
                return True
        return False   

#---------------------------------------------------------------------------------------------------------------------------------------------

def filtering(conn):
    print("Write a property that we will use as filter")
    print("1. First name")
    print("2. Last name")
    print("3. Phone number")
    print("4. age")
    
    try: 
        command = int(input())
        print("Select filter type: ASC or DESC")
        while True:
            type_filter = input()
            if type_filter == "ASC" or type_filter == "DESC":
                break 
            else:
                print("write ACS or DESC")
        property = ""
        while True: 
            if command == 1: 
                property = "first_name"
                break
            elif command == 2: 
                property = "last_name"
                break
            elif command == 3: 
                property = "phone"
                break
            elif command == 4: 
                property = "age"
                break
            else: 
                print("Incorect number")
        if conn is not None:
                try:
                    with conn.cursor() as cur:
                        command = f'SELECT * FROM laba10 ORDER BY {property} {type_filter}'
                        cur.execute(command) 
                        
                        
                        
                        for person in cur.fetchall():
                            print(f"{person[0]} {person[1]} {person[2]} {person[3]} {person[4]}")
                        
                except psycopg2.Error as e:
                    print(f"Ошибка при создании таблицы: {e}")
                finally:
                    conn.close()  

            
    except ValueError:
        print("Write number") 
        
    
#---------------------------------------------------------------------------------------------------------------------------------------------


def delete_data(conn): 
    print("Write a property that we want to delete")
    print("1. First name")
    print("2. Last name")
    print("3. Phone number")
    print("4. age")
    try: 
        command = int(input())
        property = ""
        while True: 
            if command == 1: 
                property = "first_name"
                break
            elif command == 2: 
                property = "last_name"
                break
            elif command == 3: 
                property = "phone"
                break
            elif command == 4: 
                property = "age"
                break
            else: 
                print("Incorect number")  
        try:
            if property == "age":
                condition = int(input())    
            if property == "phone": 
                while True:
                    condition = input()
                    if check_phone(condition):
                        break
                    else: 
                        print("Incorect firstname")
            if property == "first_name" or property == "last_name":
                while True: 
                    condition = input()
                    if check_name(condition):
                        break   
                    else: 
                        print("Incorect lastname")
        except ValueError as e:
            print(f"Incorect value: {e}")
                
        if conn is not None:
                try:
                    with conn.cursor() as cur: 
                        cur.execute(f'DELETE FROM laba10 WHERE {property} = %s;', (condition,))
                        conn.commit()
                        print("zaebis")
                        load_data_sql(conn)
                except psycopg2.Error as e:
                    print(f"Error while creating the table: {e}")
                finally:
                    conn.close()  
    except ValueError:
        print("Write number") 


#---------------------------------------------------------------------------------------------------------------------------------------------

def load_data_sql(conn): 
    if conn is not None: 
        try: 
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM laba10")
                rows = cur.fetchall()
                row_1 = ["name", "last_name", "phone", "age"]
                with open("data.csv", "w", newline='') as f:
                    writer = csv.writer(f, delimiter=' ')
                    writer.writerow(row_1)
                    for row in rows:
                        writer.writerow(row)

                print("Data was successfully exported to data.csv")
        except psycopg2.Error as e:
            print(f"Error loading data: {e}")

#---------------------------------------------------------------------------------------------------------------------------------------------

def update_data_sql(conn):
    print("Select the property to search for:")
    print("1. First name\n2. Last name\n3. Phone number\n4. Age")
    
    try:
        command = int(input("Enter the property number: "))
        property = set_property(command)
        condition = choose_condition(property)

        print("Select the property to update:")
        print("1. First name\n2. Last name\n3. Phone number\n4. Age")
        command_set = int(input("Enter the property number: "))
        property_set = set_property(command_set)
        condition_set = choose_condition(property_set)

        if conn is not None:
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        f'UPDATE laba10 SET {property_set} = %s WHERE {property} = %s;',
                        (condition_set, condition)
                    )
                    conn.commit()
                    print("Data updated successfully.")
                    load_data_sql(conn)
            except psycopg2.Error as e:
                print(f"Error while updating data: {e}")
    except ValueError:
        print("The property number is incorrect.")

#---------------------------------------------------------------------------------------------------------------------------------------------
           
def set_property(command):
    mapping = {
        1: "first_name",
        2: "last_name",
        3: "phone",
        4: "age"
    }
    if command in mapping:
        return mapping[command]
    else:
        raise ValueError("The property number is incorrect.")

#---------------------------------------------------------------------------------------------------------------------------------------------

def choose_condition(property):
    try:
        if property == "age":
            return int(input("Enter age: "))
        elif property == "phone":
            while True:
                phone = input("Enter your phone number: ")
                if check_phone(phone):
                    return phone
                print("Incorrect phone number.")
        else:
            while True:
                name = input(f"Enter {property.replace('_', ' ')}: ")
                if check_name(name):
                    return name
                print(f"Incorrect value for {property.replace('_', ' ')}.")
    except ValueError as e:
        raise ValueError(f"Input error: {e}")
    
#---------------------------------------------------------------------------------------------------------------------------------------------

def search_by_pattern(conn):
    pattern = input("Enter the template (part of name, surname or phone): ").strip()

    if not pattern:
        print("The template should not be empty.")
        return

    like_pattern = f"%{pattern}%"

    try:
        with conn.cursor() as cur:
            query = """
                SELECT * FROM laba10
                WHERE first_name ILIKE %s
                   OR last_name ILIKE %s
                   OR phone ILIKE %s;
            """
            cur.execute(query, (like_pattern, like_pattern, like_pattern))
            results = cur.fetchall()

            if results:
                print("Found records:")
                for row in results:
                    print(row)
            else:
                print("No matches found.")
    except psycopg2.Error as e:
        print(f"Search error: {e}")

#---------------------------------------------------------------------------------------------------------------------------------------------

def query_with_pagination(conn):
    try:
        limit = int(input("How many entries should be displayed on the page? "))
        offset = int(input("Which record to start with (offset)? "))

        if limit <= 0 or offset < 0:
            print("Limit должен быть > 0, offset ≥ 0.")
            return

        with conn.cursor() as cur:
            query = "SELECT * FROM laba10 ORDER BY id LIMIT %s OFFSET %s;"
            cur.execute(query, (limit, offset))
            rows = cur.fetchall()

            if rows:
                print(f"Display of records from {offset + 1} to {offset + len(rows)}:")
                for row in rows:
                    print(row)
            else:
                print("There are no entries to display on this page.")
    except ValueError:
        print("Please enter numerical values.")
    except psycopg2.Error as e:
        print(f"Error while executing the request: {e}")

