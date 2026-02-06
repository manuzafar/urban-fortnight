"""
Embedding Service for Cross-Run Learning.

This module provides utilities for generating embeddings using Gemini's
text-embedding-004 model and performing vector similarity searches
against stored memories in Supabase with pgvector.
"""

import structlog
from google import genai

from config import settings
from utils.db import get_supabase_client

logger = structlog.get_logger(__name__)

# Gemini embedding model - produces 768-dimensional vectors
EMBEDDING_MODEL = "text-embedding-004"
EMBEDDING_DIMENSION = 768


async def generate_embedding(text: str) -> list[float]:
    """
    Generate an embedding vector for the given text.

    Uses Gemini's text-embedding-004 model which produces
    768-dimensional embeddings.

    Args:
        text: The text to embed.

    Returns:
        list[float]: 768-dimensional embedding vector.

    Raises:
        Exception: If embedding generation fails.
    """
    try:
        client = genai.Client(api_key=settings.google_api_key)

        # Truncate text if too long (embedding models have limits)
        max_chars = 25000  # Conservative limit
        if len(text) > max_chars:
            text = text[:max_chars]
            logger.warning(
                "text_truncated_for_embedding",
                original_length=len(text),
                truncated_to=max_chars,
            )

        result = await client.aio.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
        )

        embedding = result.embeddings[0].values

        logger.debug(
            "embedding_generated",
            text_length=len(text),
            embedding_dimension=len(embedding),
        )

        return embedding

    except Exception as e:
        logger.error(
            "embedding_generation_failed",
            error=str(e),
            text_preview=text[:100],
        )
        raise


async def find_similar_memories(
    query_embedding: list[float],
    domain_type: str | None = None,
    agent_name: str | None = None,
    user_id: str | None = None,
    match_threshold: float = 0.7,
    limit: int = 3,
) -> list[dict]:
    """
    Find similar high-quality memories using vector similarity.

    Queries the run_memories table in Supabase using pgvector
    to find semantically similar past outputs.

    Args:
        query_embedding: The embedding vector to match against.
        domain_type: Optional filter by domain type (e.g., "fintech", "healthcare").
        agent_name: Optional filter by agent name.
        user_id: Optional filter by user ID.
        match_threshold: Minimum similarity score (0-1). Default 0.7.
        limit: Maximum number of results. Default 3.

    Returns:
        list[dict]: List of similar memories with similarity scores.
    """
    try:
        supabase = await get_supabase_client()

        # Call the match_memories function via RPC
        result = await supabase.rpc(
            "match_memories",
            {
                "query_embedding": query_embedding,
                "match_threshold": match_threshold,
                "match_count": limit,
                "filter_domain": domain_type,
                "filter_agent": agent_name,
                "filter_user_id": user_id,
            }
        ).execute()

        memories = result.data or []

        logger.info(
            "similar_memories_found",
            count=len(memories),
            domain_type=domain_type,
            agent_name=agent_name,
            threshold=match_threshold,
        )

        return memories

    except Exception as e:
        logger.error(
            "memory_search_failed",
            error=str(e),
            domain_type=domain_type,
            agent_name=agent_name,
        )
        # Return empty list on error - non-blocking
        return []


async def store_memory(
    user_id: str,
    session_id: str,
    domain_type: str,
    agent_name: str,
    quality_score: float,
    content_summary: str,
    embedding: list[float],
    industry: str | None = None,
) -> bool:
    """
    Store a high-quality agent output as a memory.

    Args:
        user_id: The user who created this output.
        session_id: The session this came from.
        domain_type: The product domain type.
        agent_name: Which agent produced this output.
        quality_score: Quality assessment score (0-1).
        content_summary: Compressed summary of the output.
        embedding: Pre-computed embedding vector.
        industry: Optional industry classification.

    Returns:
        bool: True if storage succeeded, False otherwise.
    """
    # Only store if quality is high enough
    if quality_score < 0.7:
        logger.debug(
            "memory_skipped_low_quality",
            quality_score=quality_score,
            agent_name=agent_name,
        )
        return False

    try:
        supabase = await get_supabase_client()

        await supabase.table("run_memories").insert({
            "user_id": user_id,
            "session_id": session_id,
            "domain_type": domain_type,
            "industry": industry,
            "agent_name": agent_name,
            "quality_score": quality_score,
            "content_summary": content_summary,
            "embedding": embedding,
        }).execute()

        logger.info(
            "memory_stored",
            user_id=user_id,
            session_id=session_id,
            agent_name=agent_name,
            quality_score=quality_score,
        )

        return True

    except Exception as e:
        logger.error(
            "memory_storage_failed",
            error=str(e),
            user_id=user_id,
            agent_name=agent_name,
        )
        return False


def compress_to_summary(output: dict, max_chars: int = 2000) -> str:
    """
    Compress agent output to a summary suitable for embedding.

    Extracts key sections and truncates to fit within embedding limits.

    Args:
        output: The agent output dictionary.
        max_chars: Maximum characters for summary.

    Returns:
        str: Compressed summary text.
    """
    import json

    # Key fields to prioritize for different agent types
    priority_fields = [
        "executive_summary",
        "recommendation",
        "key_findings",
        "summary",
        "pain_signals",
        "lean_canvas",
        "user_personas",
        "epics",
        "system_components",
        "overall_risk_assessment",
    ]

    summary_parts = []

    # Extract priority fields first
    for field in priority_fields:
        if field in output and output[field]:
            value = output[field]
            if isinstance(value, str):
                summary_parts.append(f"{field}: {value}")
            elif isinstance(value, list) and len(value) > 0:
                # Take first few items
                items = value[:3]
                summary_parts.append(f"{field}: {json.dumps(items, default=str)}")
            elif isinstance(value, dict):
                summary_parts.append(f"{field}: {json.dumps(value, default=str)[:500]}")

    # Join and truncate
    summary = "\n".join(summary_parts)

    if len(summary) > max_chars:
        summary = summary[:max_chars - 3] + "..."

    return summary


def format_memories_for_prompt(memories: list[dict]) -> str:
    """
    Format retrieved memories into a prompt-friendly string.

    Args:
        memories: List of memory objects from find_similar_memories.

    Returns:
        str: Formatted string for injection into prompts.
    """
    if not memories:
        return ""

    formatted = []

    for i, memory in enumerate(memories, 1):
        similarity = memory.get("similarity", 0)
        quality = memory.get("quality_score", 0)
        content = memory.get("content_summary", "")

        formatted.append(
            f"### Example {i} (Similarity: {similarity:.0%}, Quality: {quality:.0%})\n"
            f"{content}\n"
        )

    return "\n".join(formatted)
