import chromadb

from app.config import (
    CHROMA_COLLECTION,
    CHROMA_DB_DIR,
    EMBEDDING_BATCH_SIZE,
)
from app.ingestion.models import EmbeddedChunk

# Initialize a persistent ChromaDB client
client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))

# Create a collection, and upsert the embedded chunks into the collection
def store_chunks(embedded_chunks: list[EmbeddedChunk]
                 ) -> None:
    try:
        client.delete_collection(name=CHROMA_COLLECTION)
    except ValueError:
        pass

    collection = client.create_collection(
        name=CHROMA_COLLECTION,
        configuration={"hnsw": {"space": "cosine"}})

    for start in range(0, len(embedded_chunks), EMBEDDING_BATCH_SIZE):
        batch = embedded_chunks[start:start + EMBEDDING_BATCH_SIZE]
        collection.upsert(
            ids=[ec.chunk.chunk_id for ec in batch],
            documents=[ec.chunk.text for ec in batch],
            embeddings=[ec.embedding for ec in batch],
            metadatas=[ec.chunk.metadata for ec in batch])

    # Sanity check, will be moved to testing section later 
    collection = client.get_collection(CHROMA_COLLECTION)
    print(f"{collection.count()} chunks in collection")
    print(collection.configuration)
    sample = collection.get(limit=1, include=["embeddings", "metadatas"])
    print(len(sample["embeddings"][0]), sample["metadatas"][0])