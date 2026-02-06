"""
Services package for the Product Discovery System.

This package contains:
- embeddings: Gemini embedding generation and vector search
- memory_pipeline: Cross-run learning storage and retrieval
"""

from services.embeddings import (
    generate_embedding,
    find_similar_memories,
    store_memory,
    compress_to_summary,
    format_memories_for_prompt,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSION,
)

from services.memory_pipeline import (
    store_successful_run,
    retrieve_memories_for_agent,
    QUALITY_THRESHOLD,
)

__all__ = [
    # Embeddings
    "generate_embedding",
    "find_similar_memories",
    "store_memory",
    "compress_to_summary",
    "format_memories_for_prompt",
    "EMBEDDING_MODEL",
    "EMBEDDING_DIMENSION",
    # Memory Pipeline
    "store_successful_run",
    "retrieve_memories_for_agent",
    "QUALITY_THRESHOLD",
]
