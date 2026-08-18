from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from bs4 import BeautifulSoup, NavigableString, Tag
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import CHUNK_OVERLAP, CHUNK_SIZE, CORPUS_NAME
from backend.app.ingestion.models import Chunk, Context

HEADING_LEVELS = {
    "h2": "part",
    "h3": "chapter",
    "h4": "section",
    "h5": "subsection",
}

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