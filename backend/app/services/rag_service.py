import time
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.hybrid_search import HybridSearchService
from app.services.llm_provider import LLMProvider, GroqLLMProvider
from app.schemas.search import SearchMode

logger = logging.getLogger(__name__)

INSUFFICIENT_EVIDENCE_TEXT = "Insufficient evidence in the retrieved documents."

class RAGService:
    """
    RAG Orchestrator Service.
    Retrieves evidence chunks via Hybrid Search, constructs grounded prompt,
    generates answer via Groq LLM, and builds database-backed source citations.
    """
    def __init__(self, hybrid_search_service: HybridSearchService, llm_provider: Optional[LLMProvider] = None):
        self.hybrid_search_service = hybrid_search_service
        self.llm_provider = llm_provider or GroqLLMProvider()

    def build_system_prompt(self) -> str:
        return (
            "You are LexTrace AI, an evidence-grounded legal document research assistant.\n\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. Answer the user's question using ONLY the retrieved legal document evidence provided below.\n"
            "2. Do NOT use outside knowledge, external assumptions, or unsupported facts.\n"
            "3. Do NOT invent legal clauses, document names, section names, page numbers, or citations.\n"
            "4. Clearly distinguish explicit evidence from inference.\n"
            "5. If the retrieved evidence does not contain sufficient facts to answer the question directly, your response MUST be exactly:\n"
            f'"{INSUFFICIENT_EVIDENCE_TEXT}"\n'
            "6. Keep your response formal, concise, and structured."
        )

    def build_context_prompt(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        context_blocks = []
        for idx, chunk in enumerate(chunks, 1):
            doc_name = chunk.get("document_name", "Unknown Document")
            ver_num = chunk.get("version_number", "1.0")
            sec_name = chunk.get("section_name") or "General Section"
            pg_num = chunk.get("page_number") if chunk.get("page_number") is not None else "N/A"
            cid = chunk.get("chunk_id", "Unknown")
            content = chunk.get("content", "").strip()

            block = (
                f"SOURCE {idx}\n"
                f"Document: {doc_name}\n"
                f"Version: {ver_num}\n"
                f"Section: {sec_name}\n"
                f"Page: {pg_num}\n"
                f"Chunk ID: {cid}\n\n"
                f"{content}"
            )
            context_blocks.append(block)

        formatted_context = "\n\n----------------------------------------\n\n".join(context_blocks)

        prompt = (
            f"RETRIEVED LEGAL EVIDENCE:\n\n"
            f"{formatted_context}\n\n"
            f"----------------------------------------\n\n"
            f"USER QUESTION: {query}\n\n"
            f"GROUNDED ANSWER:"
        )
        return prompt

    def ask(self, db: Session, query: str, top_k: int = 5, min_score_threshold: float = 0.01) -> Dict[str, Any]:
        start_time = time.time()

        if not query or not query.strip():
            raise ValueError("Query string cannot be empty or whitespace-only.")

        clean_query = query.strip()
        logger.info(f"RAG Service processing question: '{clean_query}'")

        # 1. Retrieve evidence chunks using existing M4 Hybrid Search
        retrieved_chunks = self.hybrid_search_service.search(
            db=db,
            query=clean_query,
            top_k=top_k,
            mode=SearchMode.hybrid
        )

        model_name = getattr(self.llm_provider, "model", "Groq-LLM")

        # 2. Check evidence sufficiency
        if not retrieved_chunks:
            logger.info("Zero chunks retrieved from Hybrid Search. Returning insufficient evidence response.")
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "query": clean_query,
                "answer": INSUFFICIENT_EVIDENCE_TEXT,
                "citations": [],
                "retrieved_chunks": [],
                "metadata": {
                    "retrieval_mode": "hybrid",
                    "chunks_retrieved": 0,
                    "chunks_used": 0,
                    "model": model_name,
                    "latency_ms": latency_ms
                }
            }

        # 3. Build structured context and system prompts
        system_prompt = self.build_system_prompt()
        prompt = self.build_context_prompt(clean_query, retrieved_chunks)

        # 4. Generate grounded answer via LLM Provider
        try:
            raw_answer = self.llm_provider.generate_answer(prompt=prompt, system_prompt=system_prompt)
        except Exception as llm_err:
            logger.error(f"LLM generation failed in RAG service: {llm_err}")
            latency_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "query": clean_query,
                "answer": INSUFFICIENT_EVIDENCE_TEXT,
                "citations": [],
                "retrieved_chunks": retrieved_chunks,
                "metadata": {
                    "retrieval_mode": "hybrid",
                    "chunks_retrieved": len(retrieved_chunks),
                    "chunks_used": 0,
                    "model": model_name,
                    "latency_ms": latency_ms
                }
            }

        answer_text = raw_answer.strip() if raw_answer else ""

        # Normalize insufficient evidence response if LLM indicates inadequate context
        if not answer_text or "insufficient evidence in the retrieved documents" in answer_text.lower():
            answer_text = INSUFFICIENT_EVIDENCE_TEXT
            citations = []
        else:
            # 5. Build database-backed citations strictly from retrieved DocumentChunks
            citations = []
            for chunk in retrieved_chunks:
                citations.append({
                    "chunk_id": chunk["chunk_id"],
                    "document_id": chunk["document_id"],
                    "document_name": chunk["document_name"],
                    "document_type": chunk["document_type"],
                    "jurisdiction": chunk.get("jurisdiction"),
                    "practice_area": chunk.get("practice_area"),
                    "version_id": chunk["version_id"],
                    "version_number": chunk["version_number"],
                    "section_name": chunk.get("section_name"),
                    "subsection_name": chunk.get("subsection_name"),
                    "page_number": chunk.get("page_number"),
                    "chunk_index": chunk["chunk_index"],
                    "content": chunk["content"]
                })

        latency_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "query": clean_query,
            "answer": answer_text,
            "citations": citations,
            "retrieved_chunks": retrieved_chunks,
            "metadata": {
                "retrieval_mode": "hybrid",
                "chunks_retrieved": len(retrieved_chunks),
                "chunks_used": len(citations),
                "model": model_name,
                "latency_ms": latency_ms
            }
        }
