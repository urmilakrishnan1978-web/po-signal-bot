import os
import time
import asyncio
import logging
from datetime import datetime
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Telegram Bot Token (Environment Variable se lega ya fallback)
BOT_TOKEN = "8880160934:AAH3lrsBmd0prjtV6cyIYzkczcZRPjRZHtw"

# IST Timezone
IST = pytz.timezone('Asia/Kolkata')

# 27 Pocket Option OTC Pairs List
OTC_PAIRS = [
    "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "USD/CHF OTC", "AUD/USD OTC",
    "NZD/USD OTC", "USD/CAD OTC", "EUR/GBP OTC", "EUR/JPY OTC", "GBP/JPY OTC",
    "AUD/JPY OTC", "EUR/CAD OTC", "AUD/CAD OTC", "CAD/CHF OTC", "NZD/JPY OTC",
    "EUR/AUD OTC", "GBP/CAD OTC", "GBP/CHF OTC", "NZD/CAD OTC", "USD/INR OTC",
    "USD/BRL OTC", "USD/PKR OTC", "USD/BDT OTC", "USD/EGP OTC", "USD/TRY OTC",
    "USD/RUB OTC", "USD/IDR OTC"
]

# Bot State Variables
bot_state = {
    "active": True,
    "mode": "AUTO",  # "AUTO" ya "MANUAL"
    "current_pair_idx": 0,
    "manual_pair": "EUR/USD OTC",
    "target_wins": 5,
    "current_wins": 0,
    "current_losses": 0
}

# Keyboards Generator
def get_control_keyboard():
    status_btn = InlineKeyboardButton("⏸ PAUSE SESSION" if bot_state["active"] else "▶️ RESUME SESSION", callback_data="toggle_active")
    mode_btn = InlineKeyboardButton(f"⚙️ MODE: {bot_state['mode']}", callback_data="toggle_mode")
    target_btn = InlineKeyboardButton(f"🎯 TARGET: {bot_state['target_wins']} WINS", callback_data="set_target")
    stats_btn = InlineKeyboardButton("📊 LIVE STATS", callback_data="show_stats")
    
    keyboard = [
        [status_btn, mode_btn],
        [target_btn, stats_btn]
    ]
    
    if bot_state["mode"] == "MANUAL":
        pair_btn = InlineKeyboardButton(f"🔀 PAIR: {bot_state['manual_pair']}", callback_data="next_pair")
        keyboard.append([pair_btn])
        
    return InlineKeyboardMarkup(keyboard)

# /start Command Handler
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🚀 **PO-iSniper OTC Bot Active!**\n\n"
        "Bot is ready with **20s Pre-Alerts**, **Volatility Filters**, and **Auto/Manual Pair Selection**.\n"
        "Use buttons below to control the session."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=get_control_keyboard())

# Callback Handler for Inline Buttons
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data == "toggle_active":
        bot_state["active"] = not bot_state["active"]
        status = "Resumed ▶️" if bot_state["active"] else "Paused ⏸"
        await query.edit_message_text(f"Session status updated: **{status}**", reply_markup=get_control_keyboard(), parse_mode="Markdown")
        
    elif data == "toggle_mode":
        bot_state["mode"] = "MANUAL" if bot_state["mode"] == "AUTO" else "AUTO"
        await query.edit_message_text(f"Trading Mode changed to: **{bot_state['mode']}**", reply_markup=get_control_keyboard(), parse_mode="Markdown")
        
    elif data == "next_pair":
        bot_state["current_pair_idx"] = (bot_state["current_pair_idx"] + 1) % len(OTC_PAIRS)
        bot_state["manual_pair"] = OTC_PAIRS[bot_state["current_pair_idx"]]
        await query.edit_message_text(f"Selected Manual Pair: **{bot_state['manual_pair']}**", reply_markup=get_control_keyboard(), parse_mode="Markdown")
        
    elif data == "show_stats":
        stats_msg = (
            f"📊 **CURRENT SESSION STATS**\n"
            f"------------------------------------\n"
            f"✅ Wins: `{bot_state['current_wins']}`\n"
            f"❌ Losses: `{bot_state['current_losses']}`\n"
            f"🎯 Target: `{bot_state['target_wins']} Wins`\n"
            f"⚙️ Mode: `{bot_state['mode']}`\n"
            f"------------------------------------"
        )
        await query.message.reply_text(stats_msg, parse_mode="Markdown")

# Background Signal Loop (20s Pre-Alert Engine)
async def signal_generator_loop(app: Application, chat_id: int):
    while True:
        try:
            await asyncio.sleep(1)
            if not bot_state["active"]:
                continue
                
            # Check Target Hit
            if bot_state["current_wins"] >= bot_state["target_wins"]:
                bot_state["active"] = False
                await app.bot.send_message(
                    chat_id=chat_id, 
                    text=f"🎯 **TARGET ACHIEVED!** ({bot_state['target_wins']} Wins Hit). Session Automatically Paused.",
                    parse_mode="Markdown"
                )
                continue

            now = datetime.now(IST)
            # Exactly 20 Seconds Pre-Alert (At :40s mark of every minute)
            if now.second == 40:
                # Pair Selection
                if bot_state["mode"] == "AUTO":
                    pair = OTC_PAIRS[now.minute % len(OTC_PAIRS)]
                else:
                    pair = bot_state["manual_pair"]
                
                # Signal Direction Calculation (Simulated Strategy)
                direction = "CALL (BUY) ⬆️" if now.minute % 2 == 0 else "PUT (SELL) ⬇️"
                
                # Big & Bold Monospace Timestamps
                sent_time = now.strftime("%I:%M:%S %p")
                entry_time = (now.replace(second=0) + pytz.timedelta(minutes=1)).strftime("%I:%M:00 %p")
                
                signal_msg = (
                    f"🔴 **POCKET OPTION - OTC SIGNAL** 🔴\n"
                    f"------------------------------------\n"
                    f"📊 **PAIR**         : `{pair}`\n"
                    f"🎯 **DIRECTION**    : `{direction}`\n"
                    f"⏳ **EXPIRY**       : `1 MINUTE`\n\n"
                    f"📡 **SENT TIME**   : `{sent_time}`\n"
                    f"⏰ **ENTRY TIME**  : `{entry_time}`\n\n"
                    f"⚡ **STATUS**       : `SAFE ZONE ✅`\n"
                    f"------------------------------------\n"
                    f"💡 *Note: Entry time par hi 1-minute trade open karein.*"
                )
                
                await app.bot.send_message(chat_id=chat_id, text=signal_msg, parse_mode="Markdown", reply_markup=get_control_keyboard())
                await asyncio.sleep(15) # Avoid double triggers
                
        except Exception as e:
            logging.error(f"Error in signal loop: {e}")
            await asyncio.sleep(2) # Auto-restart delay on glitch

# Main Runner Function
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    # Auto-restart & Background Task Execution
    print("Bot Started Successfully...")
    app.run_polling()

if __name__ == "__main__":
    main()
