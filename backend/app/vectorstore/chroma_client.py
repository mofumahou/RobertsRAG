import chromadb

from app.config import (
    CHROMA_COLLECTION,
    CHROMA_DB_DIR,
    EMBEDDING_BATCH_SIZE,
)
from app.ingestion.models import EmbeddedChunk

client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))

def store_chunks(embedded_chunks: list[EmbeddedChunk]
                 ) -> None:
    collection = client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        configuration={"hnsw": {"space": "cosine"}})

    for start in range(0, len(embedded_chunks), EMBEDDING_BATCH_SIZE):
        batch = embedded_chunks[start:start + EMBEDDING_BATCH_SIZE]
        collection.upsert(
            ids=[ec.chunk.chunk_id for ec in batch],
            documents=[ec.chunk.text for ec in batch],
            embeddings=[ec.embedding for ec in batch],
            metadatas=[ec.chunk.metadata for ec in batch])