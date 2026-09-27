import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Token fallback setting
TELEGRAM_BOT_TOKEN = "8629088801:AAEP9d2z_1miB03T7-sCVyZpbBUbpFIjPuo"
WEB_APP_URL = os.environ.get("WEB_APP_URL", "https://po-signal-bot-web.onrender.com")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🚀 OPEN PO-iSNIPER DASHBOARD", web_app=WebAppInfo(url=WEB_APP_URL))
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
        "🚀 **PO-iSNIPER OTC ENGINE ACTIVE!**\n\n"
        "Click the button below to open the Live Signal Dashboard UI inside Telegram.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        raise ValueError("TELEGRAM_BOT_TOKEN missing!")
    
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("PO-iSNIPER Bot is running...")
    app.run_polling()
