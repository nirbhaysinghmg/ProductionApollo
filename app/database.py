import mysql.connector
from mysql.connector import Error

# MySQL Configuration (same as root analytics.py)
MYSQL_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "nirbhay",
    "password": "Nirbhay@123",
    "database": "chatbot_analytics"
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise
    return None

def execute_query(query, params=None, fetch=True):
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        
        if fetch:
            result = cursor.fetchall()
        else:
            connection.commit()
            result = None
        
        cursor.close()
        return result
    except Error as e:
        print(f"Error executing query: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection and connection.is_connected():
            connection.close()

def update_sessions_table():
    try:
        columns = execute_query("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'sessions' 
            AND TABLE_SCHEMA = DATABASE()
        """)
        existing_columns = [col['COLUMN_NAME'] for col in columns]

        if 'message_count' not in existing_columns:
            execute_query("""
                ALTER TABLE sessions
                ADD COLUMN message_count INT DEFAULT 0
            """, fetch=False)

        if 'last_message_time' not in existing_columns:
            execute_query("""
                ALTER TABLE sessions
                ADD COLUMN last_message_time DATETIME
            """, fetch=False)

        if 'status' not in existing_columns:
            execute_query("""
                ALTER TABLE sessions
                ADD COLUMN status ENUM('active', 'completed', 'error') DEFAULT 'active'
            """, fetch=False)

        if 'location_data' not in existing_columns:
            execute_query("""
                ALTER TABLE sessions
                ADD COLUMN location_data JSON
            """, fetch=False)

        if 'duration' not in existing_columns:
            execute_query("""
                ALTER TABLE sessions
                ADD COLUMN duration INT DEFAULT 0
            """, fetch=False)

        if 'end_time' not in existing_columns:
            execute_query("""
                ALTER TABLE sessions
                ADD COLUMN end_time DATETIME
            """, fetch=False)
            
        print("Sessions table schema updated successfully")
    except Error as e:
        print(f"Error updating sessions table: {e}")