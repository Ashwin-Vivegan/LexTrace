import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.semantic_search import SemanticSearchService
from app.services.keyword_search import KeywordSearchService
from app.schemas.search import SearchMode

logger = logging.getLogger(__name__)

class HybridSearchService:
    """
    Hybrid Search Engine combining FAISS Semantic Search and SQLite FTS5 Keyword Search.
    Normalizes scores, merges results, eliminates duplicates, and applies weighted fusion ranking.
    """
    def __init__(
        self,
        semantic_service: SemanticSearchService,
        keyword_service: KeywordSearchService,
        default_semantic_weight: float = 0.7,
        default_keyword_weight: float = 0.3,
        default_candidate_multiplier: int = 4
    ):
        self.semantic_service = semantic_service
        self.keyword_service = keyword_service
        self.semantic_weight = default_semantic_weight
        self.keyword_weight = default_keyword_weight
        self.candidate_multiplier = default_candidate_multiplier

    def _normalize_scores(self, results: List[Dict[str, Any]], score_key: str = "score") -> Dict[str, float]:
        """
        Applies Min-Max normalization to convert raw retrieval scores into a [0, 1] range.
        Returns a map of chunk_id -> normalized_score.
        """
        if not results:
            return {}

        scores = [res[score_key] for res in results]
        min_score = min(scores)
        max_score = max(scores)
        score_range = max_score - min_score

        normalized = {}
        for res in results:
            cid = res["chunk_id"]
            raw = res[score_key]
            if score_range > 1e-6:
                norm_val = (raw - min_score) / score_range
            else:
                # All scores are equal (e.g., single result or identical relevance)
                norm_val = 1.0 if raw > 0 else 0.5
            normalized[cid] = norm_val

        return normalized

    def search(
        self,
        db: Session,
        query: str,
        top_k: int = 5,
        mode: SearchMode = SearchMode.hybrid,
        semantic_weight: Optional[float] = None,
        keyword_weight: Optional[float] = None,
        candidate_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes unified search supporting semantic, keyword, or hybrid mode.
        """
        if not query or not query.strip():
            return []

        w_sem = semantic_weight if semantic_weight is not None else self.semantic_weight
        w_kw = keyword_weight if keyword_weight is not None else self.keyword_weight
        c_k = candidate_k if candidate_k is not None else max(20, top_k * self.candidate_multiplier)

        if mode == SearchMode.semantic:
            raw_semantic = self.semantic_service.search(db, query, top_k=top_k)
            for item in raw_semantic:
                item["score"] = item.pop("similarity_score", item.get("score", 0.0))
                item["retrieval_type"] = "semantic"
            return raw_semantic

        if mode == SearchMode.keyword:
            raw_keyword = self.keyword_service.search(db, query, top_k=top_k)
            for item in raw_keyword:
                item["retrieval_type"] = "keyword"
            return raw_keyword

        # HYBRID MODE
        # 1. Fetch larger candidate pools from both engines
        semantic_candidates = self.semantic_service.search(db, query, top_k=c_k)
        keyword_candidates = self.keyword_service.search(db, query, top_k=c_k)

        # Standardize score keys
        for item in semantic_candidates:
            if "similarity_score" in item:
                item["score"] = item["similarity_score"]

        # If both candidates are empty, return empty
        if not semantic_candidates and not keyword_candidates:
            return []

        # 2. Normalize scores for each candidate set
        norm_sem_map = self._normalize_scores(semantic_candidates, score_key="score")
        norm_kw_map = self._normalize_scores(keyword_candidates, score_key="score")

        # 3. Build index of item metadata by chunk_id
        items_by_chunk_id: Dict[str, Dict[str, Any]] = {}

        for item in semantic_candidates:
            cid = item["chunk_id"]
            items_by_chunk_id[cid] = dict(item)

        for item in keyword_candidates:
            cid = item["chunk_id"]
            if cid not in items_by_chunk_id:
                items_by_chunk_id[cid] = dict(item)

        # 4. Fuse scores & determine retrieval source
        fused_results = []
        for cid, item in items_by_chunk_id.items():
            in_sem = cid in norm_sem_map
            in_kw = cid in norm_kw_map

            sem_norm = norm_sem_map.get(cid, 0.0)
            kw_norm = norm_kw_map.get(cid, 0.0)

            # Combined weighted score
            hybrid_score = (w_sem * sem_norm) + (w_kw * kw_norm)

            if in_sem and in_kw:
                retrieval_type = "hybrid"
            elif in_sem:
                retrieval_type = "semantic"
            else:
                retrieval_type = "keyword"

            item["score"] = round(hybrid_score, 4)
            item["retrieval_type"] = retrieval_type

            # Remove obsolete field if present
            item.pop("similarity_score", None)

            fused_results.append(item)

        # 5. Rank by hybrid_score descending and slice to top_k
        fused_results.sort(key=lambda x: x["score"], reverse=True)
        return fused_results[:top_k]
