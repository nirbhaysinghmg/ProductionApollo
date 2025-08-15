from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os
import re
import logging
import pickle

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Directory for the vector database
persist_directory = "./chroma_db"

# Ensure the vector database exists
if not os.path.exists(persist_directory):
    raise FileNotFoundError(f"Vector database not found at {persist_directory}. Please create it first.")

# Initialize the embedding model
# You can uncomment one of the following lines if needed:
# embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
# embeddings = HuggingFaceEmbeddings(model_name="multi-qa-mpnet-base-dot-v1")
# embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# Initialize the Chroma vector database
try:
    vector_db = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
    )
    logging.info(f"Vector database loaded successfully from '{persist_directory}'.")
except Exception as e:
    raise RuntimeError(f"Failed to initialize the Chroma vector database: {e}")

def preprocess_query(query):
    """
    Preprocess the query to handle terms like 'Sector 106' as single tokens.
    
    Args:
        query (str): The user query.
        
    Returns:
        str: Preprocessed query with merged terms.
    """
    # Merge "Sector <number>" patterns into single tokens (e.g. "Sector 106" -> "Sector_106")
    #query = re.sub(r"\b(Sector)\s(\d+)\b", r"\1_\2", query, flags=re.IGNORECASE)
    return query.strip()

def retrieve_from_vector_db(query, top_k=5, min_score_threshold=0.1):
    """
    Retrieve relevant documents from the vector database.
    
    Args:
        query (str): User query.
        top_k (int): Number of top results to retrieve.
        min_score_threshold (float): Minimum similarity score for relevant results.
        
    Returns:
        list: List of retrieved documents with metadata and scores.
    """
    try:
        # Preprocess the query
        preprocessed_query = preprocess_query(query)
        logging.info(f"Preprocessed Query: '{query}' -> '{preprocessed_query}'")
        
        # Perform similarity search with scores
        logging.info(f"Performing similarity search for query: '{preprocessed_query}' with top_k={top_k}")
        results = vector_db.similarity_search_with_score(preprocessed_query, k=top_k)
        
        # Filter results based on score threshold and create a list of dictionaries.
        filtered_results = [
            {"content": doc.page_content, "metadata": doc.metadata, "score": score}
            for doc, score in results if score > min_score_threshold
        ]
        
        if not filtered_results:
            logging.warning("No documents found matching the minimum score threshold.")
        
        return filtered_results

    except Exception as e:
        logging.error(f"Error during similarity search: {e}")
        return []

def enhanced_bm25_search(user_query, top_k=5):
    """
    Enhanced BM25 search that normalizes the query and retrieves results.
    
    Args:
        user_query (str): Raw user query.
        top_k (int): Number of top results to retrieve.
        
    Returns:
        list: List of search results.
    """
    # Here you can integrate query normalization if needed.
    expanded_query = user_query  # Or, for example: normalize_query(user_query, word_list, 85)
    logging.info(f"Original Query: '{user_query}'")
    logging.info(f"Normalized Query: '{expanded_query}'")
    return retrieve_from_vector_db(expanded_query, top_k=top_k)

# Example Usage
# if __name__ == "__main__":
#     user_query = "best investment opportunity on dwarka expressway"
#     top_k_results = 5
#     score_threshold = 0.1

#     logging.info(f"User Query: '{user_query}'")
#     results = retrieve_from_vector_db(user_query, top_k=top_k_results, min_score_threshold=score_threshold)

#     # Print results with lowercase field names.
#     if not results:
#         logging.info("No relevant documents found.")
#     else:
#         print("\n--- Retrieved Results ---")
#         for idx, result in enumerate(results, start=1):
#             print(f"Result {idx}:")
#             print(f"Score: {result['score']:.4f}")
#             # Here 'content' holds the project summary (as stored during indexing)
#             #print(f"Project Summary: {result['content']}")
#             print(f"Metadata: {result['metadata']}")
#             print("-" * 50)
