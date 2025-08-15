import os
import pickle
import glob
import pandas as pd
from rank_bm25 import BM25Okapi
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk

# Download NLTK dependencies if not already available
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Initialize the WordNet lemmatizer and English stopwords set
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

def preprocess_text(text):
    """
    Preprocess the input text by tokenizing, lemmatizing, and handling domain-specific patterns.
    
    Steps:
      - Convert text to lowercase and tokenize it.
      - Combine tokens like "sector 42" into a single token.
      - Combine numerical ranges like "1 to 2 cr" into one token.
      - If a token matches a domain-specific term (case-insensitive), preserve it in uppercase.
      - Otherwise, lemmatize tokens that are not stopwords.
    
    Args:
        text (str): The input text.
    
    Returns:
        list: A list of processed tokens.
    """
    tokens = word_tokenize(str(text).lower())
    processed_tokens = []
    i = 0

    while i < len(tokens):
        # Combine "sector <number>" into a single token.
        if tokens[i] == "sector" and i + 1 < len(tokens) and tokens[i + 1].isdigit():
            processed_tokens.append(f"{tokens[i]} {tokens[i + 1]}")
            i += 2
            continue

        # Combine patterns like "1 to 2 cr" into one token.
        if (i + 3 < len(tokens) and tokens[i].isdigit() and tokens[i + 1] == "to" and
            tokens[i + 2].isdigit() and tokens[i + 3] in {"cr", "lakh"}):
            processed_tokens.append(f"{tokens[i]} to {tokens[i + 2]} {tokens[i + 3]}")
            i += 4
            continue

        # Preserve domain-specific terms (case-insensitive)
        if tokens[i] in domain_terms or tokens[i].lower() in domain_terms:
            processed_tokens.append(tokens[i].lower())
        elif tokens[i] not in stop_words:
            processed_tokens.append(lemmatizer.lemmatize(tokens[i]))
        i += 1

    return processed_tokens

# ----------------------
# Load and Concatenate Multiple CSV Files
# ----------------------
csv_dir = "./data/"            # Directory containing CSV files
csv_pattern = os.path.join(csv_dir, "all*21Apr25*.csv")  # Pattern to match all CSV files in the directory
csv_files = glob.glob(csv_pattern)

if not csv_files:
    raise ValueError(f"No CSV files found in {csv_dir}")

# Read each CSV file and ensure required columns are present.
df_list = []
for file in csv_files:
    temp_df = pd.read_csv(file)
    # Check for required columns: "project_summary" and "metadata"
    if "project_summary" not in temp_df.columns or "metadata" not in temp_df.columns:
        raise ValueError(f"CSV file {file} must contain 'project_summary' and 'metadata' columns.")
    df_list.append(temp_df)

# Concatenate all CSV data into one DataFrame.
df = pd.concat(df_list, ignore_index=True)
print(f"Loaded {len(csv_files)} CSV files with a total of {len(df)} records.")

# ----------------------
# Preprocess Text and Build BM25 Index
# ----------------------
# Apply preprocessing to the 'project_summary' column.
df["tokens"] = df["project_summary"].apply(preprocess_text)

# Build corpus and BM25 index.
corpus = df["tokens"].tolist()
bm25 = BM25Okapi(corpus)
print("BM25 index built successfully.")

# ----------------------
# Save BM25 Index and Metadata
# ----------------------
output_dir = "./bm25_index"
metadata_file = os.path.join(output_dir, "metadata.pkl")
bm25_file = os.path.join(output_dir, "bm25.pkl")

def clean_output_directory(output_dir):
    """
    Clean the output directory by deleting all files inside it.
    If the directory doesn't exist, it is created.
    
    Args:
        output_dir (str): The directory to clean.
    """
    if os.path.exists(output_dir):
        print(f"Cleaning up the output directory: {output_dir}")
        try:
            for file in os.listdir(output_dir):
                file_path = os.path.join(output_dir, file)
                os.remove(file_path)
                print(f"Deleted: {file_path}")
        except Exception as e:
            print(f"Error cleaning directory {output_dir}: {e}")
    else:
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created directory: {output_dir}")

# Clean the output directory before saving new indexes.
clean_output_directory(output_dir)

# Save BM25 index and metadata using pickle.
try:
    with open(metadata_file, "wb") as meta_f:
        # Save the relevant text and metadata columns.
        pickle.dump(df[["project_summary", "metadata"]], meta_f)
        print(f"Metadata stored at {metadata_file}")

    with open(bm25_file, "wb") as bm25_f:
        pickle.dump(bm25, bm25_f)
        print(f"BM25 Index stored at {bm25_file}")

except Exception as e:
    print(f"Error saving BM25 index or metadata: {e}")
