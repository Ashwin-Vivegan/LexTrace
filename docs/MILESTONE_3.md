# Milestone 3: Semantic Search

## Overview
This milestone implements real semantic retrieval for LexTrace by augmenting the existing SQLite-backed chunking with local embeddings and a FAISS vector index. 

It provides "Semantic Search" capability without using LLM answer generation (RAG will come in a later milestone).

## Why Embeddings & Semantic Search?
Semantic search allows retrieving legal document chunks based on the *meaning* of the query rather than exact keyword matches. This is critical for legal intelligence, where concepts like "termination notice" might be phrased as "notice of cancellation" or "prior to ending the agreement."

## Architecture

1. **Local Embeddings (Sentence Transformers)**
   We use `sentence-transformers/all-MiniLM-L6-v2`. It provides a fast, lightweight, and effective 384-dimensional dense vector representation of text. 
   Running it locally ensures no API keys are required and avoids external dependencies like Gemini or Groq at this stage.

2. **Vector Store (FAISS)**
   We use `faiss-cpu` with an `IndexFlatIP` (Inner Product) index. Since we L2-normalize all vectors before insertion, the inner product is mathematically equivalent to Cosine Similarity.
   The FAISS index maps 0-indexed integer IDs to actual SQLite `chunk_id`s through a persistent JSON mapping (`chunk_mapping.json`).

3. **Persistence Strategy**
   The source of truth for all documents, versions, and chunks remains **SQLite**.
   FAISS serves strictly as an in-memory search accelerator that is periodically saved to disk (in `data/vector_store/`).
   If the index is lost or corrupted, it can be completely rebuilt from SQLite using the `/api/search/rebuild-index` endpoint.

## Future Migration
The current `VectorStore` abstraction makes it trivial to swap FAISS for a PostgreSQL + `pgvector` implementation in the future, as the application logic strictly depends on `add_vectors()` and `search()` interfaces.

## Note on Legacy RAG
The `rag_engine.py` component operating on in-memory data (TF-IDF keyword matching) has been preserved as legacy. The new semantic search pipeline is entirely distinct and operates on actual database records.
