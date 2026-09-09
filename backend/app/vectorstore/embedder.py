from openai import OpenAI

from app.config import EMBEDDING_BATCH_SIZE, EMBEDDING_MODEL
from app.ingestion.models import Chunk, EmbeddedChunk

client = OpenAI()

def embed_chunks(chunks: list[Chunk]
                 ) -> list[EmbeddedChunk]:
    embedded_chunks: list[EmbeddedChunk] = []

    for start in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
        batch = chunks[start:start + EMBEDDING_BATCH_SIZE]
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=[chunk.embedding_text for chunk in batch])

        for chunk, data in zip(batch, response.data):
            embedded_chunks.append(EmbeddedChunk(
                chunk=chunk,
                embedding=data.embedding))

    return embedded_chunks