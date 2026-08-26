from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
APP_NAME = "RobertsRAG"
CORPUS_NAME = "Robert's Rules of Order, 1915 Edition"

# <---- Paths ---->
CORPUS_DIR = BACKEND_DIR / "data" / "docs" / "processed"
EPUB_DIR = BACKEND_DIR / "data" / "docs" / "raw"

# <---- Vector Store ---->
CHROMA_DB_DIR = BACKEND_DIR / "data" / "chroma"
CHROMA_COLLECTION = "ronr"

# <---- Chunking ---->
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200

# <---- Embedding ---->
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_BATCH_SIZE = 100