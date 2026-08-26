from dotenv import load_dotenv

from app.config import EMBEDDING_BATCH_SIZE, EPUB_DIR  # etc.
from app.ingestion.chunker import chunk_chapter
#from app.vectorstore.chroma_client import store_chunks
#from app.vectorstore.embedder import embed_chunks
from tools.epub_processor import clean_chapters, extract_html_chapters

load_dotenv()

def main() -> None:
    epub_path = next(EPUB_DIR.glob("*.epub"), None)
    if epub_path is None:
        raise FileNotFoundError(f"No EPUB files found in {EPUB_DIR}")

    chapters = clean_chapters(extract_html_chapters(epub_path))
    print(f"Processed {len(chapters)} chapters from {epub_path.name}\n")

    for chapter in chapters:
        chunks = chunk_chapter(
            chapter["soup"],
            chapter["chapter_id"],
            chapter["chapter_name"],
            epub_path.name)

        print(f"[{chapter['chapter_id']}] {chapter['chapter_name']}: "
              f"{len(chunks)} chunks")

        # Sanity checks: unique ids and contiguous indices from 0
        ids = [c.chunk_id for c in chunks]
        assert len(ids) == len(set(ids)), f"duplicate chunk_id in {chapter['chapter_id']}"
        assert [c.chunk_index for c in chunks] == list(range(len(chunks))), \
            f"non-contiguous chunk_index in {chapter['chapter_id']}"

        # Show the LAST chunk of each chapter — this is the block emitted by
        # the post-loop flush, i.e. the section with no trailing heading.
        if chunks:
            first = chunks[0]
            print(f"    first chunk id={first.chunk_id} "
                    f"article={first.metadata['article']!r}")
            print(f"    text: {first.text[:160]!r}")

            last = chunks[-1]
            print(f"    last chunk id={last.chunk_id} "
                  f"article={last.metadata['article']!r}")
            print(f"    text: {last.text[:160]!r}\n")

if __name__ == "__main__":
    main()