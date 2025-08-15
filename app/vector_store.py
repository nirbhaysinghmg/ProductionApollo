import os
import uuid
import pandas as pd
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from .config import settings

embeddings = GoogleGenerativeAIEmbeddings(
    model=settings.EMBED_MODEL, 
    google_api_key=settings.GEMINI_API_KEY
)

def get_vector_store():
    if os.path.exists(settings.PERSIST_DIRECTORY):
        print("Loading existing vector store...")
        return Chroma(
            persist_directory=settings.PERSIST_DIRECTORY,
            embedding_function=embeddings
        )
    
    print("Creating new vector store...")
    df = pd.read_csv(settings.CSV_PATH)

    # Create one Document per CSV row (row-wise chunking)
    documents = []
    for idx, row in df.iterrows():
        content = "\n".join([f"{k}: {v}" for k, v in row.to_dict().items()])
        documents.append(Document(page_content=content, metadata={"row_index": int(idx)}))
    
    print(f"Created {len(documents)} row documents (1 per CSV row)")
    ids = [str(uuid.uuid4()) for _ in documents]
    
    return Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=settings.PERSIST_DIRECTORY,
        ids=ids
    )