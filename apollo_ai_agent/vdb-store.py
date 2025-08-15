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

# Function: Clean text
def clean_text(text):
    #text = re.sub(r"\b(Sector)\s(\d+)\b", r"\1_\2", str(text))
    text = re.sub(r"[^a-zA-Z0-9.,_!?'\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# Enhanced safe_json_loads function to handle extra data error
# Enhanced safe_json_loads to handle markdown blocks, control characters, and decoding issues
def safe_json_loads(s):
    try:
        if not isinstance(s, str):
            return {}

        # Strip markdown code block if present (```json ... ``` or ``` ... ```)
        s = s.strip().strip("`").strip("json").strip("`").strip()

        # Remove control characters
        cleaned = re.sub(r'[\x00-\x1f]+', '', s)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            if "Extra data" in str(e):
                try:
                    decoder = json.JSONDecoder()
                    obj, end = decoder.raw_decode(cleaned)
                    return obj
                except Exception as e2:
                    print(f"⚠️ Failed after handling Extra data: {e2}")
            else:
                print(f"⚠️ JSONDecodeError: {str(e)}")
        return {}
    except Exception as e:
        print(f"❌ Unexpected error while parsing JSON: {str(e)}")
        return {}


# Function: Process Documents
def preprocess_documents(dataframe, text_column, metadata_column):
    """
    Preprocess documents to store only `text_column` as embeddings
    and keep only `metadata_column` as metadata (as a raw string).
    """
    documents = []
    for _, row in dataframe.iterrows():
        if text_column in row and row[text_column]:
            cleaned_text = clean_text(row[text_column])  # Clean text for vectorization
            # Use helper function to check metadata value
            value = row.get(metadata_column, None)
            if value is not None and is_notna(value):
                metadata = {"metadata": str(value)}
            else:
                metadata = {}
            documents.append(Document(page_content=cleaned_text, metadata=metadata))
    return documents

# Function: Reset Chroma DB only if needed
def reset_vector_database(persist_directory, embeddings):
    if os.path.exists(persist_directory):
        try:
            existing_vectordb = Chroma(persist_directory=persist_directory, embedding=embeddings)
            if len(existing_vectordb) > 0:
                print(f"Existing Chroma DB contains {len(existing_vectordb)} entries.")
                user_input = input("Reset DB? (y/n): ")
                if user_input.lower() != "y":
                    print("Skipping reset.")
                    return
        except Exception:
            pass
        print(f"Cleaning up old DB at {persist_directory}...")
        shutil.rmtree(persist_directory)
        print("Old DB cleaned up.")

# Setup
persist_directory = "./chroma_db"
csv_dir = "./data/"
csv_pattern = os.path.join(csv_dir, "all*21Apr25*_context_json.csv")

# Initialize Embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")

# Reset Vector DB
reset_vector_database(persist_directory, embeddings)

# Load CSV Files
csv_files = glob.glob(csv_pattern)
if not csv_files:
    raise ValueError(f"No CSV files found in {csv_dir}")

df_list = []
for file in csv_files:
    chunk_iter = pd.read_csv(file, chunksize=10000)  # Read in chunks
    for chunk in chunk_iter:
        df_list.append(chunk)

df = pd.concat(df_list, ignore_index=True)
df = df.dropna(subset=["contextual_data"])  # Drop rows with empty text

# Use enhanced safe_json_loads for metadata parsing
df["metadata"] = df["metadata"].apply(lambda x: safe_json_loads(x) if isinstance(x, str) else {})

print(f"Loaded {len(csv_files)} CSV files with {len(df)} records.")

# Preprocess and Vectorize
documents = preprocess_documents(df, text_column="contextual_data", metadata_column="metadata")
vectordb = Chroma.from_documents(documents=documents, embedding=embeddings, persist_directory=persist_directory)

print(f"Stored {len(documents)} documents in Chroma at '{persist_directory}'.")

# Save Metadata
metadata_file = os.path.join(persist_directory, "metadata.pkl")
with open(metadata_file, "wb") as meta_f:
    pickle.dump(df[["contextual_data", "metadata"]], meta_f)

print(f"Metadata stored at {metadata_file}")
