import re
from pathlib import Path
from app.config import CURATED_DIR

TABLE_RE = re.compile(r"<<<(table \d+ h-\d+)>>>")

def insert_curated_tables(chapters: list[dict]) -> list[dict]:
    for chapter in chapters:
        soup = chapter["soup"]

        for placeholder in soup.find_all("p"):
            match = TABLE_RE.fullmatch(placeholder.get_text(strip=True))
            if match is None:
                continue
            filename = match.group(1).replace(" ", "_") + ".txt"
            table_path = CURATED_DIR / filename

            if not table_path.is_file():
                placeholder.decompose()
                continue

            table_text = table_path.read_text(encoding="utf-8")
            if not table_text.strip():
                raise ValueError(f"Curated table file {table_path} is empty")

            paragraph = soup.new_tag("p")
            paragraph.string = table_text
            placeholder.replace_with(paragraph)
    save_modified_chapters(chapters, CURATED_DIR / "debug_output")
    return chapters

def save_modified_chapters(chapters: list[dict],
                           output_dir: Path
                           ) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    for chapter in chapters:
        output_path = output_dir / f"{chapter['chapter_id']}.html"
        output_path.write_text(str(chapter["soup"]), encoding="utf-8")

    print(f"Saved {len(chapters)} chapters to {output_dir}")
