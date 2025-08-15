import os
import pickle
import pandas as pd
from rank_bm25 import BM25Okapi
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
#from query_normalizer import normalize_query

# Initialize lemmatizer and stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))

# Define a set of domain-specific terms that should be preserved (or upper-cased)
domain_terms = { term.lower() for term in {
    'Chintamanis', 'Aviana Green Estates Pvt Ltd', 'Under Construction', 'Godrej Vrikshya', 
    'Godrej Properties Limited', 'new launch', 'Indiabulls Centrum Park', 'Indiabulls Real Estate', 
    'Ready to Move In   Since Jul, 2018', 'Signature Global Grand IVA', 'Signature Global India Limited', 
    'Ready To Move', 'Satya The Hermitage', 'Satya Group Builders', 'HCBS Auroville', 'HCBS Developments', 
    'under construction.', 'Whiteland Urban Resort', 'Whiteland Corporation', 'New Launch', 
    'Mahira Homes 103', 'Mahira Buildtech Pvt. Ltd', 'Ansal Estella', 'Ansal Housing.', 
    'Landmark The Residency', 'Landmark Group Builders', 'Ansals Highland Park', 'Ansals Buildwell Ltd.', 
    'Ready to Move', 'Suncity Avenue 102', 'Suncity Projects', 'Emaar Gurgaon Greens', 'Emaar India', 
    'Shapoorji Pallonji Joyville Gurugram', 'Shapoorji Pallonji', 'Partially Ready To Move', 
    'Adani M2K Oyster Grande', 'Adani Realty', 'Conscient Heritage Max', 'BPTP Amstoria', 
    'Puri Emerald Bay', 'ATS Triumph', 'Hero Homes', 'Godrej Summit', 'Godrej Properties', 'Zara Aavaas', 
    'Zara Group And Perfect Buildwell', 'Yashika 104', 'Yashika Group', 'ATS Sanctuary 105', 
    'ATS Homekraft', 'Godrej Meridien', 'Paras Dews', 'Paras Buildtech', 'Elan The Presidential', 
    'Elan Group', 'MRG The Crown', 'MRG World', 'Sobha Altus', 'Sobha Limited', 'M3M Woodshire', 
    'M3M India', 'Signature Global Solera', 'Earth Esabella', 'Earth Infrastructure', 'Agrante Beethoven 8',
    'Agrante', 'Possession Status', 'Sobha City', 'Experion The Heartsong', 'Experion Developers', 
    'Experion The Westerlies', 'Raheja Vedaanta', 'Raheja Developers', 'Agrante Kavyam', 
    'Agrante Realty Builders', 'International City by Sobha Phase 1', 'ATS Tourmaline', 'ATS Group', 
    'ATS Kocoon', 'ATS Infrastructure and Chintels India', 'Chintels Serenity', 'Chintels India', 
    'Chintels Paradiso', 'Raheja Shilas', 'Raheja Atharva', 'Brisk Lumbini Terrace Homes', 
    'Brisk Infrastructure', 'SBTL Caladium', 'Solutrean Building Technologies'
}}

# Sample valid word list (includes multi-word phrases like builder names and sectors)
word_list = [
    "apartment", "flat", "house", "gurgaon", "2bhk", "3bhk", "4bhk",
    "whiteland", "godrej", "signature", "elan", "under construction", "ready to move", "new launch"
]

def preprocess_text(text):
    """
    Preprocess text by tokenizing, lemmatizing, and handling domain-specific patterns.

    Args:
        text (str): Input text.

    Returns:
        list: List of processed tokens.
    """
    tokens = word_tokenize(str(text).lower())
    processed_tokens = []
    i = 0

    while i < len(tokens):
        # Handle "Sector <number>" as a single token
        if tokens[i] == "sector" and i + 1 < len(tokens) and tokens[i + 1].isdigit():
            processed_tokens.append(f"{tokens[i]} {tokens[i + 1]}")
            i += 2
            continue

        # Handle "1 to 2 cr" as a single token
        if (i + 3 < len(tokens) and tokens[i].isdigit() and tokens[i + 1] == "to" and
            tokens[i + 2].isdigit() and tokens[i + 3] in {"cr", "lakh"}):
            processed_tokens.append(f"{tokens[i]} to {tokens[i + 2]} {tokens[i + 3]}")
            i += 4
            continue

        # Retain domain-specific terms without modification
        if tokens[i] in domain_terms or tokens[i].lower() in domain_terms:
            processed_tokens.append(tokens[i].lower())  # Preserve the original word for domain terms
        elif tokens[i] not in stop_words:
            processed_tokens.append(lemmatizer.lemmatize(tokens[i]))
        i += 1

    return processed_tokens

# Load Pre-created BM25 Index and Metadata
def load_bm25_index(index_dir="./bm25_index"):
    """
    Load the BM25 index and metadata from pre-created files.

    Args:
        index_dir (str): Directory where BM25 index and metadata are stored.

    Returns:
        tuple: Loaded BM25 index and metadata DataFrame.
    """
    bm25_file = os.path.join(index_dir, "bm25.pkl")
    metadata_file = os.path.join(index_dir, "metadata.pkl")

    if not os.path.exists(bm25_file) or not os.path.exists(metadata_file):
        raise FileNotFoundError(f"BM25 index or metadata not found in {index_dir}. Please ensure the index is created.")

    with open(bm25_file, "rb") as bm25_f:
        bm25 = pickle.load(bm25_f)

    with open(metadata_file, "rb") as meta_f:
        metadata = pickle.load(meta_f)

    return bm25, metadata

# Perform BM25 Search
def bm25_search(query, bm25, metadata, top_n=5):
    """
    Perform a BM25 search on the pre-loaded index.

    Args:
        query (str): User query.
        bm25 (BM25Okapi): Pre-loaded BM25 index.
        metadata (pd.DataFrame): Metadata DataFrame.
        top_n (int): Number of top results to retrieve.

    Returns:
        pd.DataFrame: Search results with scores.
    """
    query_tokens = preprocess_text(query)
    print("Query tokens:", query_tokens)
    scores = bm25.get_scores(query_tokens)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_n]
    results = metadata.iloc[top_indices].copy()
    results["score"] = [scores[i] for i in top_indices]
    return results

# Enhanced BM25 Search
def enhanced_bm25_search(user_query, bm25, metadata, word_list, top_n=5):
    """
    Perform enhanced BM25 search with query normalization and preprocessing.

    Args:
        user_query (str): Raw user query.
        bm25 (BM25Okapi): Pre-loaded BM25 index.
        metadata (pd.DataFrame): Metadata DataFrame.
        word_list (list): List of valid domain-specific terms.
        top_n (int): Number of top results to retrieve.

    Returns:
        pd.DataFrame: Search results.
    """
    # Uncomment the next line to use query normalization if desired.
    # expanded_query = normalize_query(user_query, word_list, 85)
    expanded_query = user_query
    print("Original Query:", user_query)
    print("Normalized Query:", expanded_query)
    search_results = bm25_search(expanded_query, bm25, metadata, top_n)
    print("Search Results:")
    return search_results

# Load BM25 Index and Metadata
bm25, metadata = load_bm25_index(index_dir="./bm25_index")

def run_bm25_search(user_query, top_n=5):
    results = enhanced_bm25_search(user_query, bm25, metadata, word_list, top_n=top_n)
    return results

# # Example Usage
# user_query = "3BHK apartments in Paras Dews"
# #user_query = "3BHK apartments in whiteland urban resort"
# results = run_bm25_search(user_query, top_n=5)

# # Display Results with Scores using lowercase column names.
# for index, row in results.iterrows():
#     print(f"Score: {row['score']}")
#     print(f"Metadata: {row['metadata']}")
#     #print(f"Project Summary: {row['project_summary']}")
#     print("-" * 50)
