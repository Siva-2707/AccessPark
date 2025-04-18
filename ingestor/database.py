import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()
import logging
from logger_config import logger

logger = logging.getLogger(__name__)

def get_connection():
    con = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=os.getenv("DB_PORT")
    )
    logger.info("Connected to the database")
    return con   

def create_database_if_not_exist():
    con = get_connection()
    cur = con.cursor()
    cur.execute('''
            CREATE DATABASE IF NOT EXISTS parking
            ''')
    cur.execute('USE parking')
    con.commit()
    logger.info("Database created or already exists")

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
    logger.info("Table created or already exists")

def insert_into_accessibility_parking(record_hash, city_lot_id, name, no_of_spots, location, city, state, country):
    con = get_connection()
    cur = con.cursor()
    cur.execute('''
        INSERT IGNORE INTO accessibility_parking (record_hash, city_lot_id, name, no_of_spots, location, city, state, country)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ''', (record_hash,city_lot_id, name, no_of_spots, location, city, state, country))
    con.commit()
    logger.info(f"Inserted record with hash {record_hash} into the database")
    
def close_connection(con):
    con.close()
    logger.info("Database connection closed")
