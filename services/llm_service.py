import os
import asyncio

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


async def ask_llm(prompt: str):
    """Asynchronously ask the LLM by running the blocking client call in a thread.

    Returns the generated text.
    """
    def _call():
        return client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

    response = await asyncio.to_thread(_call)
    return response.text