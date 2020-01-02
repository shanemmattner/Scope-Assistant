import sqlite3
import os
import pandas as pd

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')

#connect to sqlite database
def connect(db_path = DEFAULT_PATH):
    try:
        conn = sqlite3.connect(db_path)
    except Error as e:
        print(e)
    return conn

def create_table(conn, df):
    df.to_sql('test1', con = conn)

def retrieve_table(conn):
    df = pd.read_sql_query('select * from test1', conn)
    return df

