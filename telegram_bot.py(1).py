import asyncio
import aiohttp
import logging
from datetime import datetime

# ===== CONFIG =====
BOT_TOKEN = "8595429894:AAFk5nSji-5DazuOontdAd0ncLoGrMnK2gY"
CHANNEL_ID = "-1003586310854"
TWELVE_API = "d4fd55b09ef4424187e10b5b07da0d77"

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
log = logging.getLogger(__name__)

# ===== PAIRS =====
LIVE_PAIRS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "USD/CAD", "USD/CHF", "AUD/USD",
    "CAD/JPY", "EUR/CAD", "GBP/JPY", "CHF/JPY", "EUR/GBP", "GBP/AUD",
    "GBP/CHF", "EUR/AUD", "EUR/CHF", "AUD/CAD", "AUD/JPY", "CAD/CHF",
    "AUD/CHF", "GBP/CAD", "NZD/USD", "EUR/JPY", "AUD/NZD", "GBP/NZD",
    "EUR/NZD", "NZD/JPY", "XAU/USD", "XAG/USD"
]

OTC_PAIRS = [
    "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC", "AUD/USD OTC",
    "USD/CAD OTC", "USD/CHF OTC", "NZD/USD OTC", "EUR/GBP OTC",
    "EUR/JPY OTC", "GBP/JPY OTC", "EUR/AUD OTC", "AUD/JPY OTC",
    "CHF/JPY OTC", "EUR/CAD OTC", "GBP/CAD OTC", "GBP/CHF OTC",
    "AUD/CAD OTC", "AUD/CHF OTC", "NZD/JPY OTC", "NZD/CAD OTC",
    "USD/SGD OTC", "USD/NOK OTC", "USD/SEK OTC", "USD/DKK OTC",
    "USD/PLN OTC", "CAD/CHF OTC", "EUR/CHF OTC", "EUR/NZD OTC",
    "GBP/AUD OTC", "GBP/NZD OTC"
]

ALL_PAIRS = LIVE_PAIRS + OTC_PAIRS

SYMBOL_MAP = {
    "EUR/USD": "EUR/USD", "GBP/USD": "GBP/USD", "USD/JPY": "USD/JPY",
    "AUD/USD": "AUD/USD", "USD/CAD": "USD/CAD", "USD/CHF": "USD/CHF",
    "CAD/JPY": "CAD/JPY", "EUR/CAD": "EUR/CAD", "GBP/JPY": "GBP/JPY",
    "CHF/JPY": "CHF/JPY", "EUR/GBP": "EUR/GBP", "GBP/AUD": "GBP/AUD",
    "GBP/CHF": "GBP/CHF", "EUR/AUD": "EUR/AUD", "EUR/CHF": "EUR/CHF",
    "AUD/CAD": "AUD/CAD", "AUD/JPY": "AUD/JPY", "CAD/CHF": "CAD/CHF",
    "AUD/CHF": "AUD/CHF", "GBP/CAD": "GBP/CAD", "NZD/USD": "NZD/USD",
    "EUR/JPY": "EUR/JPY", "AUD/NZD": "AUD/NZD", "GBP/NZD": "GBP/NZD",
    "EUR/NZD": "EUR/NZD", "NZD/JPY": "NZD/JPY", "XAU/USD": "XAU/USD",
    "XAG/USD": "XAG/USD",
    # OTC — same API symbols (OTC prices closely follow live)
    "EUR/USD OTC": "EUR/USD", "GBP/USD OTC": "GBP/USD",
    "USD/JPY OTC": "USD/JPY", "AUD/USD OTC": "AUD/USD",
    "USD/CAD OTC": "USD/CAD", "USD/CHF OTC": "USD/CHF",
    "NZD/USD OTC": "NZD/USD", "EUR/GBP OTC": "EUR/GBP",
    "EUR/JPY OTC": "EUR/JPY", "GBP/JPY OTC": "GBP/JPY",
    "EUR/AUD OTC": "EUR/AUD", "AUD/JPY OTC": "AUD/JPY",
    "CHF/JPY OTC": "CHF/JPY", "EUR/CAD OTC": "EUR/CAD",
    "GBP/CAD OTC": "GBP/CAD", "GBP/CHF OTC": "GBP/CHF",
    "AUD/CAD OTC": "AUD/CAD", "AUD/CHF OTC": "AUD/CHF",
    "NZD/JPY OTC": "NZD/JPY", "NZD/CAD OTC": "NZD/CAD",
    "USD/SGD OTC": "USD/SGD", "USD/NOK OTC": "USD/NOK",
    "USD/SEK OTC": "USD/SEK", "USD/DKK OTC": "USD/DKK",
    "USD/PLN OTC": "USD/PLN", "CAD/CHF OTC": "CAD/CHF",
    "EUR/CHF OTC": "EUR/CHF", "EUR/NZD OTC": "EUR/NZD",
    "GBP/AUD OTC": "GBP/AUD", "GBP/NZD OTC": "GBP/NZD",
}

# ===== SEND MESSAGE =====
async def send_message(session, text, parse_mode="HTML"):
    url = f"{BASE_URL}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": parse_mode
    }
    try:
        async with session.post(url, json=data) as r:
            result = await r.json()
            if result.get("ok"):
                log.info("Message sent!")
            else:
                log.error(f"Send error: {result}")
    except Exception as e:
        log.error(f"Send message error: {e}")

# ===== FETCH MARKET DATA =====
async def fetch_market_data(session, symbol):
    sym = SYMBOL_MAP.get(symbol, symbol)
    try:
        # Fetch RSI, MACD, Quote
        urls = [
            f"https://api.twelvedata.com/quote?symbol={sym}&apikey={TWELVE_API}",
            f"https://api.twelvedata.com/rsi?symbol={sym}&interval=1min&time_period=14&apikey={TWELVE_API}",
            f"https://api.twelvedata.com/macd?symbol={sym}&interval=1min&apikey={TWELVE_API}",
        ]
        results = []
        for url in urls:
            async with session.get(url) as r:
                results.append(await r.json())
            await asyncio.sleep(0.3)

        quote, rsi_data, macd_data = results

        price = float(quote.get("close", 0) or quote.get("price", 0) or 0)
        prev  = float(quote.get("previous_close", price) or price)
        rsi   = float(rsi_data["values"][0]["rsi"]) if rsi_data.get("values") else 50.0
        macd_val = float(macd_data["values"][0]["macd"]) if macd_data.get("values") else 0.0
        macd_sig = float(macd_data["values"][0]["signal"]) if macd_data.get("values") else 0.0

        # Signal logic
        bull = 0
        bear = 0
        if rsi < 45:   bull += 2
        elif rsi > 55: bear += 2
        if macd_val > macd_sig: bull += 2
        else:                   bear += 2
        if price > prev: bull += 1
        else:            bear += 1

        is_up = bull >= bear
        strength = max(bull, bear) / (bull + bear) if (bull + bear) > 0 else 0.5
        conf = int(62 + strength * 28)

        return {
            "symbol": symbol,
            "price": price,
            "rsi": round(rsi, 1),
            "macd": round(macd_val, 5),
            "is_up": is_up,
            "conf": conf,
            "bull": bull,
            "bear": bear
        }

    except Exception as e:
        log.error(f"Market data error for {symbol}: {e}")
        return None

# ===== FORMAT SIGNAL MESSAGE =====
def format_signal(data, timeframe="M1"):
    now = datetime.now().strftime("%H:%M:%S")
    arrow = "⬆️" if data["is_up"] else "⬇️"
    direction = "CALL — BUY 🟢" if data["is_up"] else "PUT — SELL 🔴"
    conf_bar = "█" * (data["conf"] // 10) + "░" * (10 - data["conf"] // 10)
    rsi_signal = "Oversold 📈" if data["rsi"] < 40 else "Overbought 📉" if data["rsi"] > 60 else "Neutral ➡️"
    macd_signal = "Bullish 📈" if data["macd"] > 0 else "Bearish 📉"
    price_str = f"${data['price']:.5f}" if data['price'] > 0 else "N/A"

    msg = f"""
🔔 <b>PO SIGNAL PRO</b> 🔔
━━━━━━━━━━━━━━━━━━━━
📊 <b>Pair:</b> {data['symbol']}
⏱ <b>Timeframe:</b> {timeframe}
🕐 <b>Time:</b> {now} IST
💰 <b>Price:</b> {price_str}
━━━━━━━━━━━━━━━━━━━━
{arrow} <b>SIGNAL: {direction}</b>
━━━━━━━━━━━━━━━━━━━━
📈 <b>Confidence:</b> {data['conf']}%
{conf_bar}

🔍 <b>Indicators:</b>
• RSI (14): <b>{data['rsi']}</b> — {rsi_signal}
• MACD: <b>{data['macd']}</b> — {macd_signal}
• Bull Score: {data['bull']} | Bear Score: {data['bear']}
━━━━━━━━━━━━━━━━━━━━
⚠️ <i>Sirf Live Market mein use karein
12 PM – 5 PM IST best time</i>
━━━━━━━━━━━━━━━━━━━━
🤖 @Traders_New_AI_Bot
"""
    return msg.strip()

# ===== HANDLE COMMANDS =====
async def handle_updates(session, offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset

    try:
        async with session.get(url, params=params) as r:
            data = await r.json()
            if not data.get("ok"):
                return offset

            updates = data.get("result", [])
            for update in updates:
                offset = update["update_id"] + 1

                # Channel post commands
                post = update.get("channel_post") or update.get("message")
                if not post:
                    continue

                text = post.get("text", "").strip().lower()
                chat_id = post["chat"]["id"]

                if text in ["/signal", "/signal@traders_new_ai_bot"]:
                    await cmd_signal(session)
                elif text in ["/start", "/start@traders_new_ai_bot"]:
                    await cmd_start(session)
                elif text in ["/help", "/help@traders_new_ai_bot"]:
                    await cmd_help(session)
                elif text in ["/live", "/live@traders_new_ai_bot"]:
                    await cmd_live_list(session)
                elif text in ["/otc", "/otc@traders_new_ai_bot"]:
                    await cmd_otc_list(session)
                elif text in ["/topsignal", "/topsignal@traders_new_ai_bot"]:
                    await cmd_top_signal(session)
                elif text.startswith("/pair "):
                    pair = text.replace("/pair ", "").strip()
                    await cmd_pair_signal(session, pair)

    except Exception as e:
        log.error(f"Update error: {e}")

    return offset

async def cmd_start(session):
    msg = """
🚀 <b>PO Signal Pro Bot</b> 🚀
━━━━━━━━━━━━━━━━━━━━
AI Trading Signal Bot ready hai!
Live + OTC — 24/7 Active ✅

<b>Commands:</b>
/signal — EUR/USD signal (default)
/live — Sab Live pairs ki list
/otc — Sab OTC pairs ki list
/pair EURUSD — Kisi bhi pair ka signal
/topsignal — Best signal dhundhe
/help — Sab commands

⚠️ <i>Trading mein risk hota hai — apna analysis bhi karein</i>
━━━━━━━━━━━━━━━━━━━━
🤖 @Traders_New_AI_Bot
"""
    await send_message(session, msg.strip())

async def cmd_help(session):
    msg = """
📖 <b>Help — PO Signal Pro</b>
━━━━━━━━━━━━━━━━━━━━
<b>Commands:</b>
• /signal — EUR/USD live signal
• /topsignal — Best high-conf signal
• /live — Live pairs list
• /otc — OTC pairs list
• /pair EURUSD — EUR/USD signal
• /pair GBPUSD — GBP/USD signal
• /pair USDJPY — USD/JPY signal
• /pair XAUUSD — Gold signal
• /pair EURUSDOTC — EUR/USD OTC
• /pair GBPUSDOTC — GBP/USD OTC

<b>Signal:</b>
⬆️ CALL = BUY | ⬇️ PUT = SELL

<b>Best Pairs (Live):</b>
🥇 EUR/USD 🥈 GBP/USD 🥉 USD/JPY

<b>OTC — Evening/Night ke liye:</b>
✅ EUR/USD OTC, GBP/USD OTC
✅ AUD/USD OTC, USD/JPY OTC

🕐 Bot 24/7 active hai!
━━━━━━━━━━━━━━━━━━━━
🤖 @Traders_New_AI_Bot
"""
    await send_message(session, msg.strip())

async def cmd_live_list(session):
    pairs_txt = "\n".join([f"• <code>/pair {p.replace('/','').replace(' ','')}</code> — {p}" for p in LIVE_PAIRS])
    msg = f"""
📊 <b>All Live Market Pairs</b>
━━━━━━━━━━━━━━━━━━━━
{pairs_txt}
━━━━━━━━━━━━━━━━━━━━
Signal lene ke liye pair code tap karein
🤖 @Traders_New_AI_Bot
"""
    await send_message(session, msg.strip())

async def cmd_otc_list(session):
    pairs_txt = "\n".join([f"• <code>/pair {p.replace('/','').replace(' ','')}</code> — {p}" for p in OTC_PAIRS])
    msg = f"""
🌙 <b>All OTC Pairs (Evening/Night)</b>
━━━━━━━━━━━━━━━━━━━━
{pairs_txt}
━━━━━━━━━━━━━━━━━━━━
OTC pairs Live market ke baad best hain
🤖 @Traders_New_AI_Bot
"""
    await send_message(session, msg.strip())

async def cmd_top_signal(session):
    await send_message(session, "🔍 <b>Best signal dhundh raha hoon — thodi der...</b>")
    best = None
    # Check top 6 pairs quickly
    check_pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "EUR/JPY", "GBP/JPY"]
    async with aiohttp.ClientSession() as s:
        for pair in check_pairs:
            data = await fetch_market_data(s, pair)
            if data:
                if best is None or data["conf"] > best["conf"]:
                    best = data
            await asyncio.sleep(0.5)
    if best:
        msg = format_signal(best, "M1")
        msg += "\n\n🏆 <b>Highest Confidence Signal!</b>"
        await send_message(session, msg)
    else:
        await send_message(session, "❌ Signal nahi mila — thodi der mein try karein")

async def cmd_signal(session):
    await send_message(session, "⏳ <b>EUR/USD ka live signal fetch ho raha hai...</b>")
    data = await fetch_market_data(session, "EUR/USD")
    if data:
        await send_message(session, format_signal(data, "M1"))
    else:
        await send_message(session, "❌ Signal fetch nahi hua — thodi der mein try karein")

async def cmd_pair_signal(session, pair):
    pair_map = {
        "EURUSD": "EUR/USD", "GBPUSD": "GBP/USD", "USDJPY": "USD/JPY",
        "AUDUSD": "AUD/USD", "USDCAD": "USD/CAD", "USDCHF": "USD/CHF",
        "EURGBP": "EUR/GBP", "EURJPY": "EUR/JPY", "GBPJPY": "GBP/JPY",
        "XAUUSD": "XAU/USD", "XAGUSD": "XAG/USD", "CADJPY": "CAD/JPY",
        "EURCAD": "EUR/CAD", "CHFJPY": "CHF/JPY", "GBPAUD": "GBP/AUD",
        "GBPCHF": "GBP/CHF", "EURAUD": "EUR/AUD", "EURCHF": "EUR/CHF",
        "AUDCAD": "AUD/CAD", "AUDJPY": "AUD/JPY", "CADCHF": "CAD/CHF",
        "AUDCHF": "AUD/CHF", "GBPCAD": "GBP/CAD", "NZDUSD": "NZD/USD",
        "AUDNZD": "AUD/NZD", "GBPNZD": "GBP/NZD", "EURNZD": "EUR/NZD",
        "NZDJPY": "NZD/JPY",
        # OTC
        "EURUSDOTC": "EUR/USD OTC", "GBPUSDOTC": "GBP/USD OTC",
        "USDJPYOTC": "USD/JPY OTC", "AUDUSDOTC": "AUD/USD OTC",
        "USDCADOTC": "USD/CAD OTC", "USDCHFOTC": "USD/CHF OTC",
        "NZDUSDOTC": "NZD/USD OTC", "EURGBPOTC": "EUR/GBP OTC",
        "EURJPYOTC": "EUR/JPY OTC", "GBPJPYOTC": "GBP/JPY OTC",
        "EURAUDOTC": "EUR/AUD OTC", "AUDJPYOTC": "AUD/JPY OTC",
        "CHFJPYOTC": "CHF/JPY OTC", "EURCADOTC": "EUR/CAD OTC",
        "GBPCADOTC": "GBP/CAD OTC", "GBPCHFOTC": "GBP/CHF OTC",
        "AUDCADOTC": "AUD/CAD OTC", "AUDCHFOTC": "AUD/CHF OTC",
        "NZDJPYOTC": "NZD/JPY OTC", "NZDCADOTC": "NZD/CAD OTC",
        "CADCHFOTC": "CAD/CHF OTC", "EURCHFOTC": "EUR/CHF OTC",
        "EURNZDOTC": "EUR/NZD OTC", "GBPAUDOTC": "GBP/AUD OTC",
        "GBPNZDOTC": "GBP/NZD OTC",
    }
    symbol = pair_map.get(pair.upper().replace("/","").replace(" ",""), pair)
    await send_message(session, f"⏳ <b>{symbol} ka live signal fetch ho raha hai...</b>")
    data = await fetch_market_data(session, symbol)
    if data:
        await send_message(session, format_signal(data, "M1"))
    else:
        await send_message(session, "❌ Signal fetch nahi hua — thodi der mein try karein")

# ===== AUTO SIGNAL (every 5 minutes) 24/7 =====
async def auto_signal_loop(session):
    pairs_cycle = [
        "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "EUR/JPY",
        "GBP/JPY", "EUR/USD OTC", "GBP/USD OTC", "USD/JPY OTC"
    ]
    idx = 0
    while True:
        await asyncio.sleep(300)  # every 5 minutes
        pair = pairs_cycle[idx % len(pairs_cycle)]
        idx += 1
        log.info(f"Auto signal: {pair}")
        data = await fetch_market_data(session, pair)
        if data and data["conf"] >= 72:
            is_otc = "OTC" in pair
            market_tag = "🌙 OTC Market" if is_otc else "📊 Live Market"
            msg = format_signal(data, "M1")
            msg += f"\n\n🔄 <i>Auto Signal | {market_tag}</i>"
            await send_message(session, msg)

# ===== MAIN =====
async def main():
    log.info("🚀 PO Signal Pro Bot starting...")
    connector = aiohttp.TCPConnector(limit=10)
    async with aiohttp.ClientSession(connector=connector) as session:
        # Send startup message
        await send_message(session, "🚀 <b>PO Signal Pro Bot online hai! 24/7 Active</b>\n\n/signal — EUR/USD signal\n/live — Live pairs\n/otc — OTC pairs\n/topsignal — Best signal\n/help — All commands")
        log.info("Bot started! Listening for commands...")

        # Start auto signal in background
        asyncio.create_task(auto_signal_loop(session))

        # Poll for updates
        offset = None
        while True:
            try:
                offset = await handle_updates(session, offset)
                await asyncio.sleep(1)
            except KeyboardInterrupt:
                break
            except Exception as e:
                log.error(f"Main loop error: {e}")
                await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
