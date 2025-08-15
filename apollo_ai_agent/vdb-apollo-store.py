import os
import glob
import re
import shutil
import pickle
import pandas as pd
import nltk
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import numpy as np

# ────────────────────────────────────────────────────────────────────────────────
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
    """
    Return True if a scalar or all elements of an array-like are not NA.
    """
    if isinstance(value, (list, tuple, np.ndarray)):
        return np.all(pd.notna(value))
    return pd.notna(value)


def clean_text(text):
    """
    Remove non-alphanumeric punctuation, collapse whitespace.
    """
    text = re.sub(r"[^a-zA-Z0-9.,_!?'\s]", "", str(text))
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def preprocess_documents(dataframe, text_column, metadata_column=None):
    """
    Build a list of langchain.schema.Document objects from `text_column`.
    If `metadata_column` is provided and exists, include it under key "metadata";
    otherwise, documents have empty metadata.
    """
    documents = []
    for _, row in dataframe.iterrows():
        # Skip rows with missing text
        txt = row.get(text_column, None)
        if not txt or pd.isna(txt):
            continue

        cleaned = clean_text(txt)

        if metadata_column:
            meta_val = row.get(metadata_column, None)
            if meta_val is not None and is_notna(meta_val):
                metadata = {"metadata": str(meta_val)}
            else:
                metadata = {}
        else:
            metadata = {}

        documents.append(Document(page_content=cleaned, metadata=metadata))

    return documents


def reset_vector_database(persist_directory, embeddings):
    """
    If a Chroma DB exists at `persist_directory` and is non-empty, prompt to reset.
    Otherwise, remove the directory outright.
    """
    if os.path.exists(persist_directory):
        try:
            existing = Chroma(persist_directory=persist_directory, embedding=embeddings)
            count = len(existing)
        except Exception:
            count = 0

        if count > 0:
            answer = input(f"Chroma DB at {persist_directory} has {count} entries. Reset? (y/n): ")
            if answer.strip().lower() != "y":
                print("Skipping vector DB reset.")
                return

        shutil.rmtree(persist_directory)
        print(f"Deleted existing DB at {persist_directory}")


# ────────────────────────────────────────────────────────────────────────────────
# Configuration
persist_directory = "./chroma_tyres_db"
csv_dir = "./data/"
csv_pattern = os.path.join(csv_dir, "apolloTyres_combined_cleaned.csv")

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")

# Optionally reset
reset_vector_database(persist_directory, embeddings)

# Load CSV files in chunks
csv_files = glob.glob(csv_pattern)
if not csv_files:
    raise FileNotFoundError(f"No CSV files matching {csv_pattern}")

df_chunks = []
for path in csv_files:
    for chunk in pd.read_csv(path, chunksize=10_000):
        df_chunks.append(chunk)
df = pd.concat(df_chunks, ignore_index=True)

# Only keep rows with tyre_detailed_summary
df = df.dropna(subset=["tyre_detailed_summary"])
print(f"Loaded {len(csv_files)} files; total records after dropna: {len(df)}")

# Preprocess text and build documents
documents = preprocess_documents(
    df,
    text_column="tyre_detailed_summary",
    metadata_column=None
)
print(f"Prepared {len(documents)} documents for embedding.")

# Create or load Chroma and persist
vectordb = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    persist_directory=persist_directory
)
print(f"Stored {len(documents)} documents in Chroma at '{persist_directory}'.")

# (Optional) Save the raw summaries for later inspection
summary_file = os.path.join(persist_directory, "tyre_summaries.pkl")
with open(summary_file, "wb") as f:
    pickle.dump(df["tyre_detailed_summary"].tolist(), f)
print(f"Tyre summaries pickled to {summary_file}.")
