import os
import re
import logging
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Directory for the vector database
persist_directory = "./chroma_db2"  # Use your updated DB path

# Ensure the vector database exists
if not os.path.exists(persist_directory):
    raise FileNotFoundError(f"Vector database not found at {persist_directory}. Please create it first.")

# Initialize the embedding model
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# Initialize the Chroma vector database
try:
    vector_db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    logging.info(f"✅ Vector database loaded successfully from '{persist_directory}'.")
except Exception as e:
    raise RuntimeError(f"❌ Failed to initialize the Chroma vector database: {e}")

def preprocess_query(query: str) -> str:
    """
    Preprocess the query to normalize text and handle terms like 'Sector 106' as single tokens.

    Args:
        query (str): The user query.
    Returns:
        str: Preprocessed query with merged terms.
    """
    query = query.strip()
    # Merge "Sector <number>" into "Sector_106" for better matching
    query = re.sub(r"\b(Sector)\s(\d+)\b", r"\1_\2", query, flags=re.IGNORECASE)
    return query

def retrieve_from_vector_db(query: str, top_k: int = 5, min_score_threshold: float = 0.1):
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
        logging.info(f"🔎 Searching for: '{preprocessed_query}' (Top {top_k} results)")

        # Perform similarity search with scores
        results = vector_db.similarity_search_with_score(preprocessed_query, k=top_k)

        # Filter results based on score threshold
        filtered_results = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score
            }
            for doc, score in results if score > min_score_threshold
        ]

        if not filtered_results:
            logging.warning("⚠️ No documents found matching the minimum score threshold.")

        return filtered_results

    except Exception as e:
        logging.error(f"❌ Error during similarity search: {e}")
        return []

def hybrid_search(user_query: str, top_k: int = 5):
    """
    Hybrid search combining query normalization and vector search.

    Args:
        user_query (str): Raw user query.
        top_k (int): Number of top results to retrieve.

    Returns:
        list: List of retrieved results.
    """
    logging.info(f"🔹 User Query: '{user_query}'")
    return retrieve_from_vector_db(user_query, top_k=top_k)

# Example Usage
# if __name__ == "__main__":
#     user_query = "best investment opportunity on dwarka expressway"
#     top_k_results = 5
#     score_threshold = 0.1

#     logging.info(f"�� Query: '{user_query}' | Retrieving top {top_k_results} results...")
#     results = retrieve_from_vector_db(user_query, top_k=top_k_results, min_score_threshold=score_threshold)

#     # Display results
#     if not results:
#         logging.info("❌ No relevant documents found.")
#     else:
#         print("\n--- 📌 Retrieved Results ---")
#         for idx, result in enumerate(results, start=1):
#             print(f"🔹 Result {idx}:")
#             print(f"�� Score: {result['score']:.4f}")
#             print(f"📄 Content: {result['content'][:200]}...")  # Print first 200 characters
#             print(f"📝 Metadata: {result['metadata']}")
#             print("-" * 80)

