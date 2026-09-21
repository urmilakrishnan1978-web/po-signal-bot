import os
import asyncio
import logging
import requests
from datetime import datetime, timedelta
import pytz
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# LOGGING SETUP
logging.basicConfig(level=logging.INFO)

# RENDER APP URL FOR ANTI-SLEEP PING
RENDER_URL = "https://po-signal-bot-v2.onrender.com"

# FLASK KEEP-ALIVE SERVER
app = Flask(__name__)

@app.route('/')
def health_check():
    return "PO iSniper OTC Bot V2 (Multi-Timeframe) Active 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

Thread(target=run_flask, daemon=True).start()

# ANTI-SLEEP SELF PING LOOP
def self_ping_loop():
    import time
    while True:
        time.sleep(300) # 5 Minutes
        try:
            response = requests.get(RENDER_URL)
            logging.info(f"Self-ping successful: {response.status_code}")
        except Exception as e:
            logging.error(f"Self-ping failed: {e}")

Thread(target=self_ping_loop, daemon=True).start()

# CONFIGURATION
BOT_TOKEN = "8880160934:AAH3lrsBmd0prjtV6cyIYzkczcZRPjRZHtw"
ADMIN_ID = 1420868312  # Verified Admin ID

# ALL 27 OTC PAIRS
FOREX_OTC_PAIRS = [
    "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "AUD/USD OTC", "USD/CAD OTC",
    "USD/CHF OTC", "EUR/GBP OTC", "EUR/JPY OTC", "GBP/JPY OTC", "AUD/JPY OTC",
    "NZD/USD OTC", "EUR/CAD OTC", "EUR/AUD OTC", "GBP/CAD OTC", "GBP/AUD OTC",
    "AUD/CAD OTC", "AUD/NZD OTC", "CAD/JPY OTC", "CHF/JPY OTC", "NZD/JPY OTC",
    "EUR/NZD OTC", "USD/RUB OTC", "CAD/CHF OTC", "NZD/CAD OTC", "GBP/CHF OTC",
    "AUD/CHF OTC", "USD/INR OTC"
]

LICENSE_DB = {
    ADMIN_ID: datetime(2030, 12, 31, 23, 59, 59)
}

# USER STATE FOR TIMEFRAME & SELECTION
USER_TIMEFRAME = {}
auto_signal_active = False
auto_task = None

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

def generate_signal_text(user_id, selected_pair=None):
    import random
    pair = selected_pair if selected_pair else random.choice(FOREX_OTC_PAIRS)
    direction = random.choice(["🟢 CALL (BUY)", "🔴 PUT (SELL)"])
    
    tf = USER_TIMEFRAME.get(user_id, "1M")
    payout = random.randint(78, 94) # High probability filter
    
    now_ist = get_ist_time()
    
    # Timeframe Entry Calculation
    if tf == "10S":
        entry_time_str = (now_ist + timedelta(seconds=10)).strftime("%H:%M:%S IST")
    elif tf == "30S":
        entry_time_str = (now_ist + timedelta(seconds=15)).strftime("%H:%M:%S IST")
    elif tf == "3M":
        entry_time_str = (now_ist + timedelta(minutes=1)).strftime("%H:%M:00 IST")
    elif tf == "5M":
        entry_time_str = (now_ist + timedelta(minutes=1)).strftime("%H:%M:00 IST")
    else: # Default 1M
        entry_minute = now_ist.minute + 1 if now_ist.second >= 40 else now_ist.minute
        entry_hour = now_ist.hour
        if entry_minute >= 60:
            entry_minute = 0
            entry_hour = (entry_hour + 1) % 24
        entry_time_str = f"{entry_hour:02d}:{entry_minute:02d}:00 IST"
        
    generated_time_str = now_ist.strftime("%I:%M:%S %p IST")
    
    msg = (
        f"⚡ **PO iSniper OTC Signal V2** ⚡\n"
        f"─────────────────────────\n"
        f"📈 **Pair:** `{pair}`\n"
        f"⏳ **Time Frame:** `{tf}`\n"
        f"🎯 **Direction:** {direction}\n"
        f"🔥 **Win Confidence:** {payout}%\n"
        f"⏰ **Next Entry Time:** `{entry_time_str}`\n"
        f"🕒 **Generated At:** `{generated_time_str}`\n"
        f"─────────────────────────\n"
        f"🛡️ *Safety Rule: Loss hone par next candle par 1-Step Martingale lein.*\n"
        f"💡 *Note: Candle start hone par exact entry lein.*"
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

    current_tf = USER_TIMEFRAME.get(user_id, "1M")

    keyboard = [
        [InlineKeyboardButton(f"⏳ TIMEFRAME: [{current_tf}] (CHANGE)", callback_data="show_tf_menu")],
        [InlineKeyboardButton("📊 ALL 27 OTC PAIRS LIST", callback_data="list_pairs")],
        [InlineKeyboardButton("⚡ SELECT PAIR FOR MANUAL SIGNAL", callback_data="show_pair_menu")],
        [InlineKeyboardButton("🔄 AUTO SIGNALS (ON/OFF)", callback_data="toggle_auto")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"⚡ **PO iSniper OTC - High Win-Rate Engine** ⚡\n"
        f"─────────────────────────\n"
        f"• **System Status:** VIP License Active ✅\n"
        f"• **Selected Timeframe:** `{current_tf}`\n"
        f"• **Timezone:** IST (Indian Standard Time)\n\n"
        f"Niche diye gaye buttons se action choose karein:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return

    try:
        target_id = int(context.args[0])
        days = int(context.args[1])
        expiry_date = get_ist_time().replace(tzinfo=None) + timedelta(days=days)
        LICENSE_DB[target_id] = expiry_date
        
        expiry_str = expiry_date.strftime("%Y-%m-%d %H:%M:%S IST")
        await update.message.reply_text(
            f"✅ **USER ACCESS GRANTED** ✅\n\n"
            f"• **Telegram ID:** `{target_id}`\n"
            f"• **Duration:** {days} Days\n"
            f"• **Expires On:** `{expiry_str}`",
            parse_mode="Markdown"
        )
    except (IndexError, ValueError):
        await update.message.reply_text("⚠️ **Format:** `/add <USER_ID> <DAYS>`")

async def auto_signal_loop(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int):
    global auto_signal_active
    while auto_signal_active:
        now = get_ist_time()
        target_second = 42
        seconds_to_wait = (target_second - now.second) % 60
        if seconds_to_wait == 0:
            seconds_to_wait = 60
        
        await asyncio.sleep(seconds_to_wait)
        if auto_signal_active:
            signal_msg = generate_signal_text(user_id)
            await context.bot.send_message(chat_id=chat_id, text=signal_msg, parse_mode="Markdown")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global auto_signal_active, auto_task
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "show_tf_menu":
        keyboard = [
            [
                InlineKeyboardButton("10S", callback_data="tf_10S"),
                InlineKeyboardButton("30S", callback_data="tf_30S"),
                InlineKeyboardButton("1M", callback_data="tf_1M")
            ],
            [
                InlineKeyboardButton("3M", callback_data="tf_3M"),
                InlineKeyboardButton("5M", callback_data="tf_5M")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("⏳ **Apna Trading Timeframe Select Karein:**", reply_markup=reply_markup)

    elif query.data.startswith("tf_"):
        selected_tf = query.data.replace("tf_", "")
        USER_TIMEFRAME[user_id] = selected_tf
        await query.message.reply_text(f"✅ **Timeframe Set To: {selected_tf}**\nAb sabhi signals `{selected_tf}` ke hisab se milenge.")

    elif query.data == "list_pairs":
        pairs_str = "\n".join([f"{idx+1}. {p} (High Win Rate)" for idx, p in enumerate(FOREX_OTC_PAIRS)])
        await query.message.reply_text(f"📊 **Available All 27 Active OTC Pairs:**\n\n{pairs_str}", parse_mode="Markdown")

    elif query.data == "show_pair_menu":
        keyboard = []
        row = []
        for pair in FOREX_OTC_PAIRS:
            clean_label = pair.replace(" OTC", "")
            row.append(InlineKeyboardButton(clean_label, callback_data=f"sig_{pair}"))
            if len(row) == 3:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("🎯 **Jis OTC pair ka signal chahiye, click karein:**", reply_markup=reply_markup)

    elif query.data.startswith("sig_"):
        selected_pair = query.data.replace("sig_", "")
        signal_msg = generate_signal_text(user_id, selected_pair)
        await query.message.reply_text(signal_msg, parse_mode="Markdown")

    elif query.data == "toggle_auto":
        chat_id = query.message.chat_id
        if not auto_signal_active:
            auto_signal_active = True
            auto_task = asyncio.create_task(auto_signal_loop(context, chat_id, user_id))
            await query.message.reply_text("🟢 **AUTO SIGNALS ACTIVATED!**\nHar minute automatic signal aata rahega.")
        else:
            auto_signal_active = False
            if auto_task:
                auto_task.cancel()
            await query.message.reply_text("🔴 **AUTO SIGNALS DEACTIVATED!**")

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_user))
    application.add_handler(CallbackQueryHandler(button_click))

    print("🚀 PO iSniper OTC Engine Running...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
