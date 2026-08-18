from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    text: str
    metadata: dict[str, Any]
    chapter_id: str
    chapter_name: str
    chunk_index: int

@dataclass(frozen=True)
class EmbeddedChunk:
    chunk: Chunk
    embedding: list[float]

@dataclass(frozen=True)
class Context:
    part: str=""
    chapter: str=""
    section: str=""
    subsection: str=""