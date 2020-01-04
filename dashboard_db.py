import sqlite3
import os
import pandas as pd

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')

#connect to sqlite database
def connect(db_path = DEFAULT_PATH):
    try:
        conn = sqlite3.connect(db_path)
        create_desc_table(conn)#we make sure there's a description table every time we connect
        print(list_tables(conn))
    except:
        print("Error")
    return conn
def list_tables(conn):
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
    return tables

def create_table(conn, df):
    tables = list_tables(connect()) #get the list of tables
    new_table_name = 'test' + str(len(tables))
    df.to_sql(new_table_name, con = conn)

def retrieve_table(conn):
    tables = list_tables(connect()) #get the list of tables
    last_table_name = 'test' + str(len(tables)-1)
    df = pd.read_sql_query('SELECT * FROM ' + last_table_name, conn)
    return df

def create_desc_table(conn):
    try:
        sql_create_desc_table = """
            CREATE TABLE IF NOT EXISTS desc(
            id integer PRIMARY KEY,
            date text NOT NULL,
            desc text NOT NULL,
            sRate float NOT NULL
            );"""
        cur = conn.cursor()
        cur.execute(sql_create_desc_table)
    except:
        print("Error")

def add_desc_entry(conn,description, sample_rate):
    try:
        sql_insert_query = """
            INSERT INTO desc
            (id, date, desc, sRate)
            VALUES
            (1,'19:81:10:10', 'the first insert', 0.00032)
            """
        cur = conn.cursor()
        cur.execute(sql_insert_query)
        test = pd.read_sql_query('SELECT * FROM desc', conn)
        print(test)
    except:
        print("couldn't add description")

            
