import psycopg2
from config import load_config
import pandas as pd
import csv
import functionsHelp 


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
    
    cur.execute("CREEATE TABLE ЫТФЛУ")
    
    