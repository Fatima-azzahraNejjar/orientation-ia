import psycopg2
import psycopg2.extras
import os

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    if not DATABASE_URL:
        raise Exception("DATABASE_URL non configurée.")
    conn = psycopg2.connect(DATABASE_URL)
    return conn