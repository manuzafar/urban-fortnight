"""
Memory Pipeline for Cross-Run Learning.

This module handles the extraction, processing, and storage of
high-quality agent outputs for use in future runs.
"""

import asyncio
from typing import Any

import structlog

from agents.state import DiscoveryState
from services.embeddings import (
    generate_embedding,
    store_memory,
    compress_to_summary,
)

logger = structlog.get_logger(__name__)

# Minimum quality score to store a memory
QUALITY_THRESHOLD = 0.8

# Agent output mappings
AGENT_OUTPUT_MAPPINGS = [
    ("customer_research", "customer_research", "Market Hypothesis Generator"),
    ("business_case", "business_strategy", "Business Strategy Agent"),
    ("product_requirements", "product_requirements", "Product Requirements"),
    ("technical_architecture", "technical_architect", "Technical Architect"),
    ("legal_regulatory_review", "legal_regulatory", "Legal & Regulatory Review"),
    ("executive_summary", "executive_summary", "Executive Summary"),
]


async def store_successful_run(
    session_id: str,
    user_id: str,
    state: DiscoveryState,
) -> dict[str, bool]:
    """
    Extract and store memories from a successful discovery run.

    This function:
    1. Checks if overall quality meets the threshold
    2. Extracts outputs from each agent
    3. Compresses each to a summary
    4. Generates embeddings
    5. Stores as memories for future retrieval

    Args:
        session_id: The discovery session ID.
        user_id: The user who ran this session.
        state: The final discovery state with all outputs.

    Returns:
        dict[str, bool]: Status of memory storage for each agent.
    """
    # Get overall quality score
    quality_assessment = state.get("quality_assessment", {})
    overall_score = quality_assessment.get("overall_score", 0)

    if overall_score < QUALITY_THRESHOLD:
        logger.info(
            "run_below_quality_threshold",
            session_id=session_id,
            overall_score=overall_score,
            threshold=QUALITY_THRESHOLD,
        )
        return {"skipped": True, "reason": "below_quality_threshold"}

    # Extract domain type from research plan
    research_plan = state.get("research_plan", {})
    domain_type = research_plan.get("domain_type", "general")
    industry = state.get("industry")

    # Get section-specific scores if available
    section_scores = {
        s.get("section"): s.get("score", overall_score)
        for s in quality_assessment.get("section_scores", [])
    }

    results = {}
    storage_tasks = []

    for state_key, agent_key, agent_display_name in AGENT_OUTPUT_MAPPINGS:
        output = state.get(state_key)

        if not output:
            results[agent_key] = False
            continue

        # Get agent-specific quality score or use overall
        agent_score = section_scores.get(state_key, overall_score)

        if agent_score < QUALITY_THRESHOLD:
            logger.debug(
                "agent_output_below_threshold",
                agent=agent_key,
                score=agent_score,
                threshold=QUALITY_THRESHOLD,
            )
            results[agent_key] = False
            continue

        # Create storage task
        task = _store_agent_memory(
            session_id=session_id,
            user_id=user_id,
            agent_name=agent_key,
            output=output,
            quality_score=agent_score,
            domain_type=domain_type,
            industry=industry,
        )
        storage_tasks.append((agent_key, task))

    # Run all storage tasks concurrently
    if storage_tasks:
        task_results = await asyncio.gather(
            *[task for _, task in storage_tasks],
            return_exceptions=True,
        )

        for (agent_key, _), result in zip(storage_tasks, task_results):
            if isinstance(result, Exception):
                logger.error(
                    "memory_storage_exception",
                    agent=agent_key,
                    error=str(result),
                )
                results[agent_key] = False
            else:
                results[agent_key] = result

    # Log summary
    stored_count = sum(1 for v in results.values() if v is True)
    logger.info(
        "run_memories_stored",
        session_id=session_id,
        total_agents=len(AGENT_OUTPUT_MAPPINGS),
        stored_count=stored_count,
        results=results,
    )

    return results


async def _store_agent_memory(
    session_id: str,
    user_id: str,
    agent_name: str,
    output: dict[str, Any],
    quality_score: float,
    domain_type: str,
    industry: str | None,
) -> bool:
    """
    Store a single agent's output as a memory.

    Args:
        session_id: The session ID.
        user_id: The user ID.
        agent_name: The agent's name.
        output: The agent's output dictionary.
        quality_score: Quality assessment score.
        domain_type: Product domain type.
        industry: Optional industry.

    Returns:
        bool: True if storage succeeded.
    """
    try:
        # Compress output to summary
        summary = compress_to_summary(output)

        if not summary or len(summary) < 50:
            logger.warning(
                "summary_too_short",
                agent=agent_name,
                summary_length=len(summary) if summary else 0,
            )
            return False

        # Generate embedding
        embedding = await generate_embedding(summary)

        # Store memory
        success = await store_memory(
            user_id=user_id,
            session_id=session_id,
            domain_type=domain_type,
            agent_name=agent_name,
            quality_score=quality_score,
            content_summary=summary,
            embedding=embedding,
            industry=industry,
        )

        return success

    except Exception as e:
        logger.error(
            "agent_memory_storage_failed",
            agent=agent_name,
            error=str(e),
        )
        return False


async def retrieve_memories_for_agent(
    product_idea: str,
    agent_name: str,
    domain_type: str | None = None,
    user_id: str | None = None,
    limit: int = 3,
) -> list[dict]:
    """
    Retrieve relevant memories for an agent based on product idea.

    Args:
        product_idea: The product idea to find similar examples for.
        agent_name: The agent that will use these memories.
        domain_type: Optional domain type filter.
        user_id: Optional user ID filter.
        limit: Maximum memories to retrieve.

    Returns:
        list[dict]: Retrieved memory objects.
    """
    from services.embeddings import find_similar_memories

    try:
        # Generate embedding for product idea
        query_embedding = await generate_embedding(product_idea)

        # Find similar memories
        memories = await find_similar_memories(
            query_embedding=query_embedding,
            domain_type=domain_type,
            agent_name=agent_name,
            user_id=user_id,
            match_threshold=0.7,
            limit=limit,
        )

        logger.info(
            "memories_retrieved",
            agent=agent_name,
            count=len(memories),
            domain_type=domain_type,
        )

        return memories

    except Exception as e:
        logger.error(
            "memory_retrieval_failed",
            agent=agent_name,
            error=str(e),
        )
        return []
