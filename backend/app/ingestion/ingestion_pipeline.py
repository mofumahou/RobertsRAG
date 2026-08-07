import chromadb
from langchain_core import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from pathlib import Path
from tools.epub_processor import extract_html_chapters

load_dotenv()

def main():
    print("Starting ingestion pipeline...")
    #load documents
    #chunk
    #embed
    #store

if __name__ == "__main__":
    main()