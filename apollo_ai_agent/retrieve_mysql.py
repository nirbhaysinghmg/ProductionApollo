import os
import mysql.connector
import logging
from mysql.connector import Error
from db_functions import get_db_connection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def execute_query(sql_query):
    """
    Executes a given SQL query and returns results as a list of dictionaries.

    Args:
        sql_query (str): SQL query to execute.

    Returns:
        list: List of dictionaries containing the query results.
    """
    connection = get_db_connection()
    if not connection:
        return []

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(sql_query)
        results = cursor.fetchall()

        if not results:
            print("⚠️ No records found.")
            return []

        # Print all records with first 100 characters
        print("\n--- MySQL Query Results ---")
        for idx, row in enumerate(results, start=1):
            row_preview = {key: str(value)[:100] for key, value in row.items()}  # Trim to 100 chars
            print(f"Result {idx}: {row_preview}")
            print("-" * 50)

        return results  # Returns a list of dictionaries

    except Error as e:
        logging.error(f"❌ SQL Execution Error: {e}")
        return []
    finally:
        cursor.close()
        connection.close()

# Example usage
# if __name__ == "__main__":
#     sample_query = "SELECT * FROM projects LIMIT 5;"  # Change your SQL query here
#     response = execute_query(sample_query)
#     print(response)  # Print formatted response

