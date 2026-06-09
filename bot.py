import asyncio
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import TELEGRAM_BOT_TOKEN
from news_collector import get_cybersecurity_news, get_madrid_news
from summarizer import summarize_cybersecurity, summarize_madrid

MAX_MSG = 4000


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        pass


def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(("0.0.0.0", port), HealthHandler).serve_forever()


def _chunk(text: str, max_len: int = MAX_MSG) -> list[str]:
    return [text[i:i+max_len] for i in range(0, len(text), max_len)] if len(text) > max_len else [text]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hola! Soy tu asistente de noticias con IA.\n\n"
        "Comandos:\n"
        "/resumen  - Ciberseguridad + Madrid\n"
        "/cyber    - Solo ciberseguridad\n"
        "/madrid   - Solo Madrid"
    )


async def resumen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.message.reply_text("Recopilando noticias...")
    cyber_items, madrid_items = await asyncio.gather(
        get_cybersecurity_news(), get_madrid_news()
    )
    await msg.edit_text("Generando resumen con IA...")
    tasks = []
    if cyber_items:
        tasks.append(summarize_cybersecurity(cyber_items))
    if madrid_items:
        tasks.append(summarize_madrid(madrid_items))
    results = await asyncio.gather(*tasks)
    final = ""
    if len(results) > 0:
        final += "<b>🔒 CIBERSEGURIDAD</b>\n" + results[0] + "\n\n"
    if len(results) > 1:
        final += "<b>🏙️ MADRID</b>\n" + results[1]
    for part in _chunk(final):
        await msg.edit_text(part, parse_mode="HTML")


async def cyber(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.message.reply_text("Recopilando noticias de ciberseguridad...")
    items = await get_cybersecurity_news()
    await msg.edit_text("Generando resumen...")
    text = "<b>🔒 CIBERSEGURIDAD</b>\n" + await summarize_cybersecurity(items)
    for part in _chunk(text):
        await msg.edit_text(part, parse_mode="HTML")


async def madrid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.message.reply_text("Recopilando noticias de Madrid...")
    items = await get_madrid_news()
    await msg.edit_text("Generando resumen...")
    text = "<b>🏙️ MADRID</b>\n" + await summarize_madrid(items)
    for part in _chunk(text):
        await msg.edit_text(part, parse_mode="HTML")


def main() -> None:
    threading.Thread(target=run_health_server, daemon=True).start()
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("resumen", resumen))
    app.add_handler(CommandHandler("cyber", cyber))
    app.add_handler(CommandHandler("madrid", madrid))
    print("Bot iniciado")
    app.run_polling()


if __name__ == "__main__":
    main()
