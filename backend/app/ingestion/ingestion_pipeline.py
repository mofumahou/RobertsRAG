import os
from dotenv import load_dotenv
from openai import OpenAI

from app.config import EPUB_DIR  # etc.
from app.ingestion.chunker import chunk_chapters
from app.vectorstore.chroma_client import store_chunks
from app.vectorstore.embedder import embed_chunks
from tools.epub_processor import clean_chapters, extract_html_chapters
from tools.insert_curated_tables import insert_curated_tables

load_dotenv()

def main() -> None:
    # Load the first EPUB file found in the EPUB_DIR
    epub_path = next(EPUB_DIR.glob("*.epub"), None)
    if epub_path is None:
        raise FileNotFoundError(f"No EPUB files found in {EPUB_DIR}")

    # Extract html from epub, format it into a simple pre-ingestion structure, and insert curated tables (replacing placeholders with actual data)    
    chapters = insert_curated_tables(clean_chapters(extract_html_chapters(epub_path)))
    print(f"Processed {len(chapters)} chapters from {epub_path.name}\n")

    # Chunk the chapters with a size of 1500 characters and an overlap of 200 characters
    chunks = chunk_chapters(chapters, epub_path.name)
    print(f"Created {len(chunks)} chunks from {len(chapters)} chapters\n")

    # Embed the chunks passing the OpenAI client and store them in the Chroma vector store
    client = OpenAI(api_key=os.getenv("NANOGPT_API_KEY"),
                     base_url=os.getenv("NANOGPT_BASE_URL"))

    embedded_chunks = embed_chunks(chunks, client)
    print(f"Processed {len(chunks)} chunks into {len(embedded_chunks)} embedded chunks\n")
    
    store_chunks(embedded_chunks)

    return

if __name__ == "__main__":
    main()