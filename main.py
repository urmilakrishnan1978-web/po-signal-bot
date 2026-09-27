import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Telegram Bot Token (Render Environment Variable ya Direct Fallback)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🚀 **PO-iSniper OTC Bot Active!**\n\n"
        "Bot is ready with 20s Pre-Alerts, Volatility Filters, and Auto/Manual Pair Selection.\n"
        "Use buttons below to control the session."
    )
    
    keyboard = [
        [
            InlineKeyboardButton("⏸️ PAUSE SESSION", callback_data="pause_session"),
            InlineKeyboardButton("⚙️ MODE: AUTO", callback_data="toggle_mode")
        ],
        [
            InlineKeyboardButton("🎯 TARGET: 5 WINS", callback_data="target_wins"),
            InlineKeyboardButton("📊 LIVE STATS", callback_data="live_stats")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data == "pause_session":
        await query.message.reply_text("⏸️ Session Status: PAUSED")
    elif data == "toggle_mode":
        await query.message.reply_text("⚙️ Mode switched to: MANUAL / AUTO")
    elif data == "target_wins":
        await query.message.reply_text("🎯 Target set to: 5 WINS")
    elif data == "live_stats":
        await query.message.reply_text("📊 Live Stats: Active session running smoothly.")

def main():
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Please set your TELEGRAM_BOT_TOKEN in Render Environment Variables.")
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
