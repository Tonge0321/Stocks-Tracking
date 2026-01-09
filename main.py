import requests
import json
import yfinance as yf
from datetime import datetime

# 您的 Apps Script 網址
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwbZ-6VDAPGy6j3GOV64WAdgR5JSPZaYpXqoDr7Y5iLCoCOUYF10RNtywY52gntnsWp/exec"

def get_stock_list():
    """從 Google Sheet 取得目前的股票清單"""
    try:
        print("正在讀取股票清單...")
        response = requests.get(WEBHOOK_URL)
        data = response.json()
        # 提取 symbol
        stock_list = [item['symbol'] for item in data]
        print(f"目前清單: {stock_list}")
        return stock_list
    except Exception as e:
        print(f"讀取清單失敗: {e}")
        return []

def get_market_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        # 嘗試使用 fast_info
        try:
            price = stock.fast_info.last_price
            prev_close = stock.fast_info.previous_close
        except:
            # 如果失敗，回退到 history
            hist = stock.history(period="2d")
            if hist.empty: return None
            price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[0] if len(hist) > 1 else price

        change_pct = ((price - prev_close) / prev_close) * 100
        
        # 盤後價模擬 (yfinance 免費版盤後數據不穩定，此為備用邏輯)
        futures = "-"
        if not ticker.endswith('.TW'):
             futures = f"{price:.2f}" # 美股暫顯示收盤價

        return {
            "symbol": ticker,
            "price": f"{price:.2f}",
            "futuresPrice": futures,
            "changePercent": f"{change_pct:.2f}%",
            "timestamp": datetime.now().strftime("%H:%M")
        }
    except Exception as e:
        print(f"抓取 {ticker} 失敗: {e}")
        return None

def run_update():
    # 1. 先從 Sheet 取得名單
    target_stocks = get_stock_list()
    
    if not target_stocks:
        print("沒有股票需要更新")
        return

    payload = []
    # 2. 逐一抓取價格
    for symbol in target_stocks:
        data = get_market_data(symbol)
        if data:
            payload.append(data)
            
    # 3. 回傳更新數據 (Action: update_prices)
    if payload:
        print(f"正在更新 {len(payload)} 筆股價...")
        try:
            final_data = {"action": "update_prices", "updates": payload}
            requests.post(WEBHOOK_URL, data=json.dumps(final_data))
            print("更新完成！")
        except Exception as e:
            print(f"上傳失敗: {e}")

if __name__ == "__main__":
    run_update()
