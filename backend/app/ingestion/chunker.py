from __future__ import annotations

from dataclasses import replace
from typing import Any

from bs4 import BeautifulSoup as Soup, Tag
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import CHUNK_OVERLAP, CHUNK_SIZE, CORPUS_NAME
from app.ingestion.models import ChapterDict, Chunk, Context

HEADING_LEVELS = {
    "h2": "part",
    "h3": "article",
    "h4": "section",
    "h5": "subsection",
}

def update_context(context: Context,
                   heading: Tag
                   ) -> Context:
    heading_level = heading.name
    heading_text = " ".join(heading.get_text(strip=True).split())

    if not heading_level or not heading_text:
        return context

    match heading_level:
        case "h2":
            return replace(
                context, 
                part=heading_text, 
                article="", 
                section="", 
                subsection="")
        case "h3":
            return replace(
                context, 
                article=heading_text, 
                section="", 
                subsection="")
        case "h4":
            return replace(
                context, 
                section=heading_text, 
                subsection="")
        case "h5":
            return replace(
                context, 
                subsection=heading_text)
        case _:
            return context

def build_embedding_text(context: Context,
                         text: str
                         ) -> str:
    return

def build_metadata(context: Context, 
                   chapter_id: str, 
                   chapter_name: str, 
                   chunk_index: int, 
                   source: str
                   ) -> dict[str, Any]:
    return {
        "source": source,
        "part": context.part,
        "article": context.article,
        "section": context.section,
        "subsection": context.subsection,
        "chapter_id": chapter_id,
        "chapter_name": chapter_name,
        "chunk_index": chunk_index,
    }

def chunk_chapter(soup: Soup,
                  chapter_id: str,
                  chapter_name: str,
                  source: str
                  ) -> list[Chunk]:
    return

def chunk_chapters(chapters: list[ChapterDict],
                   source: str
                   ) -> list[Chunk]:
    return
