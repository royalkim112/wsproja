# embedding_model.py

import chromadb
from sentence_transformers import SentenceTransformer

# 1) Connect to Chroma (running in Docker on localhost:9000)
chroma_client = chromadb.HttpClient(host="localhost", port=8000)

# 2) Create or get a collection
collection_name = "legal_docs"
collection = chroma_client.get_or_create_collection(name=collection_name)

# 3) Choose an embedding model
model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
