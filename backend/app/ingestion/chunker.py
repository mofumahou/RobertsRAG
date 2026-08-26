from __future__ import annotations

from dataclasses import replace
from typing import Any

from bs4 import BeautifulSoup as Soup, Tag
from langchain_text_splitters import RecursiveCharacterTextSplitter as Splitter
from numpy import block

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
    context_elements = [
        element for element in (
            context.part,
            context.article,
            context.section,
            context.subsection,
        ) if element
    ]
    text_path = " > ".join([*context_elements, f"from {CORPUS_NAME}"])
    return f"{text_path}\n\n{text}"

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

def build_chunks(splitter: Splitter,
                 context: Context,
                 block_text: str,
                 chapter_id: str,
                 chapter_name: str,
                 source: str,
                 chunk_index: int) -> list[Chunk]:
    block_text = block_text.strip()
    if not block_text:
        return []

    chunks:list[Chunk] = []

    for chunk_text in splitter.split_text(block_text):
        chunks.append(Chunk(
            chunk_id=f"{chapter_id}_{chunk_index}",
            text=chunk_text,
            embedding_text=build_embedding_text(context, chunk_text),
            metadata=build_metadata(
                context,
                chapter_id, 
                chapter_name, 
                chunk_index, 
                source),
            chapter_id = chapter_id,
            chapter_name = chapter_name,
            chunk_index = chunk_index))
        chunk_index += 1

    return chunks

def chunk_chapter(soup: Soup,
                  chapter_id: str,
                  chapter_name: str,
                  source: str
                  ) -> list[Chunk]:
    block_text = ""
    chunks:list[Chunk] = []
    context = Context()
    splitter = Splitter(chunk_size=CHUNK_SIZE, 
                        chunk_overlap=CHUNK_OVERLAP)

    for element in soup.find_all([*HEADING_LEVELS, "p"]):
        if element.name in HEADING_LEVELS:
            chunks.extend(build_chunks(
                splitter,
                context,
                block_text,
                chapter_id,
                chapter_name,
                source,
                len(chunks)))
            block_text = ""
            context = update_context(context, element)
            continue

        element_text = " ".join(element.get_text(separator=" ", strip=True).split())
        if element_text:
            block_text += f"\n\n{element_text}"

    chunks.extend(build_chunks(
        splitter,
        context,
        block_text,
        chapter_id,
        chapter_name,
        source,
        len(chunks)))
    
    return chunks

def chunk_chapters(chapters: list[ChapterDict],
                   source: str
                   ) -> list[Chunk]:
    chunks:list[Chunk] = []
    for chapter in chapters:
        chunks.extend(chunk_chapter(
            chapter.soup,
            chapter.chapter_id,
            chapter.chapter_name,
            source))
    return chunks
