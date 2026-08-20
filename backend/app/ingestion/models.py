from dataclasses import dataclass
from bs4 import BeautifulSoup as Soup
from typing import Any

@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    text: str
    embedding_text: str
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
    article: str=""
    section: str=""
    subsection: str=""

@dataclass(frozen=True)
class ChapterDict:
    chapter_id: str
    chapter_name: str
    soup: Soup