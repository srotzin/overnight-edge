import os
import csv
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import time
import sys

# Add services directory to path
sys.path.insert(0, '/mnt/user/overnight-edge/services')
from cartoon_gen import generate_cartoon

TELEGRAM_TOKEN = "8640911773:AAEYcQpVsU1eOVKRZaWkJ35K04c5nY8Pvsk"
PUBLIC_CHANNEL = "-1003828989254"
ADMIN_CHAT = "5975342168"

EDGAR_RSS = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=4&company=&dateb=&owner=only&start=0&count=100&output=atom"
EDGAR_8K_RSS = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K&company=&dateb=&owner=include&start=0&count=40&output=atom"

HEADERS = {
    "User-Agent": "OvernightEdgeBot/1.0 (bot@overnightedge.ai)",
    "Accept": "application/atom+xml"
}

def send_telegram(text: str, chat_id: str = PUBLIC_CHANNEL):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=30)
        return True
    except Exception as e:
        print(f"Telegram send failed to {chat_id}: {e}")
        return False

def send_telegram_photo(photo_path: str, caption: str, chat_id: str = PUBLIC_CHANNEL):
    """Send photo with caption to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    
    # Build multipart form data
    with open(photo_path, "rb") as f:
        photo_data = f.read()
    
    body = []
    body.append(f"--{boundary}".encode())
    body.append(b'Content-Disposition: form-data; name="chat_id"')
    body.append(b"")
    body.append(chat_id.encode())
    
    body.append(f"--{boundary}".encode())
    body.append(b'Content-Disposition: form-data; name="caption"')
    body.append(b"")
    body.append(caption.encode())
    
    body.append(f"--{boundary}".encode())
    body.append(b'Content-Disposition: form-data; name="parse_mode"')
    body.append(b"")
    body.append(b"HTML")
    
    body.append(f"--{boundary}".encode())
    body.append(f'Content-Disposition: form-data; name="photo"; filename="{os.path.basename(photo_path)}"'.encode())
    body.append(b"Content-Type: image/png")
    body.append(b"")
    body.append(photo_data)
    
    body.append(f"--{boundary}--".encode())
    
    payload = b"\r\n".join(body)
    
    req = urllib.request.Request(url, data=payload, headers={
        "Content-Type": f"multipart/form-data; boundary={boundary}"
    })
    
    try:
        urllib.request.urlopen(req, timeout=30)
        return True
    except Exception as e:
        print(f"Telegram photo send failed to {chat_id}: {e}")
        return False

def log_signal(date_str, ticker, signal_type, score, s1, s2, s3, notes):
    with open("/mnt/user/overnight-edge/signal_accuracy.csv", "a", newline="") as f:
        csv.writer(f).writerow([date_str, ticker, signal_type, score, s1, s2, s3, notes])

def fetch_edgar_form4():
    """Fetch recent Form 4 filings from EDGAR"""
    try:
        req = urllib.request.Request(EDGAR_RSS, headers=HEADERS)
        resp = urllib.request.urlopen(req, timeout=30)
        xml_data = resp.read()
        
        root = ET.fromstring(xml_data)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        filings = []
        for entry in root.findall('.//atom:entry', ns):
            title = entry.find('atom:title', ns)
            updated = entry.find('atom:updated', ns)
            link = entry.find('atom:link', ns)
            
            if title is not None:
                filings.append({
                    'title': title.text,
                    'updated': updated.text if updated else '',
                    'link': link.get('href') if link else '',
                })
        return filings
    except Exception as e:
        print(f"EDGAR fetch error: {e}")
        return []

def fetch_congressional_trades():
    """Fetch congressional trade disclosures via House Stock Watcher"""
    trades = []
    try:
        house_api = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json"
        req = urllib.request.Request(house_api, headers={"User-Agent": HEADERS["User-Agent"]})
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read())
        
        # Filter recent transactions (last 24 hours)
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        
        for trade in data[:50]:
            try:
                date_str = trade.get('transaction_date', '')
                if date_str:
                    trade_date = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                    if trade_date >= cutoff:
                        amount = trade.get('amount', '')
                        if any(x in amount for x in ['$50,000', '$100,000', '$250,000', '$500,000', '$1,000,000']):
                            trades.append({
                                'representative': trade.get('representative', 'Unknown'),
                                'ticker': trade.get('ticker', 'Unknown'),
                                'transaction': trade.get('transaction', 'Purchase/Sale'),
                                'amount': amount,
                                'date': date_str,
                                'type': 'congressional'
                            })
            except:
                continue
                
    except Exception as e:
        print(f"Congressional trades error: {e}")
    
    return trades

def send_congressional_alert(trade, is_public=True):
    """Send congressional trade alert with cartoon"""
    ticker = trade['ticker']
    rep = trade['representative']
    action = trade['transaction']
    amount = trade['amount']
    date = trade['date']
    
    # Determine politician for cartoon
    politician = "generic"
    rep_lower = rep.lower()
    if any(n in rep_lower for n in ['pelosi', 'nancy']):
        politician = "Nancy Pelosi"
    elif any(n in rep_lower for n in ['trump', 'donald']):
        politician = "Donald Trump"
    elif any(n in rep_lower for n in ['graham', 'lindsey']):
        politician = "Lindsey Graham"
    elif any(n in rep_lower for n in ['gates', 'bill']):
        politician = "Bill Gates"
    elif any(n in rep_lower for n in ['biden', 'joe']):
        politician = "Joe Biden"
    elif any(n in rep_lower for n in ['harris', 'kamala']):
        politician = "Kamala Harris"
    elif any(n in rep_lower for n in ['mcconnell', 'mitch']):
        politician = "Mitch McConnell"
    elif any(n in rep_lower for n in ['schumer', 'chuck']):
        politician = "Chuck Schumer"
    elif any(n in rep_lower for n in ['mcCarthy', 'kevin']):
        politician = "Kevin McCarthy"
    elif any(n in rep_lower for n in ['warren', 'elizabeth']):
        politician = "Elizabeth Warren"
    elif any(n in rep_lower for n in ['soros', 'george']):
        politician = "George Soros"
    
    # Generate cartoon
    cartoon_text = f"{action} {amount} of {ticker}! Filed {date}."
    cartoon_path = generate_cartoon(politician, cartoon_text, f"/mnt/user/overnight-edge/cartoons/alert_{ticker}_{datetime.now().strftime('%H%M%S')}.png")
    
    # Score
    score = 3
    if '$500,000' in amount or '$1,000,000' in amount:
        score = 4
    if '$1,000,001' in amount:
        score = 5
    
    if is_public:
        # Public teaser with cartoon
        caption = f"""🚨 <b>CONGRESSIONAL TRADE ALERT</b>
━━━━━━━━━━━━━━━━━━━━
👤 <b>{rep}</b>
📊 <b>Ticker:</b> {ticker}
📈 <b>Action:</b> {action}
💰 <b>Amount:</b> {amount}
📅 <b>Filed:</b> {date}

Full analysis + confluence scoring →
https://overnight-edge.onrender.com"""
        
        sent = send_telegram_photo(cartoon_path, caption, PUBLIC_CHANNEL)
        print(f"Public cartoon alert for {ticker}: {'OK' if sent else 'FAIL'}")
    else:
        # Full alert for paid subscribers
        caption = f"""🚨 <b>SIGNALSYNTHESIZER — {ticker}</b>
━━━━━━━━━━━━━━━━━━━━
📊 <b>TYPE:</b> congressional
🎯 <b>CONFLUENCE:</b> {score}/5
📈 <b>DIRECTION:</b> {'bullish' if 'Purchase' in action else 'bearish'}
💰 <b>DETAIL:</b> {rep} {action} {amount}
🔗 <b>SOURCES:</b> STOCK Act, House/Senate records
⏰ <b>TIME:</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC
⚠️ NOT FINANCIAL ADVICE"""
        
        sent = send_telegram_photo(cartoon_path, caption, ADMIN_CHAT)
        log_signal(
            datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M'),
            ticker, 'congressional', score,
            'STOCK Act', 'House records', '',
            'delivered' if sent else 'failed'
        )
        print(f"Full cartoon alert for {ticker}: {'OK' if sent else 'FAIL'}")

def main():
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y-%m-%d %H:%M")
    
    print(f"Starting EDGAR/Congressional scan at {date_str}")
    
    # Check Congressional Trades
    print("Fetching congressional trades...")
    congressional = fetch_congressional_trades()
    
    for trade in congressional:
        send_congressional_alert(trade, is_public=True)
        time.sleep(3)
        send_congressional_alert(trade, is_public=False)
        time.sleep(3)
    
    # Check EDGAR Form 4
    print("Fetching EDGAR Form 4 filings...")
    form4 = fetch_edgar_form4()
    
    for filing in form4[:5]:
        # Basic insider filing alert
        title = filing['title']
        import re
        match = re.search(r'4 - ([A-Z]+) - (.+?) \(', title)
        if match:
            ticker = match.group(1)
            insider = match.group(2)
            
            # Generate generic cartoon
            cartoon_text = f"Filed Form 4 for {ticker}. Insider: {insider}."
            cartoon_path = generate_cartoon("generic", cartoon_text, f"/mnt/user/overnight-edge/cartoons/insider_{ticker}_{datetime.now().strftime('%H%M%S')}.png")
            
            caption = f"""📋 <b>INSIDER FILING — {ticker}</b>
━━━━━━━━━━━━━━━━━━━━
👤 <b>Insider:</b> {insider}
📊 <b>Form:</b> SEC Form 4
📅 <b>Filed:</b> {filing['updated'][:10]}

Full analysis + options flow →
https://overnight-edge.onrender.com"""
            
            send_telegram_photo(cartoon_path, caption, PUBLIC_CHANNEL)
            time.sleep(3)
    
    print(f"Scan complete at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    main()
