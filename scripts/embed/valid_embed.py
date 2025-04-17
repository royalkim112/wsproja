# embed/valid_embed.py

import chromadb

# Connect to Chroma running in Docker
chroma_client = chromadb.HttpClient(host="localhost", port=9000)

# Get the collection
collection_name = "legal_docs"
collection = chroma_client.get_collection(name=collection_name)

# Count the number of stored embeddings
count = collection.count()
print(f"Total documents in ChromaDB: {count}")
