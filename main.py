import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Yahan apni Render Static Site ka URL dalein (jaise: https://your-app.onrender.com)
WEB_APP_URL = os.environ.get("WEB_APP_URL", "https://po-signal-bot-web.onrender.com")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🚀 OPEN BINARY HAWK DASHBOARD", web_app=WebAppInfo(url=WEB_APP_URL))
        ],
        [
            InlineKeyboardButton("⏸️ PAUSE SESSION", callback_data="pause"),
            InlineKeyboardButton("⚙️ MODE: AUTO", callback_data="mode")
        ],
        [
            InlineKeyboardButton("🎯 TARGET: 5 WINS", callback_data="target"),
            InlineKeyboardButton("📊 LIVE STATS", callback_data="stats")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🚀 **BINARY HAWK OTC ENGINE ACTIVE!**\n\n"
        "Click the button below to open the Live Signal Dashboard UI inside Telegram.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable missing!")
    
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot is running...")
    app.run_polling()
