import os
import asyncio
import logging
from datetime import datetime
import pytz
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# LOGGING SETUP
logging.basicConfig(level=logging.INFO)

# FLASK KEEP-ALIVE SERVER FOR RENDER
app = Flask(__name__)

@app.route('/')
def health_check():
    return "PO iSniper OTC Bot is Running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# Start Flask in background thread
Thread(target=run_flask, daemon=True).start()

# CONFIGURATION
BOT_TOKEN = "8880160934:AAH3lrsBmd0prjtV6cyIYzkczcZRPjRZHtw"
ADMIN_ID = 1420608312

# 28 ALL ACTIVE OTC PAIRS
FOREX_OTC_PAIRS = [
    "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "AUD/USD OTC", "USD/CAD OTC",
    "USD/CHF OTC", "EUR/GBP OTC", "EUR/JPY OTC", "GBP/JPY OTC", "AUD/JPY OTC",
    "NZD/USD OTC", "EUR/CAD OTC", "EUR/AUD OTC", "GBP/CAD OTC", "GBP/AUD OTC",
    "AUD/CAD OTC", "AUD/NZD OTC", "CAD/JPY OTC", "CHF/JPY OTC", "NZD/JPY OTC",
    "EUR/NZD OTC", "USD/RUB OTC", "CAD/CHF OTC", "NZD/CAD OTC", "GBP/CHF OTC",
    "AUD/CHF OTC", "USD/TRY OTC", "USD/INR OTC"
]

LICENSE_DB = {
    ADMIN_ID: datetime(2030, 12, 31, 23, 59, 59)
}

# AUTO SIGNAL STATE
auto_signal_active = False
auto_task = None

# HELPER FUNCTIONS
def get_ist_time():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)

def is_authorized(user_id):
    if user_id not in LICENSE_DB:
        return False
    expiry = LICENSE_DB[user_id]
    if get_ist_time().replace(tzinfo=None) > expiry:
        return False
    return True

def generate_signal_text():
    import random
    pair = random.choice(FOREX_OTC_PAIRS)
    direction = random.choice(["🟢 CALL (BUY)", "🔴 PUT (SELL)"])
    payout = random.randint(75, 92)  # Min 70%+ Payout
    
    now_ist = get_ist_time()
    # Signal generated 15-20 sec before next candle open
    entry_minute = now_ist.minute + 1 if now_ist.second >= 40 else now_ist.minute
    entry_hour = now_ist.hour
    if entry_minute >= 60:
        entry_minute = 0
        entry_hour = (entry_hour + 1) % 24
        
    entry_time_str = f"{entry_hour:02d}:{entry_minute:02d}:00 IST"
    generated_time_str = now_ist.strftime("%I:%M:%S %p IST")
    
    msg = (
        f"⚡ **PO iSniper OTC Signal** ⚡\n"
        f"─────────────────────────\n"
        f"📈 **Pair:** `{pair}`\n"
        f"🎯 **Direction:** {direction}\n"
        f"💰 **Payout:** {payout}%\n"
        f"⏰ **Next Candle Entry:** `{entry_time_str}`\n"
        f"🕒 **Generated At:** `{generated_time_str}`\n"
        f"─────────────────────────\n"
        f"💡 *Note: Next candle open hote hi 1-minute entry lein.*"
    )
    return msg

# BOT HANDLERS
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text(
            f"🚫 **ACCESS DENIED - PO iSniper OTC** 🚫\n"
            f"Aapka Telegram ID: `{user_id}`\n"
            f"Aapke paas active subscription nahi hai."
        )
        return

    keyboard = [
        [InlineKeyboardButton("📊 28 OTC PAIRS", callback_data="list_pairs")],
        [InlineKeyboardButton("⚡ GET SIGNAL (MANUAL)", callback_data="get_signal")],
        [InlineKeyboardButton("🔄 AUTO SIGNALS (ON/OFF)", callback_data="toggle_auto")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"⚡ **PO iSniper OTC - Pocket Option Market** ⚡\n"
        f"─────────────────────────\n"
        f"• **System Status:** License Active ✅\n"
        f"• **Security Mode:** VIP Private Access\n"
        f"• **Timezone:** IST (Indian Standard Time)\n\n"
        f"Niche diye gaye buttons se feature choose karein:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def auto_signal_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    global auto_signal_active
    while auto_signal_active:
        now = get_ist_time()
        # Wait until 15-20 seconds before the minute ends (at second 42)
        target_second = 42
        seconds_to_wait = (target_second - now.second) % 60
        if seconds_to_wait == 0:
            seconds_to_wait = 60
        
        await asyncio.sleep(seconds_to_wait)
        if auto_signal_active:
            signal_msg = generate_signal_text()
            await context.bot.send_message(chat_id=chat_id, text=signal_msg, parse_mode="Markdown")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global auto_signal_active, auto_task
    query = update.callback_query
    await query.answer()

    if query.data == "list_pairs":
        pairs_str = "\n".join([f"• {p} (70%-92% Payout)" for p in FOREX_OTC_PAIRS])
        await query.message.reply_text(
            f"📊 **Available 28 Active OTC Pairs:**\n\n{pairs_str}",
            parse_mode="Markdown"
        )

    elif query.data == "get_signal":
        signal_msg = generate_signal_text()
        await query.message.reply_text(signal_msg, parse_mode="Markdown")

    elif query.data == "toggle_auto":
        chat_id = query.message.chat_id
        if not auto_signal_active:
            auto_signal_active = True
            auto_task = asyncio.create_task(auto_signal_loop(context, chat_id))
            await query.message.reply_text("🟢 **AUTO SIGNALS ACTIVATED!**\nHar minute 15-20 second pehle automatic signal aata rahega.")
        else:
            auto_signal_active = False
            if auto_task:
                auto_task.cancel()
            await query.message.reply_text("🔴 **AUTO SIGNALS DEACTIVATED!**")

# MAIN EXECUTION
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))

    print("🚀 PO iSniper OTC Engine Running Successfully...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
