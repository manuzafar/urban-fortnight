"""
Base agent functionality for the Product Discovery Multi-Agent System.

This module provides the shared LLM client and common utilities used by all agents.
It handles Gemini API communication, response parsing, and error handling.
"""

import json
import re
import time
from typing import Any

from google import genai
from google.genai import types
import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from config import settings, get_agent_model

# Configure structured logging
logger = structlog.get_logger(__name__)

# Global client instance
_client: genai.Client | None = None


class LLMError(Exception):
    """Custom exception for LLM-related errors."""

    pass


class JSONParseError(Exception):
    """Custom exception for JSON parsing errors."""

    pass


def configure_gemini() -> None:
    """
    Configure the Gemini API with the API key from settings.

    This should be called once at application startup.
    """
    global _client
    _client = genai.Client(api_key=settings.google_api_key)
    logger.info("gemini_configured", model=settings.llm_model)


def get_client() -> genai.Client:
    """
    Get the configured Gemini client instance.

    Returns:
        genai.Client: Configured client instance.
    """
    global _client
    if _client is None:
        configure_gemini()
    return _client


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type((LLMError, ConnectionError, TimeoutError)),
    before_sleep=lambda retry_state: logger.warning(
        "llm_retry",
        attempt=retry_state.attempt_number,
        wait=retry_state.next_action.sleep,
    ),
)
async def call_llm(
    prompt: str,
    agent_name: str,
    model_override: str | None = None,
) -> dict[str, Any]:
    """
    Call the Gemini LLM with the given prompt and parse the JSON response.

    This function handles:
    - API communication with retries
    - Agent-specific model routing (Flash vs Pro)
    - Response parsing and validation
    - Token counting and timing
    - Error handling and logging

    Args:
        prompt: The formatted prompt to send to the LLM.
        agent_name: Name of the calling agent for logging and model selection.
        model_override: Optional model to use instead of agent-specific default.

    Returns:
        dict containing:
            - success: bool indicating if the call succeeded
            - data: parsed JSON response (if successful)
            - raw_response: raw text response
            - error: error message (if failed)
            - tokens_used: approximate token count
            - duration_seconds: time taken for the call
            - model_used: which model was actually used

    Raises:
        LLMError: If the API call fails after retries.
        JSONParseError: If the response cannot be parsed as JSON.
    """
    start_time = time.time()

    # Use agent-specific model or override
    model = model_override or get_agent_model(agent_name)

    logger.info("llm_call_start", agent=agent_name, model=model)

    raw_text = ""

    try:
        client = get_client()

        # Configure generation settings
        config = types.GenerateContentConfig(
            temperature=settings.llm_temperature,
            max_output_tokens=settings.llm_max_tokens,
            response_mime_type="application/json",
        )

        # Make the API call with agent-specific model
        response = await client.aio.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )

        duration = time.time() - start_time

        # Extract text from response
        raw_text = response.text

        # Parse JSON from response
        parsed_data = parse_json_response(raw_text, agent_name)

        # Estimate token usage
        tokens_used = estimate_tokens(prompt, raw_text)

        logger.info(
            "llm_call_success",
            agent=agent_name,
            model=model,
            duration=round(duration, 2),
            tokens=tokens_used,
        )

        return {
            "success": True,
            "data": parsed_data,
            "raw_response": raw_text,
            "error": None,
            "tokens_used": tokens_used,
            "duration_seconds": duration,
            "model_used": model,
        }

    except json.JSONDecodeError as e:
        duration = time.time() - start_time
        error_msg = f"Failed to parse JSON response: {str(e)}"
        logger.error("llm_json_parse_error", agent=agent_name, model=model, error=error_msg)

        return {
            "success": False,
            "data": None,
            "raw_response": raw_text,
            "error": error_msg,
            "tokens_used": 0,
            "duration_seconds": duration,
            "model_used": model,
        }

    except Exception as e:
        duration = time.time() - start_time
        error_msg = f"LLM call failed: {str(e)}"
        logger.error("llm_call_error", agent=agent_name, model=model, error=error_msg, exc_info=True)

        return {
            "success": False,
            "data": None,
            "raw_response": raw_text,
            "error": error_msg,
            "tokens_used": 0,
            "duration_seconds": duration,
            "model_used": model,
        }


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type((LLMError, ConnectionError, TimeoutError)),
    before_sleep=lambda retry_state: logger.warning(
        "llm_grounded_retry",
        attempt=retry_state.attempt_number,
        wait=retry_state.next_action.sleep,
    ),
)
async def call_llm_with_grounding(
    prompt: str,
    agent_name: str,
    model_override: str | None = None,
) -> dict[str, Any]:
    """
    Call the Gemini LLM with Google Search grounding enabled.

    Used for agents that benefit from real-world data (Customer Research,
    Business Strategy, Legal & Regulatory). Grounding enables the LLM to
    access current information from Google Search to validate market data,
    competitor info, regulations, and industry trends.

    Args:
        prompt: The formatted prompt to send to the LLM.
        agent_name: Name of the calling agent for logging and model selection.
        model_override: Optional model to use instead of agent-specific default.

    Returns:
        dict containing:
            - success: bool indicating if the call succeeded
            - data: parsed JSON response (if successful)
            - raw_response: raw text response
            - error: error message (if failed)
            - tokens_used: approximate token count
            - duration_seconds: time taken for the call
            - grounded: bool indicating grounding was used
            - model_used: which model was actually used

    Raises:
        LLMError: If the API call fails after retries.
        JSONParseError: If the response cannot be parsed as JSON.
    """
    # Use agent-specific model or override
    model = model_override or get_agent_model(agent_name)

    # Check if grounding is enabled globally
    if not settings.llm_enable_grounding:
        logger.info("grounding_disabled_fallback", agent=agent_name, model=model)
        result = await call_llm(prompt, agent_name, model_override=model)
        result["grounded"] = False
        return result

    start_time = time.time()
    logger.info("llm_grounded_call_start", agent=agent_name, model=model)

    raw_text = ""

    try:
        client = get_client()

        # Configure with Google Search grounding tool
        # Note: Grounding does NOT support response_mime_type="application/json"
        # (controlled generation). We rely on parse_json_response to extract JSON.
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        config = types.GenerateContentConfig(
            temperature=settings.llm_temperature,
            max_output_tokens=settings.llm_max_tokens,
            # Cannot use response_mime_type with grounding - Gemini API limitation
            tools=[grounding_tool],
        )

        # Make the API call with grounding using agent-specific model
        response = await client.aio.models.generate_content(
            model=model,
            contents=prompt,
            config=config,
        )

        duration = time.time() - start_time

        # Extract text from response
        raw_text = response.text

        # Parse JSON from response
        parsed_data = parse_json_response(raw_text, agent_name)

        # Estimate token usage
        tokens_used = estimate_tokens(prompt, raw_text)

        logger.info(
            "llm_grounded_call_success",
            agent=agent_name,
            model=model,
            duration=round(duration, 2),
            tokens=tokens_used,
        )

        return {
            "success": True,
            "data": parsed_data,
            "raw_response": raw_text,
            "error": None,
            "tokens_used": tokens_used,
            "duration_seconds": duration,
            "grounded": True,
            "model_used": model,
        }

    except json.JSONDecodeError as e:
        duration = time.time() - start_time
        error_msg = f"Failed to parse JSON response: {str(e)}"
        logger.error("llm_grounded_json_parse_error", agent=agent_name, model=model, error=error_msg)

        return {
            "success": False,
            "data": None,
            "raw_response": raw_text,
            "error": error_msg,
            "tokens_used": 0,
            "duration_seconds": duration,
            "grounded": True,
            "model_used": model,
        }

    except Exception as e:
        duration = time.time() - start_time
        error_msg = f"Grounded LLM call failed: {str(e)}"
        logger.warning("llm_grounded_call_failed", agent=agent_name, model=model, error=error_msg)

        # Fallback to non-grounded call
        logger.info("grounding_fallback_to_standard", agent=agent_name, model=model)
        try:
            result = await call_llm(prompt, agent_name, model_override=model)
            result["grounded"] = False
            return result
        except Exception as fallback_error:
            logger.error(
                "llm_grounded_fallback_failed",
                agent=agent_name,
                model=model,
                error=str(fallback_error),
                exc_info=True,
            )
            return {
                "success": False,
                "data": None,
                "raw_response": raw_text,
                "error": f"Both grounded and fallback calls failed: {error_msg}",
                "tokens_used": 0,
                "duration_seconds": duration,
                "grounded": False,
                "model_used": model,
            }


def parse_json_response(text: str, agent_name: str) -> dict[str, Any]:
    """
    Parse JSON from LLM response text.

    Handles common issues like:
    - Markdown code blocks around JSON
    - Leading/trailing whitespace
    - BOM characters
    - Truncated JSON (attempts to repair)
    - Missing commas between elements

    Args:
        text: Raw response text from LLM.
        agent_name: Name of the calling agent for logging.

    Returns:
        dict: Parsed JSON data.

    Raises:
        JSONParseError: If parsing fails.
    """
    # Clean the response text
    cleaned = text.strip()

    # Remove markdown code blocks if present
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]

    cleaned = cleaned.strip()

    # Remove BOM if present
    if cleaned.startswith("\ufeff"):
        cleaned = cleaned[1:]

    # Try to extract JSON if there's extra text
    json_match = re.search(r"\{[\s\S]*\}", cleaned)
    if json_match:
        cleaned = json_match.group()

    # First attempt: try direct parsing
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.warning(
            "json_parse_attempt_1_failed",
            agent=agent_name,
            error=str(e),
        )

    # Second attempt: try to repair common JSON issues
    try:
        repaired = repair_json(cleaned)
        result = json.loads(repaired)
        logger.info("json_repair_successful", agent=agent_name)
        return result
    except (json.JSONDecodeError, Exception) as e:
        logger.warning(
            "json_repair_failed",
            agent=agent_name,
            error=str(e),
        )

    # Third attempt: try to find and parse a valid JSON subset
    try:
        result = extract_partial_json(cleaned)
        if result:
            logger.info("json_partial_extraction_successful", agent=agent_name)
            return result
    except Exception as e:
        logger.warning(
            "json_partial_extraction_failed",
            agent=agent_name,
            error=str(e),
        )

    # All attempts failed
    logger.error(
        "json_parse_failed",
        agent=agent_name,
        text_preview=cleaned[:500],
    )
    raise JSONParseError(f"Failed to parse JSON after all repair attempts")


def repair_json(text: str) -> str:
    """
    Attempt to repair common JSON syntax errors.

    Handles:
    - Missing commas between array elements or object properties
    - Trailing commas
    - Unclosed brackets/braces (truncated responses)

    Args:
        text: Malformed JSON string.

    Returns:
        str: Repaired JSON string.
    """
    # Fix missing commas between elements (common LLM issue)
    # Pattern: "}\n{" or "]\n[" or value followed by key without comma
    text = re.sub(r'"\s*\n\s*"', '",\n"', text)
    text = re.sub(r'}\s*\n\s*"', '},\n"', text)
    text = re.sub(r']\s*\n\s*"', '],\n"', text)
    text = re.sub(r'}\s*\n\s*{', '},\n{', text)
    text = re.sub(r']\s*\n\s*{', '],\n{', text)
    text = re.sub(r'"\s*\n\s*{', '",\n{', text)
    text = re.sub(r'"\s*\n\s*\[', '",\n[', text)

    # Fix missing commas after values followed by keys
    text = re.sub(r'(true|false|null|\d+)\s*\n\s*"', r'\1,\n"', text)

    # Remove trailing commas before closing brackets
    text = re.sub(r',\s*}', '}', text)
    text = re.sub(r',\s*]', ']', text)

    # Try to close unclosed structures (truncated response)
    open_braces = text.count('{') - text.count('}')
    open_brackets = text.count('[') - text.count(']')

    if open_braces > 0 or open_brackets > 0:
        # Find the last complete value and truncate there
        # Then close remaining structures
        text = text.rstrip()

        # Remove incomplete string at the end
        if text.count('"') % 2 != 0:
            last_quote = text.rfind('"')
            if last_quote > 0:
                # Find the start of this incomplete string
                prev_quote = text.rfind('"', 0, last_quote)
                if prev_quote > 0:
                    text = text[:prev_quote + 1]

        # Remove trailing incomplete elements
        text = re.sub(r',\s*$', '', text)
        text = re.sub(r':\s*$', ': null', text)

        # Close remaining structures
        text += ']' * open_brackets
        text += '}' * open_braces

    return text


def extract_partial_json(text: str) -> dict[str, Any] | None:
    """
    Extract a valid partial JSON object from truncated text.

    Useful when the LLM response is cut off but contains valid data.

    Args:
        text: Potentially truncated JSON string.

    Returns:
        dict | None: Parsed JSON or None if extraction failed.
    """
    # Try progressively shorter substrings
    for end_pos in range(len(text), max(100, len(text) // 2), -100):
        substring = text[:end_pos]

        # Count brackets
        open_braces = substring.count('{') - substring.count('}')
        open_brackets = substring.count('[') - substring.count(']')

        # Skip if too unbalanced
        if open_braces > 10 or open_brackets > 10:
            continue

        # Try to close and parse
        attempt = substring.rstrip()

        # Clean up trailing partial content
        attempt = re.sub(r',\s*$', '', attempt)
        attempt = re.sub(r':\s*$', ': null', attempt)

        # Close structures
        attempt += ']' * max(0, open_brackets)
        attempt += '}' * max(0, open_braces)

        try:
            result = json.loads(attempt)
            if isinstance(result, dict) and len(result) > 0:
                return result
        except json.JSONDecodeError:
            continue

    return None


def estimate_tokens(prompt: str, response: str) -> int:
    """
    Estimate token count for prompt and response.

    Uses a simple heuristic of ~4 characters per token.
    This is an approximation since Gemini doesn't always
    provide exact token counts.

    Args:
        prompt: The prompt text.
        response: The response text.

    Returns:
        int: Estimated token count.
    """
    total_chars = len(prompt) + len(response)
    return total_chars // 4


def extract_feedback_for_agent(
    critique_feedback: dict[str, Any] | None,
    agent_key: str,
) -> str | None:
    """
    Extract revision feedback for a specific agent from critique feedback.

    Args:
        critique_feedback: The critique feedback dictionary.
        agent_key: The key for the agent's feedback (e.g., 'customer_research_feedback').

    Returns:
        str | None: Formatted feedback string or None if no feedback.
    """
    if not critique_feedback:
        return None

    feedback_list = critique_feedback.get(agent_key, [])
    if not feedback_list:
        return None

    priority_items = critique_feedback.get("priority_improvements", [])

    feedback_parts = ["### Specific Feedback:"]
    for i, item in enumerate(feedback_list, 1):
        feedback_parts.append(f"{i}. {item}")

    if priority_items:
        feedback_parts.append("\n### Priority Improvements:")
        for i, item in enumerate(priority_items, 1):
            feedback_parts.append(f"{i}. {item}")

    return "\n".join(feedback_parts)
