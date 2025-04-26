import psycopg2
from config import load_config
import pandas as pd
import csv
import functionsHelp 

FILENAME = "data.csv"

def connect(config):
    """Connect to the PostgreSQL database server"""
    try:
        conn = psycopg2.connect(**config)
        print('Connected to the PostgreSQL server.')
        return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
        return None

if __name__ == '__main__':
    config = load_config()
    conn = connect(config)
    cur = conn.cursor()
    while True:
        print(" \nSelect the action with SQL or CSV (enter number):")
        print("1. Show data from SQL database")
        print("2. Show data from CSV file")
        print("3. Insert entry into SQL database")
        print("4. Add record to CSV file")
        print("5. Filtering and output from SQL")
        print("6. Update SQL record")
        print("7. Searching by template")
        print("8. Page choose print")
        print("9. Exit")

        try:
            choice = int(input("your choice: "))
        except ValueError:
            print("Please enter the correct number.")
            continue

        if choice == 1:
            functionsHelp.csv_data_print(FILENAME)
        elif choice == 2:
            functionsHelp.data_print(cur)
        elif choice == 3:
            functionsHelp.add_upsert(conn)
        elif choice == 4:
            functionsHelp.append_to_csv(FILENAME, conn)
        elif choice == 5:
            functionsHelp.filtering(conn)
        elif choice == 6:
            functionsHelp.update_data_sql(conn)
        elif choice == 7:
            functionsHelp.search_by_pattern(conn)
        elif choice == 8:
            functionsHelp.query_with_pagination(conn)
        elif choice == 9:
            print("Completion of work.")
            break
        else:
            print("No such option. Please try again.")
