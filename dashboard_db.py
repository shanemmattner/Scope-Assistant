import sqlite3
import os
import pandas as pd
from datetime import datetime

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')

#connect to sqlite database
def connect(db_path = DEFAULT_PATH):
    try:
        conn = sqlite3.connect(db_path)
        create_desc_table(conn)#we make sure there's a description table every time we connect
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
            sRate float NOT NULL,
            push float,
            start float,
            end float
            );"""
        cur = conn.cursor()
        cur.execute(sql_create_desc_table) #no commit needed, this is table structure stuff
    except:
        print("Error")

def add_desc_entry(conn,description, sample_rate,end_time):
    try:
        #get the date
        now = datetime.today()
        frmt_now = now.strftime("%Y-%m-%d %H:%M:%S") #TODO: convert from UTC to CST
        sql_insert_query = """
            INSERT INTO desc
            (date, desc, sRate, push, start, end)
            VALUES
            ("{}","{}",{},{},{},{})
            """.format(frmt_now, description, sample_rate, 0, 0, end_time)
        cur = conn.cursor()
        cur.execute(sql_insert_query)
        conn.commit()
        desc_table = pd.read_sql_query("SELECT * FROM desc", conn)
        print(desc_table)
    except Exception as e:
        print("couldn't add description: ", e)

            
