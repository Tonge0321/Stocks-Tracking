import requests
import json
import random
from datetime import datetime

# ---------------------------------------------------------
# ★★★ 設定區：請在這裡「新增」或「刪除」股票代碼 ★★★
# 格式：'代碼' (美股直接打代碼，台股加 .TW)
MY_STOCKS = [
    'NVDA',     # 輝達
    'TSLA',     # 特斯拉
    'AAPL',     # 蘋果
    'AMD',      # 超微
    'PLTR',     # Palantir
    '0050.TW',  # 台灣50
    '2330.TW',  # 台積電
    'EOSE',     # 您關注的股票
    'SOFI'      
]
# ---------------------------------------------------------

# 您的 Google Apps Script 網址
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwbZ-6VDAPGy6j3GOV64WAdgR5JSPZaYpXqoDr7Y5iLCoCOUYF10RNtywY52gntnsWp/exec"

def get_price_data(ticker):
    """
    這是一個模擬真實數據的函數。
    因為在 GitHub 上抓即時股價比較嚴格，我們先用模擬數據確保流程暢通。
    如果您有 Yahoo Finance 套件 (yfinance)，可以在這裡替換。
    """
    # 這裡生成一些模擬的波動，讓您看到圖表和數字會跳動
    base_price = 100.00
    if ticker == 'NVDA': base_price = 185.00
    if ticker == 'TSLA': base_price = 420.00
    if ticker == '0050.TW': base_price = 198.00
    
    noise = random.uniform(-2, 2)
    price = base_price + noise
    futures = price * (1 + random.uniform(-0.01, 0.01))
    pct = random.uniform(-3, 3)
    
    return {
        "regular": round(price, 2),
        "futures": round(futures, 2),
        "pct": round(pct, 2)
    }

def run_update():
    print(f"準備更新 {len(MY_STOCKS)} 檔股票...")
    payload = []
    
    for symbol in MY_STOCKS:
        # 1. 獲取數據
        data = get_price_data(symbol)
        
        # 2. 打包資料
        payload.append({
            "symbol": symbol,
            "price": f"{data['regular']:.2f}",
            "futuresPrice": f"{data['futures']:.2f}",
            "changePercent": f"{data['pct']}%",
            "timestamp": datetime.now().strftime("%H:%M")
        })
        
    print("正在上傳數據至 Google Sheet...")
    
    try:
        response = requests.post(
            WEBHOOK_URL, 
            data=json.dumps(payload), 
            headers={'Content-Type': 'application/json'}
        )
        print(f"上傳結果: {response.text}")
        
    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    run_update()
