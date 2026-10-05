import os
from dotenv import load_dotenv
from openai import OpenAI

from app.config import CORPUS_NAME, EMBEDDING_BATCH_SIZE, EPUB_DIR  # etc.
from app.ingestion.chunker import chunk_chapters
from app.vectorstore.chroma_client import store_chunks
from app.vectorstore.embedder import embed_chunks
from tools.epub_processor import clean_chapters, extract_html_chapters

load_dotenv()

def main() -> None:
    # Temporary pipeline for processing the EPUB, chunking, embedding, and storing in Chroma
    # Runs fine so far, pending furter documentation
    epub_path = next(EPUB_DIR.glob("*.epub"), None)
    if epub_path is None:
        raise FileNotFoundError(f"No EPUB files found in {EPUB_DIR}")
    
    chapters = clean_chapters(extract_html_chapters(epub_path))
    print(f"Processed {len(chapters)} chapters from {epub_path.name}\n")

    chunks = chunk_chapters(chapters, epub_path.name)
    print(f"Created {len(chunks)} chunks from {len(chapters)} chapters\n")

    client = OpenAI(api_key=os.getenv("NANOGPT_API_KEY"),
                     base_url=os.getenv("NANOGPT_BASE_URL"))
    
    embedded_chunks = embed_chunks(chunks, client)
    print(f"Processed {len(chunks)} chunks into {len(embedded_chunks)} embedded chunks\n")
    
    store_chunks(embedded_chunks)

    return

if __name__ == "__main__":
    main()