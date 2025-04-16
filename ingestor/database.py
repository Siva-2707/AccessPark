import mysql.connector

def get_connection():
    con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="parking",
    port=3306
    )
    return con   

def create_database_if_not_exist():
    con = get_connection()
    cur = con.cursor()
    cur.execute('''
            CREATE DATABASE IF NOT EXISTS parking
            ''')
    cur.execute('USE parking')
    con.commit()

def create_table_if_not_exist():
    con = get_connection()
    cur = con.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS accessibility_parking (
            record_hash VARCHAR(64) PRIMARY KEY,
            city_lot_id INT,
            name VARCHAR(255),
            no_of_spots INT,
            location VARCHAR(255),
            city VARCHAR(100),
            state VARCHAR(100),
            country VARCHAR(100)
        )''')
    con.commit()

def insert_into_accessibility_parking(record_hash, city_lot_id, name, no_of_spots, location, city, state, country):
    con = get_connection()
    cur = con.cursor()
    cur.execute('''
        INSERT IGNORE INTO accessibility_parking (record_hash, city_lot_id, name, no_of_spots, location, city, state, country)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ''', (record_hash,city_lot_id, name, no_of_spots, location, city, state, country))
    con.commit()
    
def close_connection(con):
    con.close()
