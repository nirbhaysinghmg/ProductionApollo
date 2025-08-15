import os
import pickle
import glob
import re
import shutil
import json
import pandas as pd
import nltk
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import numpy as np
import logging
from mysql.connector import Error
from db_functions import get_db_connection  # Assuming this function is defined elsewhere

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Download required NLTK resources if missing
for resource in ["punkt", "stopwords", "wordnet"]:
    try:
        nltk.data.find(f"corpora/{resource}")
    except LookupError:
        nltk.download(resource)

# Initialize lemmatizer and stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))

def is_notna(value):
    # If value is array-like, check that all elements are not NA
    if isinstance(value, (list, tuple, np.ndarray)):
        return np.all(pd.notna(value))
    # Otherwise, check the scalar value
    return pd.notna(value)

def clean_text(text):
    text = re.sub(r"[^a-zA-Z0-9.,_!?'\s]", "", str(text))
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def safe_json_loads(s):
    # Remove control characters (0x00-0x1F) from the string
    cleaned = re.sub(r'[\x00-\x1f]+', '', s)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logging.error(f"JSONDecodeError for string: {s[:50]}... Error: {e}")
        return {}

def clean_metadata(meta):
    """
    Recursively convert None values to empty strings within metadata.
    """
    if isinstance(meta, dict):
        return {k: clean_metadata(v) for k, v in meta.items()}
    elif isinstance(meta, list):
        return [clean_metadata(item) for item in meta]
    else:
        return meta if meta is not None else ""

def preprocess_documents(dataframe, text_column, metadata_column):
    """
    Preprocess documents to store only `text_column` as embeddings
    and keep only `metadata_column` as metadata (converted to string if needed).
    """
    documents = []
    for _, row in dataframe.iterrows():
        if text_column in row and row[text_column]:
            cleaned_text = clean_text(row[text_column])
            value = row.get(metadata_column, None)
            if value is not None and is_notna(value):
                # If value is a dict, convert None values to empty strings; otherwise, store as string.
                metadata = clean_metadata(value) if isinstance(value, dict) else {"metadata": str(value) if value is not None else ""}
            else:
                metadata = {}
            documents.append(Document(page_content=cleaned_text, metadata=metadata))
    return documents

def reset_vector_database(persist_directory, embeddings):
    if os.path.exists(persist_directory):
        try:
            existing_vectordb = Chroma(persist_directory=persist_directory, embedding=embeddings)
            if len(existing_vectordb) > 0:
                logging.info(f"Existing Chroma DB contains {len(existing_vectordb)} entries.")
                user_input = input("Reset DB? (y/n): ")
                if user_input.lower() != "y":
                    logging.info("Skipping reset.")
                    return
        except Exception:
            pass
        logging.info(f"Cleaning up old DB at {persist_directory}...")
        shutil.rmtree(persist_directory)
        logging.info("Old DB cleaned up.")

# ------------------- MySQL functions ----------------------
def create_tables(cursor):
    """Creates necessary tables if they don't exist."""
    create_projects_table = """
    CREATE TABLE IF NOT EXISTS projects (
        project_id INT AUTO_INCREMENT PRIMARY KEY,
        project_name VARCHAR(255) NOT NULL UNIQUE,
        developer_name VARCHAR(255) DEFAULT 'Unknown Developer',
        sector VARCHAR(100) NOT NULL,
        city VARCHAR(100) NOT NULL,
        project_status VARCHAR(100) NOT NULL,
        category VARCHAR(100) NOT NULL,
        average_price VARCHAR(100) DEFAULT 'Price Not Available',
        launch_date DATE DEFAULT NULL,
        completion_date DATE DEFAULT NULL,
        project_score INT DEFAULT 0,
        project_summary TEXT DEFAULT NULL
    ) ENGINE=InnoDB;
    """
    
    create_apartment_sizes_table = """
    CREATE TABLE IF NOT EXISTS apartment_sizes (
        apartment_id INT AUTO_INCREMENT PRIMARY KEY,
        project_id INT NOT NULL,
        size VARCHAR(50) NOT NULL,
        min_price DECIMAL(12,2) DEFAULT NULL,
        max_price DECIMAL(12,2) DEFAULT NULL,
        FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """
    try:
        cursor.execute(create_projects_table)
        cursor.execute(create_apartment_sizes_table)
        logging.info("✅ Tables checked/created successfully.")
    except Error as e:
        logging.error(f"Table creation error: {e}")

def convert_price_to_crores(price_str):
    """Converts price strings like '2.05 - 9.45 Cr in INR' or '95 Lakhs in INR' into Crores."""
    if not price_str:
        return None  # Return None if empty

    cleaned_str = price_str.replace("Cr in INR", "").replace("Lakhs in INR", "").replace("+", "").strip()

    try:
        if " - " in cleaned_str:
            min_price, max_price = map(float, cleaned_str.split(" - "))
        else:
            min_price = max_price = float(cleaned_str)
        if "lakhs" in price_str.lower():
            min_price /= 100
            max_price /= 100
        return min_price, max_price
    except ValueError:
        return None, None

def convert_to_mysql_date(date_input):
    """
    Converts various date formats to 'YYYY-MM-DD' for MySQL.
    """
    from datetime import datetime
    try:
        if not date_input or str(date_input).strip().lower() in ["na", "not available", ""]:
            return None
        if len(date_input.split()) == 2:
            return datetime.strptime(date_input, "%B %Y").strftime("%Y-%m-01")
        if "." in date_input and len(date_input.split(".")) == 3:
            return datetime.strptime(date_input, "%d.%m.%Y").strftime("%Y-%m-%d")
        if len(date_input) == 10 and "-" in date_input:
            return date_input
    except ValueError as e:
        logging.error(f"❌ Date conversion error for '{date_input}': {e}")
        return None
    return None

def validate_json(metadata):
    """
    Ensures required fields exist in the JSON data and applies default values.
    Enforces that 'apartment_sizes' is a list and 'price_range' is a dict.
    """
    required_fields = [
        "project_name", "developer_name", "sector", "city", "project_status",
        "category", "average_price", "launch_date", "completion_date", "project_score",
        "apartment_sizes", "price_range"
    ]
    
    for field in required_fields:
        if field not in metadata or metadata[field] is None:
            logging.warning(f"⚠️ Missing field '{field}' in metadata. Assigning default value.")
            if field == "developer_name":
                metadata[field] = "Unknown Developer"
            elif field == "project_score":
                metadata[field] = 0
            elif field in ["apartment_sizes", "price_range"]:
                metadata[field] = None
            elif field in ["launch_date", "completion_date"]:
                metadata[field] = None
            else:
                metadata[field] = "Unknown"
        else:
            if isinstance(metadata[field], str):
                value = metadata[field].strip().lower()
                if value in ["na", "not available", ""]:
                    logging.warning(f"⚠️ Missing or invalid field '{field}' in metadata. Assigning default value.")
                    if field == "developer_name":
                        metadata[field] = "Unknown Developer"
                    elif field == "project_score":
                        metadata[field] = 0
                    elif field in ["apartment_sizes", "price_range"]:
                        metadata[field] = None
                    elif field in ["launch_date", "completion_date"]:
                        metadata[field] = None
                    else:
                        metadata[field] = "Unknown"
    
    if metadata.get("apartment_sizes") is None or not isinstance(metadata["apartment_sizes"], list):
        if metadata.get("apartment_sizes") is not None:
            logging.warning("⚠️ Field 'apartment_sizes' expected as a list. Converting to empty list.")
        metadata["apartment_sizes"] = []
    
    if metadata.get("price_range") is None or not isinstance(metadata["price_range"], dict):
        if isinstance(metadata.get("price_range"), str):
            if metadata.get("apartment_sizes") and isinstance(metadata["apartment_sizes"], list) and metadata["apartment_sizes"]:
                logging.warning("⚠️ Field 'price_range' is a string; converting to dict for each apartment size.")
                pr_str = metadata["price_range"]
                metadata["price_range"] = {size: pr_str for size in metadata["apartment_sizes"]}
            else:
                logging.warning("⚠️ Field 'price_range' is a string but no valid apartment_sizes found; converting to empty dict.")
                metadata["price_range"] = {}
        else:
            logging.warning("⚠️ Field 'price_range' expected as a dict. Converting to empty dict.")
            metadata["price_range"] = {}
    return metadata

def process_csv_file(file_path, connection):
    """Process a single CSV file and insert its records into the database."""
    logging.info(f"📂 Processing file: {file_path}")
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        logging.error(f"❌ Error reading {file_path}: {e}")
        return

    cursor = connection.cursor()
    for _, row in df.iterrows():
        try:
            raw_metadata = row["metadata"]
            metadata = json.loads(raw_metadata) if isinstance(raw_metadata, str) else {}
            metadata = clean_metadata(metadata)
            
            # Check if metadata is a list; if so, log entire metadata JSON and use the first element.
            if isinstance(metadata, list):
                logging.info("Processing project with problematic metadata (list): " + json.dumps(metadata, indent=2))
                metadata = metadata[0] if metadata else {}
            else:
                logging.info("Processing project with metadata: " + json.dumps(metadata, indent=2))
            
            project_summary = row.get("contextual_data", "").strip()
            
            metadata = validate_json(metadata)
            
            # If developer_name is a list, join it into a string.
            if isinstance(metadata["developer_name"], list):
                metadata["developer_name"] = ", ".join(metadata["developer_name"])
            
            formatted_launch_date = convert_to_mysql_date(metadata["launch_date"])
            formatted_completion_date = convert_to_mysql_date(metadata["completion_date"])
            
            # Ensure project_score is an integer.
            if isinstance(metadata["project_score"], int):
                pass
            elif isinstance(metadata["project_score"], str) and metadata["project_score"].isdigit():
                metadata["project_score"] = int(metadata["project_score"])
            else:
                metadata["project_score"] = 0
            
            # Check if the project already exists.
            check_query = "SELECT project_id FROM projects WHERE project_name = %s"
            cursor.execute(check_query, (metadata["project_name"],))
            existing_project = cursor.fetchone()
            
            if existing_project:
                logging.warning(f"⚠️ Project '{metadata['project_name']}' already exists. Skipping insert.")
                continue
            
            project_query = """
            INSERT INTO projects (
                project_name, developer_name, sector, city,
                project_status, category, average_price, launch_date,
                completion_date, project_score, project_summary
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            project_values = (
                metadata["project_name"], metadata["developer_name"], metadata["sector"], metadata["city"],
                metadata["project_status"], metadata["category"], metadata["average_price"],
                formatted_launch_date, formatted_completion_date, metadata["project_score"], project_summary
            )
            
            cursor.execute(project_query, project_values)
            project_id = cursor.lastrowid
            
            apartment_query = """
            INSERT INTO apartment_sizes (project_id, size, min_price, max_price)
            VALUES (%s, %s, %s, %s)
            """
            for size in metadata["apartment_sizes"]:
                price_value = metadata["price_range"].get(size, "")
                if price_value:
                    min_price, max_price = convert_price_to_crores(price_value)
                else:
                    min_price, max_price = None, None
                apartment_values = (project_id, size, min_price, max_price)
                cursor.execute(apartment_query, apartment_values)
            
            connection.commit()
            logging.info(f"✅ Data for '{metadata['project_name']}' inserted successfully!")
        
        except json.JSONDecodeError as json_error:
            logging.error(f"❌ JSON Parsing Error: {json_error}")
        except Error as db_error:
            logging.error(f"❌ Database error: {db_error}")
            connection.rollback()
    
    cursor.close()

def process_multiple_csv_files():
    """Process all CSV files matching the specified pattern."""
    CSV_DIR = "/home/ubuntu/test/new/project/data"
    CSV_FILE_PATTERN = "all_projects_29Mar25*_context.csv"
    file_pattern = os.path.join(CSV_DIR, CSV_FILE_PATTERN)
    csv_files = glob.glob(file_pattern)
    if not csv_files:
        logging.warning("⚠️ No CSV files found matching the pattern.")
        return

    connection = get_db_connection()
    if not connection:
        logging.error("❌ Failed to connect to the database.")
        return

    try:
        cursor = connection.cursor()
        create_tables(cursor)
        cursor.close()

        for file_path in csv_files:
            process_csv_file(file_path, connection)
    finally:
        if connection.is_connected():
            connection.close()
            logging.info("🔒 Database connection closed.")

# Start processing all CSV files matching the pattern
process_multiple_csv_files()
