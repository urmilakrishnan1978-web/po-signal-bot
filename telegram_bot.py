import asyncio
import aiohttp
import logging
from datetime import datetime
from aiohttp import web

BOT_TOKEN = "8595429894:AAFk5nSji-5DazuOontdAd0ncLoGrMnK2gY"
CHANNEL_ID = "-1003586310854"
TWELVE_API = "d4fd55b09ef4424187e10b5b07da0d77"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
log = logging.getLogger(__name__)

LIVE_PAIRS = ["EUR/USD","GBP/USD","USD/JPY","USD/CAD","USD/CHF","AUD/USD","CAD/JPY","EUR/CAD","GBP/JPY","CHF/JPY","EUR/GBP","GBP/AUD","GBP/CHF","EUR/AUD","EUR/CHF","AUD/CAD","AUD/JPY","CAD/CHF","AUD/CHF","GBP/CAD","NZD/USD","EUR/JPY","AUD/NZD","GBP/NZD","EUR/NZD","NZD/JPY","XAU/USD","XAG/USD"]
OTC_PAIRS = ["EUR/USD OTC","GBP/USD OTC","USD/JPY OTC","AUD/USD OTC","USD/CAD OTC","USD/CHF OTC","NZD/USD OTC","EUR/GBP OTC","EUR/JPY OTC","GBP/JPY OTC","EUR/AUD OTC","AUD/JPY OTC","CHF/JPY OTC","EUR/CAD OTC","GBP/CAD OTC","GBP/CHF OTC","AUD/CAD OTC","AUD/CHF OTC","NZD/JPY OTC","NZD/CAD OTC","CAD/CHF OTC","EUR/CHF OTC","EUR/NZD OTC","GBP/AUD OTC","GBP/NZD OTC"]

SYMBOL_MAP = {"EUR/USD":"EUR/USD","GBP/USD":"GBP/USD","USD/JPY":"USD/JPY","AUD/USD":"AUD/USD","USD/CAD":"USD/CAD","USD/CHF":"USD/CHF","CAD/JPY":"CAD/JPY","EUR/CAD":"EUR/CAD","GBP/JPY":"GBP/JPY","CHF/JPY":"CHF/JPY","EUR/GBP":"EUR/GBP","GBP/AUD":"GBP/AUD","GBP/CHF":"GBP/CHF","EUR/AUD":"EUR/AUD","EUR/CHF":"EUR/CHF","AUD/CAD":"AUD/CAD","AUD/JPY":"AUD/JPY","CAD/CHF":"CAD/CHF","AUD/CHF":"AUD/CHF","GBP/CAD":"GBP/CAD","NZD/USD":"NZD/USD","EUR/JPY":"EUR/JPY","AUD/NZD":"AUD/NZD","GBP/NZD":"GBP/NZD","EUR/NZD":"EUR/NZD","NZD/JPY":"NZD/JPY","XAU/USD":"XAU/USD","XAG/USD":"XAG/USD","EUR/USD OTC":"EUR/USD","GBP/USD OTC":"GBP/USD","USD/JPY OTC":"USD/JPY","AUD/USD OTC":"AUD/USD","USD/CAD OTC":"USD/CAD","USD/CHF OTC":"USD/CHF","NZD/USD OTC":"NZD/USD","EUR/GBP OTC":"EUR/GBP","EUR/JPY OTC":"EUR/JPY","GBP/JPY OTC":"GBP/JPY","EUR/AUD OTC":"EUR/AUD","AUD/JPY OTC":"AUD/JPY","CHF/JPY OTC":"CHF/JPY","EUR/CAD OTC":"EUR/CAD","GBP/CAD OTC":"GBP/CAD","GBP/CHF OTC":"GBP/CHF","AUD/CAD OTC":"AUD/CAD","AUD/CHF OTC":"AUD/CHF","NZD/JPY OTC":"NZD/JPY","NZD/CAD OTC":"NZD/CAD","CAD/CHF OTC":"CAD/CHF","EUR/CHF OTC":"EUR/CHF","EUR/NZD OTC":"EUR/NZD","GBP/AUD OTC":"GBP/AUD","GBP/NZD OTC":"GBP/NZD"}

PAIR_CMD = {"EURUSD":"EUR/USD","GBPUSD":"GBP/USD","USDJPY":"USD/JPY","AUDUSD":"AUD/USD","USDCAD":"USD/CAD","USDCHF":"USD/CHF","CADJPY":"CAD/JPY","EURCAD":"EUR/CAD","GBPJPY":"GBP/JPY","CHFJPY":"CHF/JPY","EURGBP":"EUR/GBP","GBPAUD":"GBP/AUD","GBPCHF":"GBP/CHF","EURAUD":"EUR/AUD","EURCHF":"EUR/CHF","AUDCAD":"AUD/CAD","AUDJPY":"AUD/JPY","CADCHF":"CAD/CHF","AUDCHF":"AUD/CHF","GBPCAD":"GBP/CAD","NZDUSD":"NZD/USD","EURJPY":"EUR/JPY","AUDNZD":"AUD/NZD","GBPNZD":"GBP/NZD","EURNZD":"EUR/NZD","NZDJPY":"NZD/JPY","XAUUSD":"XAU/USD","XAGUSD":"XAG/USD","EURUSDOTC":"EUR/USD OTC","GBPUSDOTC":"GBP/USD OTC","USDJPYOTC":"USD/JPY OTC","AUDUSDOTC":"AUD/USD OTC","USDCADOTC":"USD/CAD OTC","USDCHFOTC":"USD/CHF OTC","NZDUSDOTC":"NZD/USD OTC","EURGBPOTC":"EUR/GBP OTC","EURJPYOTC":"EUR/JPY OTC","GBPJPYOTC":"GBP/JPY OTC","EURAUDOTC":"EUR/AUD OTC","AUDJPYOTC":"AUD/JPY OTC","CHFJPYOTC":"CHF/JPY OTC","EURCADOTC":"EUR/CAD OTC","GBPCADOTC":"GBP/CAD OTC","GBPCHFOTC":"GBP/CHF OTC","AUDCADOTC":"AUD/CAD OTC","AUDCHFOTC":"AUD/CHF OTC","NZDJPYOTC":"NZD/JPY OTC","NZDCADOTC":"NZD/CAD OTC","CADCHFOTC":"CAD/CHF OTC","EURCHFOTC":"EUR/CHF OTC","EURNZDOTC":"EUR/NZD OTC","GBPAUDOTC":"GBP/AUD OTC","GBPNZDOTC":"GBP/NZD OTC"}

async def send_msg(session, text, chat_id=None):
    cid = chat_id or CHANNEL_ID
    try:
        async with session.post(f"{BASE_URL}/sendMessage", json={"chat_id":cid,"text":text,"parse_mode":"HTML"}) as r:
            res = await r.json()
            if res.get("ok"): log.info("Sent!")
            else: log.error(f"Err: {res}")
    except Exception as e:
        log.error(f"Send err: {e}")

async def fetch_data(session, symbol):
    sym = SYMBOL_MAP.get(symbol, symbol)
    try:
        async with session.get(f"https://api.twelvedata.com/quote?symbol={sym}&apikey={TWELVE_API}") as r:
            q = await r.json()
        await asyncio.sleep(0.3)
        async with session.get(f"https://api.twelvedata.com/rsi?symbol={sym}&interval=1min&time_period=14&apikey={TWELVE_API}") as r:
            rd = await r.json()
        await asyncio.sleep(0.3)
        async with session.get(f"https://api.twelvedata.com/macd?symbol={sym}&interval=1min&apikey={TWELVE_API}") as r:
            md = await r.json()
        price = float(q.get("close") or q.get("price") or 0)
        prev  = float(q.get("previous_close") or price)
        pct   = float(q.get("percent_change") or 0)
        rsi   = float(rd["values"][0]["rsi"]) if rd.get("values") else 50.0
        macd_v= float(md["values"][0]["macd"]) if md.get("values") else 0.0
        macd_s= float(md["values"][0].get("signal") or md["values"][0].get("signal_line") or 0) if md.get("values") else 0.0
        bull=0; bear=0
        if rsi<40: bull+=3
        elif rsi<45: bull+=2
        elif rsi>65: bear+=3
        elif rsi>60: bear+=2
        if macd_v>macd_s: bull+=2
        else: bear+=2
        if price>prev: bull+=1
        else: bear+=1
        total=bull+bear or 1
        is_up=bull>=bear
        conf=int(60+max(bull,bear)/total*30)
        return {"symbol":symbol,"price":price,"pct":pct,"rsi":round(rsi,1),"macd":round(macd_v,5),"is_up":is_up,"conf":conf,"bull":bull,"bear":bear,"is_otc":"OTC" in symbol,"ok":True}
    except Exception as e:
        log.error(f"Fetch err {symbol}: {e}")
        return {"ok":False}

def fmt(d, tf="M1"):
    now=datetime.now().strftime("%H:%M:%S")
    arrow="⬆️" if d["is_up"] else "⬇️"
    sig="CALL — BUY 🟢" if d["is_up"] else "PUT — SELL 🔴"
    mkt="🌙 OTC Market" if d["is_otc"] else "📊 Live Market"
    c=d["conf"]; bar="█"*(c//10)+"░"*(10-c//10)
    rsi=d["rsi"]; rt="Oversold 📈" if rsi<40 else "Overbought 📉" if rsi>60 else "Neutral ➡️"
    mt="Bullish 📈" if d["macd"]>0 else "Bearish 📉"
    pr=f"{d['price']:.5f}" if d['price']>0 else "N/A"
    pc=f"{d['pct']:+.2f}%" if d['pct']!=0 else ""
    return f"""🔔 <b>PO SIGNAL PRO</b> 🔔
{mkt}
━━━━━━━━━━━━━━━━━━━━
📊 <b>Pair:</b> {d['symbol']}
⏱ <b>Timeframe:</b> {tf}
🕐 <b>Time:</b> {now} IST
💰 <b>Price:</b> {pr} {pc}
━━━━━━━━━━━━━━━━━━━━
{arrow} <b>SIGNAL: {sig}</b>
━━━━━━━━━━━━━━━━━━━━
📈 <b>Confidence: {c}%</b>
{bar}

🔍 <b>Indicators:</b>
• RSI (14): <b>{rsi}</b> — {rt}
• MACD: <b>{d['macd']}</b> — {mt}
• Bull: {d['bull']} pts | Bear: {d['bear']} pts
━━━━━━━━━━━━━━━━━━━━
⚠️ <i>Demo mein test karke trade lein</i>
🤖 @Traders_New_AI_Bot""".strip()

async def do_signal(session, sym, cid):
    await send_msg(session, f"⏳ <b>{sym} signal aa raha hai...</b>", cid)
    d = await fetch_data(session, sym)
    if d["ok"]: await send_msg(session, fmt(d), cid)
    else: await send_msg(session, f"❌ {sym} signal nahi mila — dobara try karein", cid)

async def handle_updates(session, offset=None):
    try:
        params={"timeout":20,"allowed_updates":["message","channel_post"]}
        if offset: params["offset"]=offset
        async with session.get(f"{BASE_URL}/getUpdates", params=params) as r:
            data=await r.json()
        if not data.get("ok"): return offset
        for upd in data.get("result",[]):
            offset=upd["update_id"]+1
            post=upd.get("channel_post") or upd.get("message")
            if not post: continue
            text=post.get("text","").strip()
            cid=str(post["chat"]["id"])
            t=text.lower().split("@")[0].strip()
            log.info(f"CMD:{t}")
            if t=="/signal":
                await do_signal(session,"EUR/USD",cid)
            elif t in ["/start","/help"]:
                await send_msg(session,"""🚀 <b>PO Signal Pro Bot</b> — 24/7 Active ✅
━━━━━━━━━━━━━━━━━━━━
/signal — EUR/USD signal
/topsignal — Best signal
/live — Live pairs list
/otc — OTC pairs list
/pair GBPUSD — GBP/USD signal
/pair EURUSDOTC — EUR/USD OTC signal
/pair XAUUSD — Gold signal
━━━━━━━━━━━━━━━━━━━━
⬆️ CALL=BUY | ⬇️ PUT=SELL
🤖 @Traders_New_AI_Bot""",cid)
            elif t=="/live":
                lines="\n".join([f"• /pair {p.replace('/','').replace(' ','')} — {p}" for p in LIVE_PAIRS])
                await send_msg(session,f"📊 <b>Live Pairs:</b>\n━━━━━━━━━━━━━━━━━━━━\n{lines}\n🤖 @Traders_New_AI_Bot",cid)
            elif t=="/otc":
                lines="\n".join([f"• /pair {p.replace('/','').replace(' ','')} — {p}" for p in OTC_PAIRS])
                await send_msg(session,f"🌙 <b>OTC Pairs:</b>\n━━━━━━━━━━━━━━━━━━━━\n{lines}\n🤖 @Traders_New_AI_Bot",cid)
            elif t=="/topsignal":
                await send_msg(session,"🔍 <b>Best signal dhundh raha hoon...</b>",cid)
                best=None
                for p in ["EUR/USD","GBP/USD","USD/JPY","AUD/USD","EUR/JPY","GBP/JPY"]:
                    d=await fetch_data(session,p)
                    if d["ok"] and (best is None or d["conf"]>best["conf"]): best=d
                    await asyncio.sleep(0.5)
                if best: await send_msg(session,fmt(best)+"\n\n🏆 <b>Highest Confidence!</b>",cid)
                else: await send_msg(session,"❌ Signal nahi mila",cid)
            elif t.startswith("/pair "):
                raw=text[6:].strip()
                key=raw.upper().replace("/","").replace(" ","")
                sym=PAIR_CMD.get(key)
                if sym: await do_signal(session,sym,cid)
                else: await send_msg(session,f"❌ <b>{raw}</b> nahi mila!\nExample: /pair EURUSD\n/pair EURUSDOTC\n\n/live ya /otc se list dekho",cid)
    except Exception as e:
        log.error(f"Upd err: {e}")
    return offset

async def auto_signal(session):
    pairs=["EUR/USD","GBP/USD","USD/JPY","EUR/USD OTC","GBP/USD OTC","USD/JPY OTC","AUD/USD","EUR/JPY"]
    idx=0
    while True:
        await asyncio.sleep(300)
        p=pairs[idx%len(pairs)]; idx+=1
        d=await fetch_data(session,p)
        if d["ok"] and d["conf"]>=73:
            tag="🌙 Auto OTC" if "OTC" in p else "📊 Auto Live"
            await send_msg(session,fmt(d)+f"\n\n🔄 <i>{tag} Signal</i>")

async def keep_alive():
    async def h(req): return web.Response(text="PO Bot Running! ✅")
    app=web.Application()
    app.router.add_get("/",h)
    runner=web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner,"0.0.0.0",10000).start()
    log.info("Keep-alive on port 10000")

async def main():
    log.info("Bot starting...")
    await keep_alive()
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=10)) as session:
        await send_msg(session,"🚀 <b>PO Signal Pro Bot LIVE!</b> 24/7 Active ✅\n/signal — Signal lo\n/topsignal — Best signal\n/live /otc — Pairs list\n/help — Commands")
        asyncio.create_task(auto_signal(session))
        offset=None
        while True:
            try:
                offset=await handle_updates(session,offset)
                await asyncio.sleep(0.5)
            except Exception as e:
                log.error(f"Loop err: {e}")
                await asyncio.sleep(3)

if __name__=="__main__":
    asyncio.run(main())
