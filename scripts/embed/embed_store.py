# embed/embed_store.py

import json
import uuid
import logging
from scripts.embed.embedding_model import model, collection

import os
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(
    filename="embed_store.log",
    level=logging.INFO,  # Change to DEBUG for more details
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.info("Script started: embed_store.py")

# Load JSON Data
file_path = os.getenv("FILE1")
try:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    logging.info(f"Successfully loaded JSON file: {file_path}")
except Exception as e:
    logging.error(f"Failed to load JSON file: {e}")
    raise

# Define fields of interest
FIELDS_OF_INTEREST = [
    "http://www.aihub.or.kr/kb/law/caseNumber",
    "http://www.aihub.or.kr/kb/law/caseName",
    "http://www.aihub.or.kr/kb/law/caseType",
    "http://www.aihub.or.kr/kb/law/courtName",
    "http://www.aihub.or.kr/kb/law/sentenceDate",
    "http://www.aihub.or.kr/kb/law/judgementAbstract",
    "http://www.aihub.or.kr/kb/law/precedentText",
    "http://www.aihub.or.kr/kb/law/judgementNote",
]

logging.info(f"Fields of interest: {FIELDS_OF_INTEREST}")

text_chunks = []
metadata_list = []

# Extract and process JSON data
for uri, properties in data.items():
    combined_text = []
    meta = {"uri": uri}  # Store URI for reference

    for field in FIELDS_OF_INTEREST:
        if field in properties:
            field_values = properties[field]
            extracted_values = [fv["value"] for fv in field_values if "value" in fv]
            field_text = " ".join(extracted_values)

            combined_text.append(field_text)

            if field == "http://www.aihub.or.kr/kb/law/caseNumber":
                meta["caseNumber"] = extracted_values[0] if extracted_values else ""

    if combined_text:
        text_chunk = "\n".join(combined_text)
        text_chunks.append(text_chunk)
        metadata_list.append(meta)

logging.info(f"Extracted {len(text_chunks)} text chunks.")

# Function to chunk large text
def chunk_text(text, chunk_size=1000):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end
    return chunks

# Chunking process
final_chunks = []
final_metadata = []

for t, m in zip(text_chunks, metadata_list):
    if len(t) > 1000:
        splitted = chunk_text(t, chunk_size=1000)
        for i, sub_t in enumerate(splitted):
            new_meta = dict(m)
            new_meta["chunk_index"] = i
            final_chunks.append(sub_t)
            final_metadata.append(new_meta)
    else:
        final_chunks.append(t)
        final_metadata.append(m)

logging.info(f"Total chunks after splitting: {len(final_chunks)}")

# Generate embeddings
try:
    embeddings = model.encode(final_chunks)
    logging.info("Successfully generated embeddings.")
except Exception as e:
    logging.error(f"Failed to generate embeddings: {e}")
    raise

# Generate unique IDs
ids = [str(uuid.uuid4()) for _ in range(len(final_chunks))]

# Define the maximum batch size allowed
MAX_BATCH_SIZE = 41666

# Insert into ChromaDB
try:
    for i in range(0, len(final_chunks), MAX_BATCH_SIZE):
        batch_documents = final_chunks[i : i + MAX_BATCH_SIZE]
        batch_embeddings = embeddings[i : i + MAX_BATCH_SIZE]
        batch_metadatas = final_metadata[i : i + MAX_BATCH_SIZE]
        batch_ids = ids[i : i + MAX_BATCH_SIZE]

        collection.add(
            documents=batch_documents,
            embeddings=batch_embeddings,
            metadatas=batch_metadatas,
            ids=batch_ids
        )
        logging.info(f"Inserted batch {i // MAX_BATCH_SIZE + 1}: {len(batch_documents)} text chunks into ChromaDB.")

    logging.info(f"Successfully inserted all text chunks into ChromaDB.")

except Exception as e:
    logging.error(f"Failed to insert data into ChromaDB: {e}")
    raise

logging.info("Script completed successfully.")
