import os
import asyncio
import logging

from dotenv import load_dotenv
from google import genai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError,
)

load_dotenv()

logger = logging.getLogger(__name__)

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10), retry=retry_if_exception_type(Exception))
def _call_llm(prompt: str):
    """Blocking call to the Gemini client with retries handled by tenacity.

    Kept as a sync function so it can be executed with `asyncio.to_thread`.
    """
    logger.debug("Calling Gemini for prompt (truncated): %s", prompt[:120])
    return client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )


async def ask_llm(prompt: str):
    """Asynchronously ask the LLM by running the blocking client call in a thread.

    Returns the generated text. Retries/backoff are handled by tenacity in
    the synchronous helper.
    """
    try:
        response = await asyncio.to_thread(_call_llm, prompt)
    except RetryError as exc:
        cause = exc.last_attempt.exception() if exc.last_attempt is not None else None
        message = str(cause) if cause else str(exc)
        raise RuntimeError(f"LLM request failed after retries: {message}") from exc

    return getattr(response, "text", str(response))