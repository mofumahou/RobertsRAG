# RobertsRAG

A work-in-progress Retrieval-Augmented Generation (RAG) system for the
public-domain 1915 edition of Robert's Rules of Order.

The project processes an EPUB into structured text chunks, preserving
Part, Article, Section, and Subsection metadata. These chunks are embedded
and stored in Chroma for semantic search.

The goal is to answer parliamentary procedure questions using relevant
passages from the book, with clear source references.

## Status

Currently refining the ingestion pipeline and its tests before building
the retrieval and question-answering pipeline.
