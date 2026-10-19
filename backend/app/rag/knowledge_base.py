from __future__ import annotations

import hashlib
import logging
import math
import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import Product

logger = logging.getLogger(__name__)


def product_document(product: Product) -> str:
    specs = "; ".join(f"{key}: {value}" for key, value in (product.specifications_json or {}).items())
    return "\n".join(
        [
            f"Product: {product.name}",
            f"Category: {product.category}",
            f"Subcategory: {product.subcategory or 'Specification not available'}",
            f"Description: {product.description}",
            f"Use cases: {', '.join(product.use_cases or [])}",
            f"Industries: {', '.join(product.industries or [])}",
            f"Environment: {product.environment or 'Specification not available'}",
            f"Dimensions: {product.dimensions or 'Specification not available'}",
            f"Material: {product.material or 'Specification not available'}",
            f"Specifications: {specs or 'Specification not available'}",
            f"Source: {product.source}",
        ]
    )


class HashingEmbeddingModel:
    """Small offline local embedding fallback with stable signed feature hashing."""

    dimensions = 384
    name = "local-hashing-384"

    def encode(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        for token in tokens:
            digest = hashlib.sha256(token.encode()).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


@dataclass(frozen=True)
class RetrievalHit:
    product: Product
    score: float


class ProductKnowledgeBase:
    def __init__(self) -> None:
        self.embedding_model = HashingEmbeddingModel()
        self.backend = "local-hashing"
        self._sentence_model = None
        self._chroma = None

    def _try_production_backend(self) -> None:
        if settings.demo_mode or self._sentence_model is not None or self._chroma is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
            import chromadb

            self._sentence_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            client = chromadb.PersistentClient(path=str(settings.vector_path))
            self._chroma = client.get_or_create_collection("signaflow_products")
            self.backend = "chroma+all-MiniLM-L6-v2"
        except Exception as exc:
            logger.warning("rag backend=local-hashing reason=%s", type(exc).__name__)

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        return sum(x * y for x, y in zip(a, b, strict=False))

    def semantic_search(self, db: Session, query: str, limit: int = 12) -> list[RetrievalHit]:
        self._try_production_backend()
        products = db.query(Product).all()
        if self._sentence_model is not None and self._chroma is not None:
            existing = self._chroma.count()
            if existing != len(products):
                ids = [p.id for p in products]
                docs = [product_document(p) for p in products]
                embeddings = self._sentence_model.encode(docs, normalize_embeddings=True).tolist()
                if existing:
                    self._chroma.delete(ids=self._chroma.get().get("ids", []))
                self._chroma.add(ids=ids, documents=docs, embeddings=embeddings)
            query_embedding = self._sentence_model.encode([query], normalize_embeddings=True).tolist()[0]
            result = self._chroma.query(query_embeddings=[query_embedding], n_results=min(limit, len(products)))
            product_by_id = {p.id: p for p in products}
            return [RetrievalHit(product_by_id[item_id], max(0.0, min(1.0, 1 - distance))) for item_id, distance in zip(result["ids"][0], result["distances"][0], strict=False) if item_id in product_by_id]
        query_vector = self.embedding_model.encode(query)
        hits = [RetrievalHit(product, max(0.0, self._cosine(query_vector, self.embedding_model.encode(product_document(product))))) for product in products]
        return sorted(hits, key=lambda hit: hit.score, reverse=True)[:limit]


knowledge_base = ProductKnowledgeBase()

