import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")


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
    return (await model.generate_content_async(
        _build_prompt(news_items, "ciberseguridad")
    )).text


async def summarize_madrid(news_items: list[dict]) -> str:
    if not news_items:
        return "No se encontraron noticias de Madrid."
    return (await model.generate_content_async(
        _build_prompt(news_items, "Madrid (actualidad)")
    )).text
