from dotenv import load_dotenv

from app.config import EMBEDDING_BATCH_SIZE, EPUB_DIR  # etc.
from app.ingestion.chunker import chunk_chapter
from app.vectorstore.chroma_client import store_chunks
from app.vectorstore.embedder import embed_chunks
from tools.epub_processor import clean_chapters, extract_html_chapters

load_dotenv()

