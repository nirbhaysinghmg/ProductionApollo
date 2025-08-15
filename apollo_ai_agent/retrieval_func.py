import pandas as pd
from bm25_retrieval import run_bm25_search  # BM25 search function
from retrieve_vdb_apollo import retrieve_from_vector_db  # Chroma vector DB retrieval function
from retrieve_mysql import execute_query  # MySQL retrieval function

def rank_results(bm25_results, vdb_results, mysql_results, bm25_weight=0.5, vdb_weight=0.3, mysql_weight=0.2):
    """
    Merge and rank results from BM25, Vector DB, and MySQL.

    Args:
        bm25_results (pd.DataFrame): BM25 results DataFrame with 'score' and 'project_summary'.
        vdb_results (list): Vector DB results list with 'score' and 'content'.
        mysql_results (list): MySQL results list of dictionaries.
        bm25_weight (float): Weight for BM25 scores.
        vdb_weight (float): Weight for Vector DB scores.
        mysql_weight (float): Weight for MySQL scores.

    Returns:
        list: Ranked and merged results.
    """
    combined_results = []

    # # Ensure BM25 results are always a DataFrame
    # if not isinstance(bm25_results, pd.DataFrame):
    #     bm25_results = pd.DataFrame(columns=["score", "project_summary"])

    # # Normalize BM25 scores
    # if not bm25_results.empty:
    #     bm25_results = bm25_results[bm25_results["score"] > 1.0].copy()
    #     bm25_max_score = bm25_results["score"].max()
    #     bm25_results["normalized_score"] = bm25_results["score"] / bm25_max_score if bm25_max_score > 0 else 0
    # else:
    #     bm25_results["normalized_score"] = 0.0

    # Normalize Vector DB scores
    vdb_max_score = max((res["score"] for res in vdb_results), default=1.0)
    for res in vdb_results:
        res["normalized_score"] = res["score"] / vdb_max_score if vdb_max_score > 0 else 0

    # Normalize MySQL results (Assume no score, so assign fixed score)
    mysql_score = 1.0  # Assign a fixed score
    for res in mysql_results:
        res["normalized_score"] = mysql_score  # Keep fixed score for MySQL entries

    # # Merge results
    # for _, row in bm25_results.iterrows():
    #     combined_results.append({
    #         "content": row["project_summary"],
    #         "score": row["normalized_score"] * bm25_weight,
    #     })
    for res in vdb_results:
        combined_results.append({
            "content": res["content"],
            "score": res["normalized_score"] * vdb_weight,
        })
    # for res in mysql_results:
    #     combined_results.append({
    #         "content": res["project_summary"],  # Assuming MySQL returns 'project_summary'
    #         "score": res["normalized_score"] * mysql_weight,
    #     })

    # # Sort combined results by score in descending order
    # combined_results.sort(key=lambda x: x["score"], reverse=True)

    return combined_results

def retrieve_and_rank(user_query, sql_query, category, bm25_top_n=5, vdb_top_k=5, bm25_weight=0.5, vdb_weight=0.3, mysql_weight=0.2):
    """
    Perform retrieval from BM25, Vector DB, and MySQL, merge results, and rank them.

    Args:
        user_query (str): User query.
        sql_query (str): SQL query to retrieve from MySQL.
        category (str): Use to control the search flow.
        bm25_top_n (int): Number of top BM25 results to retrieve.
        vdb_top_k (int): Number of top Vector DB results to retrieve.
        bm25_weight (float): Weight for BM25 scores.
        vdb_weight (float): Weight for Vector DB scores.
        mysql_weight (float): Weight for MySQL scores.

    Returns:
        str: Merged and ranked context as a single string.
    """
    try:
        # # Retrieve results from BM25
        # bm25_results = pd.DataFrame(columns=["score", "project_summary"])  # Initialize as empty DataFrame
        # if category not in ('city_level_query', 'micro-market_level_query'):
        #     print("BM25 Execution starts:")
        #     bm25_results = run_bm25_search(user_query=user_query, top_n=bm25_top_n)

        #     # Ensure bm25_results is always a DataFrame
        #     if not isinstance(bm25_results, pd.DataFrame):
        #         bm25_results = pd.DataFrame(columns=["score", "project_summary"])

        #     if not bm25_results.empty:
        #         bm25_results = bm25_results[bm25_results["score"] > 1.0].copy()
        #         print("\n--- BM25 Results ---")
        #         print(bm25_results)

        # Retrieve results from Vector DB
        print("Chroma DB Execution starts:")
        vdb_results = retrieve_from_vector_db(user_query, top_k=vdb_top_k, min_score_threshold=0.1)
        print("\n--- Vector DB Results ---")
        for idx, result in enumerate(vdb_results, start=1):
            print(f"Result {idx}: Score: {result['score']:.4f}, Content: {result['content'][:100]}")
            print("-" * 50)

        # # Retrieve results from MySQL
        # print("MySQL Execution starts:")
        # mysql_results = execute_query(sql_query) or []

        bm25_results = []
        mysql_results = []
        # Merge and rank results
        ranked_results = rank_results(bm25_results, vdb_results, mysql_results, bm25_weight, vdb_weight, mysql_weight)

        # Create context from ranked results
        merged_context = "\n\n".join([res["content"] for res in ranked_results])
        if not merged_context:
            merged_context = "No highly relevant documents were found."

    except Exception as e:
        print(f"Error during retrieval or ranking: {e}")
        merged_context = "No documents were retrieved due to an error."
    return merged_context
