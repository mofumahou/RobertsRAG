from dotenv import load_dotenv

from app.config import EPUB_DIR
from app.ingestion.chunker import chunk_chapter
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

        # Show the LAST chunk of each chapter — this is the block emitted by
        # the post-loop flush, i.e. the section with no trailing heading.
        if chunks:
            first = chunks[0]
            print(f"    first chunk id={first.chunk_id} "
                  f"    source: {first.metadata["source"]!r}\n"
                  f"    part: {first.metadata["part"]!r}\n"
                  f"    article: {first.metadata["article"]!r}\n"
                  f"    section: {first.metadata["section"]!r}\n"
                  f"    subsection: {first.metadata["subsection"]!r}\n"
                  f"    chapter_id: {first.metadata["chapter_id"]!r}\n"
                  f"    chapter_name: {first.metadata["chapter_name"]!r}\n"
                  f"    chunk_index: {first.metadata["chunk_index"]!r}")
            print(f"    text: {first.text}")

            last = chunks[-1]
            print(f"    last chunk id={last.chunk_id} "
                  f"metadata: {last.metadata!r}")
            print(f"    text: {last.text}\n")

if __name__ == "__main__":
    main()