import chromadb
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


def main():
    print("Starting ingestion pipeline...")

if __name__ == "__main__":
    main()