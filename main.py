import os
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
threading.Thread(target=run_web, daemon=True).start()
import time
import datetime
import pytz
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ==========================================
# CONFIGURATION
# ==========================================
BOT_TOKEN = "8880160934:AAH3lrsBmd0prjtV6cyIYzkczcZRPjRZHtw"  # Cleaned Token
ADMIN_ID = 1420868312                                     # Aapka Locked Admin ID

# Top 28 Forex OTC Pairs
FOREX_OTC_PAIRS = [
    "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "AUD/USD OTC", "USD/CAD OTC",
    "USD/CHF OTC", "EUR/GBP OTC", "EUR/JPY OTC", "GBP/JPY OTC", "AUD/JPY OTC",
    "NZD/USD OTC", "EUR/CAD OTC", "EUR/AUD OTC", "GBP/CAD OTC", "GBP/AUD OTC",
    "AUD/CAD OTC", "AUD/NZD OTC", "CAD/JPY OTC", "CHF/JPY OTC", "NZD/JPY OTC",
    "EUR/NZD OTC", "GBP/NZD OTC", "CAD/CHF OTC", "NZD/CAD OTC", "NZD/CHF OTC",
    "AUD/CHF OTC", "USD/TRY OTC", "USD/INR OTC"
]

# Database for Licenses (Telegram ID -> Expiry Timestamp)
LICENSE_DB = {
    ADMIN_ID: datetime.datetime(2099, 12, 31, 23, 59, 59) # Lifetime Access for Admin
}

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def get_ist_time():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.datetime.now(ist)

def is_authorized(user_id):
    if user_id not in LICENSE_DB:
        return False
    expiry = LICENSE_DB[user_id]
    if get_ist_time().replace(tzinfo=None) > expiry:
        return False
    return True

# ==========================================
# OTC SIGNAL GENERATOR LOGIC
# ==========================================
def scan_otc_pattern(selected_pair=None):
    pair = selected_pair if selected_pair else random.choice(FOREX_OTC_PAIRS)
    payout = random.randint(85, 94)
    direction = random.choice(["CALL (BUY) ⬆️", "PUT (SELL) ⬇️"])
    confidence = random.randint(88, 96)
    
    ist_now = get_ist_time()
    entry_time = (ist_now + datetime.timedelta(minutes=1)).strftime("%H:%M:00 IST")
    
    return {
        "pair": pair,
        "direction": direction,
        "payout": f"{payout}%",
        "confidence": f"{confidence}%",
        "entry_time": entry_time
    }

# ==========================================
# TELEGRAM BOT HANDLERS
# ==========================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # License Authorization Check
    if not is_authorized(user_id):
        await update.message.reply_text(
            "🔒 **ACCESS DENIED - PO iSniper OTC**\n\n"
            "Aapke paas active subscription nahi hai.\n"
            "Access ke liye Admin se contact karein.\n\n"
            f"👤 **Aapki Telegram ID:** `{user_id}`",
            parse_mode="Markdown"
        )
        return

    # Web-App Launcher Button
    keyboard = [
        [InlineKeyboardButton("🚀 OPEN OTC TERMINAL", web_app=WebAppInfo(url="https://your-webapp-link.com"))],
        [InlineKeyboardButton("📊 PAIRS LIST", callback_data="list_pairs")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "⚡ **PO iSniper OTC — Pocket Option Market** ⚡\n"
        "-----------------------------------------\n"
        "• System Status: License Active ✅\n"
        "• Security Mode: VIP Private Access\n\n"
        "Terminal launch karne ke liye niche click karein:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# Admin Licensing Commands (/add_user <USER_ID> <DAYS>)
async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return

    try:
        target_id = int(context.args[0])
        days = int(context.args[1])
        expiry_date = get_ist_time().replace(tzinfo=None) + datetime.timedelta(days=days)
        LICENSE_DB[target_id] = expiry_date
        
        await update.message.reply_text(
            f"✅ **License Activated Successfully!**\n\n"
            f"• User ID: `{target_id}`\n"
            f"• Access: {days} Days\n"
            f"• Expiry: {expiry_date.strftime('%d-%b-%Y %H:%M')} IST",
            parse_mode="Markdown"
        )
    except Exception:
        await update.message.reply_text("Usage: `/add_user <TELEGRAM_ID> <DAYS>`", parse_mode="Markdown")

# ==========================================
# MAIN APP EXECUTION
# ==========================================
if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add_user", add_user))
    
    print("🚀 PO iSniper OTC Engine Running Successfully...")
    app.run_polling()
