from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()

db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

if not db_host or not db_user or not db_password or not db_name:
    raise ValueError("DB_HOST, DB_USER, DB_PASSWORD, and DB_NAME must be set in .env file")


def create_schema():
    connection = mysql.connector.connect(
        host=db_host, user=db_user, password=db_password, database=db_name
    )
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS patients (
                id VARCHAR(64) PRIMARY KEY,
                data JSON NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id VARCHAR(64) PRIMARY KEY,
                data JSON NOT NULL
            )
            """
        )

        connection.commit()
        cursor.close()
        print("tables are ready")
    finally:
        connection.close()


if __name__ == '__main__':
    create_schema()
