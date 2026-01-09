import requests
import json
from datetime import datetime

# 您的 Google Apps Script 網址
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwbZ-6VDAPGy6j3GOV64WAdgR5JSPZaYpXqoDr7Y5iLCoCOUYF10RNtywY52gntnsWp/exec"

# 模擬股票數據 (後續可自行修改或加入爬蟲)
stock_db = {
    '0050.TW': { 'regular': 198.50, 'futures': 198.00, 'pct': 0.85 },
    'NVDA':    { 'regular': 185.08, 'futures': 184.90, 'pct': -2.13 },
    'TSLA':    { 'regular': 420.69, 'futures': 425.00, 'pct': 5.20 },
    'AAPL':    { 'regular': 230.15, 'futures': 230.10, 'pct': -0.50 }
}

def run_update():
    print("Preparing data...")
    payload = []
    
    for symbol, data in stock_db.items():
        payload.append({
            "symbol": symbol,
            "price": f"{data['regular']:.2f}",
            "futuresPrice": f"{data['futures']:.2f}",
            "changePercent": f"{data['pct']}%",
            "timestamp": datetime.now().strftime("%H:%M")
        })
    
    print(f"Sending {len(payload)} stocks to Google Sheet...")
    
    try:
        # 發送 POST 請求
        response = requests.post(
            WEBHOOK_URL, 
            data=json.dumps(payload), 
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_update()
