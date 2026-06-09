import asyncio
from google import genai
from google.genai import errors
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


async def _call_gemini(prompt: str) -> str:
    for attempt in range(3):
        try:
            response = await client.aio.models.generate_content(
                model=MODEL, contents=prompt
            )
            return response.text
        except errors.ClientError as e:
            if "429" in str(e) and attempt < 2:
                await asyncio.sleep(30)
                continue
            return "Error: límite de API excedido. Espera un minuto y vuelve a intentarlo."
    return "Error: no se pudo generar el resumen."


async def summarize_cybersecurity(news_items: list[dict]) -> str:
    if not news_items:
        return "No se encontraron noticias de ciberseguridad."
    return await _call_gemini(_build_prompt(news_items, "ciberseguridad"))


async def summarize_madrid(news_items: list[dict]) -> str:
    if not news_items:
        return "No se encontraron noticias de Madrid."
    return await _call_gemini(_build_prompt(news_items, "Madrid (actualidad)"))


async def summarize_all(cyber_items: list[dict], madrid_items: list[dict]) -> str:
    parts = []
    if cyber_items:
        parts.append(_build_prompt(cyber_items, "ciberseguridad"))
    if madrid_items:
        parts.append(_build_prompt(madrid_items, "Madrid (actualidad)"))
    if not parts:
        return "No se encontraron noticias."
    prompt = "\n\n---\n\n".join(parts)
    return await _call_gemini(prompt)
