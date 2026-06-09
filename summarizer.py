import asyncio
from groq import AsyncGroq
from config import GROQ_API_KEY

client = AsyncGroq(api_key=GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"


def _build_prompt(news_items: list[dict], topic: str) -> str:
    texts = "\n\n".join(
        f"- {item['title']}: {item['summary']}" for item in news_items
    )
    return (
        f"Resume las siguientes noticias de {topic} en español. "
        f"Destaca lo más importante. Máximo 3 párrafos, sé conciso:\n\n{texts}"
    )


async def _call_groq(prompt: str) -> str:
    for attempt in range(3):
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                await asyncio.sleep(5 * (attempt + 1))
                continue
            return f"Error: {str(e)[:100]}"
    return "Error: no se pudo generar el resumen."


async def summarize_cybersecurity(news_items: list[dict]) -> str:
    if not news_items:
        return "No se encontraron noticias de ciberseguridad."
    return await _call_groq(_build_prompt(news_items, "ciberseguridad"))


async def summarize_madrid(news_items: list[dict]) -> str:
    if not news_items:
        return "No se encontraron noticias de Madrid."
    return await _call_groq(_build_prompt(news_items, "Madrid (actualidad)"))


async def summarize_all(cyber_items: list[dict], madrid_items: list[dict]) -> str:
    parts = []
    if cyber_items:
        parts.append(_build_prompt(cyber_items, "ciberseguridad"))
    if madrid_items:
        parts.append(_build_prompt(madrid_items, "Madrid (actualidad)"))
    if not parts:
        return "No se encontraron noticias."
    prompt = "\n\n---\n\n".join(parts)
    return await _call_groq(prompt)
