from google import genai
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-2.0-flash"


def _build_prompt(news_items: list[dict], topic: str) -> str:
    texts = "\n\n".join(
        f"- {item['title']}: {item['summary']}" for item in news_items
    )
    return (
        f"Resume las siguientes noticias de {topic} en español. "
        f"Destaca lo más importante. Máximo 3 párrafos, sé conciso:\n\n{texts}"
    )


async def summarize_cybersecurity(news_items: list[dict]) -> str:
    if not news_items:
        return "No se encontraron noticias de ciberseguridad."
    response = await client.aio.models.generate_content(
        model=MODEL, contents=_build_prompt(news_items, "ciberseguridad")
    )
    return response.text


async def summarize_madrid(news_items: list[dict]) -> str:
    if not news_items:
        return "No se encontraron noticias de Madrid."
    response = await client.aio.models.generate_content(
        model=MODEL, contents=_build_prompt(news_items, "Madrid (actualidad)")
    )
    return response.text
