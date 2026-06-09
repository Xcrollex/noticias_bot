import asyncio
from openai import AsyncOpenAI
from config import NVIDIA_API_KEY

client = AsyncOpenAI(
    api_key=NVIDIA_API_KEY,
    base_url="https://integrate.api.nvidia.com/v1",
)
MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"


async def _call(prompt: str) -> str:
    for attempt in range(3):
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                top_p=0.95,
                max_tokens=65536,
                extra_body={
                    "chat_template_kwargs": {"enable_thinking": True},
                    "reasoning_budget": 16384,
                },
            )
            reasoning = getattr(response.choices[0].message, "reasoning_content", None)
            content = response.choices[0].message.content or ""
            return f"{reasoning}\n\n{content}" if reasoning else content
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                await asyncio.sleep(5 * (attempt + 1))
                continue
            return f"Error: {str(e)[:100]}"
    return "Error: no se pudo generar el resumen."


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
    return await _call(_build_prompt(news_items, "ciberseguridad"))


async def summarize_madrid(news_items: list[dict]) -> str:
    if not news_items:
        return "No se encontraron noticias de Madrid."
    return await _call(_build_prompt(news_items, "Madrid (actualidad)"))


async def summarize_all(cyber_items: list[dict], madrid_items: list[dict]) -> str:
    parts = []
    if cyber_items:
        parts.append(_build_prompt(cyber_items, "ciberseguridad"))
    if madrid_items:
        parts.append(_build_prompt(madrid_items, "Madrid (actualidad)"))
    if not parts:
        return "No se encontraron noticias."
    return await _call("\n\n---\n\n".join(parts))
