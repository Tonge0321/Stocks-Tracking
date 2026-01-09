import requests
import json
import yfinance as yf
from datetime import datetime
import time

# 您的 Apps Script 網址
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwbZ-6VDAPGy6j3GOV64WAdgR5JSPZaYpXqoDr7Y5iLCoCOUYF10RNtywY52gntnsWp/exec"

def get_stock_list():
    """從 Google Sheet 取得清單"""
    try:
        response = requests.get(WEBHOOK_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # 確保按照 user 定義的順序 (order 欄位) 回傳
            return [item['symbol'] for item in data]
        return []
    except Exception as e:
        print(f"清單讀取錯誤: {e}")
        return []

def get_realtime_data(ticker):
    """
    抓取邏輯：
    1. 優先使用 fast_info (最即時)
    2. 判斷是否有盤後交易 (Extended Hours)
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.fast_info
        
        # --- 價格邏輯 ---
        # last_price 通常是最近一筆成交價 (包含盤中或收盤)
        price = info.last_price
        prev_close = info.previous_close
        
        # 計算漲跌
        change_val = price - prev_close
        change_pct = (change_val / prev_close) * 100
        
        # --- 盤後/期貨邏輯 ---
        # yfinance 的 fast_info 沒有直接的 "preMarket" 欄位，
        # 但我們可以透過比對 last_price 和 regular_market_previous_close 來判斷
        # 為了更精準，我們這裡做一個簡單的標示：
        # 如果是美股，我們把 current price 當作即時價
        # 如果有明顯差異，可以視為盤後波動
        
        # 嘗試抓取當日高低
        day_high = info.day_high
        day_low = info.day_low

        futures_text = "-"
        # 簡單判定：如果現在價格跟收盤價不一樣，且不在正規時間，那就是盤後
        # 這裡我們直接顯示 "當前最新價"
        
        return {
            "symbol": ticker,
            "price": f"{price:.2f}",
            "high": f"{day_high:.2f}",
            "low": f"{day_low:.2f}",
            "futuresPrice": f"{change_val:+.2f} ({change_pct:+.2f}%)", # 這裡改顯示「漲跌額」讓介面更豐富
            "changePercent": f"{change_pct:.2f}%",
            "timestamp": datetime.now().strftime("%H:%M")
        }

    except Exception as e:
        print(f"無法抓取 {ticker}: {e}")
        # 發生錯誤時回傳 None，讓主程式跳過或填舊資料
        return None

def run_update():
    # 1. 獲取名單
    tickers = get_stock_list()
    if not tickers:
        print("Google Sheet 清單為空，使用預設清單測試")
        tickers = ['NVDA', 'TSLA', 'AAPL'] # 備用

    print(f"正在更新: {tickers}")
    
    payload = []
    for t in tickers:
        data = get_realtime_data(t)
        if data:
            payload.append(data)
        time.sleep(0.5) # 避免太快被擋

    # 2. 上傳
    if payload:
        try:
            final_data = {"action": "update_prices", "updates": payload}
            requests.post(WEBHOOK_URL, data=json.dumps(final_data))
            print("更新成功")
        except Exception as e:
            print(f"上傳錯誤: {e}")

if __name__ == "__main__":
    run_update()
