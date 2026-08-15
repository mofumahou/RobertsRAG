from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from bs4 import BeautifulSoup, NavigableString, Tag
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import CHUNK_OVERLAP, CHUNK_SIZE, CORPUS_NAME

HEADING_LEVELS = {
    "h2": "Part",
    "h3": "Chapter",
    "h4": "Section",
    "h5": "Subsection",
}

@dataclass(frozen=True)
class Context:
    part: str=""
    chapter: str=""
    section: str=""
    subsection: str=""

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

def build_metadata(context: Context, 
                   chapter_id: str, 
                   chapter_name: str, 
                   chunk_index: int, 
                   source: str) -> dict[str, Any]:
    return {
        "source": source,
        "part": context.part,
        "chapter": context.chapter,
        "section": context.section,
        "subsection": context.subsection,
        "chapter_id": chapter_id,
        "chapter_name": chapter_name,
        "chunk_index": chunk_index,
    }