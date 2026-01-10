import requests
import json
import yfinance as yf
from datetime import datetime
import time

# ★★★ 請換成您的 Apps Script 網址 ★★★
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwbZ-6VDAPGy6j3GOV64WAdgR5JSPZaYpXqoDr7Y5iLCoCOUYF10RNtywY52gntnsWp/exec"

# 預設清單 (如果 Sheet 裡是空的)
DEFAULT_STOCKS = ['NVDA', 'TSLA', 'AMD', 'PLTR', '0050.TW']

def get_watchlist():
    """從 Google Sheet 取得目前的清單"""
    try:
        # 送出 action=get_watchlist 參數
        url = f"{WEBHOOK_URL}?action=get_watchlist"
        res = requests.get(url)
        data = res.json()
        if data: return data
    except:
        pass
    return DEFAULT_STOCKS

def get_full_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        
        # 1. 取得即時報價 (Fast Info)
        info = stock.fast_info
        price = info.last_price
        prev_close = info.previous_close
        change = price - prev_close
        pct = (change / prev_close) * 100
        
        # 2. 取得當日走勢圖數據 (1天, 5分鐘頻率)
        # 這是為了您的 Chart.js 畫圖用
        hist = stock.history(period="1d", interval="5m")
        
        # 處理圖表數據
        chart_labels = []
        chart_data = []
        
        if not hist.empty:
            # 簡化數據，每隔幾個點取一個，避免 JSON 太大
            subset = hist.iloc[::2] 
            for index, row in subset.iterrows():
                # 格式化時間 HH:MM
                t_str = index.strftime('%H:%M')
                chart_labels.append(t_str)
                chart_data.append(round(row['Close'], 2))
        
        # 3. 模擬/獲取期貨與詳細數據 (配合您的前端欄位)
        data = {
            "id": ticker,
            "name": ticker, # 簡化，用代碼當名稱
            "price": price,
            "change": change,
            "pct": pct,
            "open": round(info.open if info.open else price, 2),
            "high": round(info.day_high if info.day_high else price, 2),
            "low": round(info.day_low if info.day_low else price, 2),
            # 模擬買賣價 (yfinance 免費版無此數據，為了不讓頁面顯示 --)
            "futBid": round(price * 0.999, 2),
            "futAsk": round(price * 1.001, 2),
            
            # 圖表陣列
            "chartLabels": chart_labels,
            "chartData": chart_data,
            "dashedData": [] # 虛線數據留空
        }
        return data

    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

def run_update():
    tickers = get_watchlist()
    print(f"Updating: {tickers}")
    
    final_payload = []
    
    for t in tickers:
        data = get_full_stock_data(t)
        if data:
            final_payload.append(data)
    
    # 上傳到 Google Sheet (type=update_data)
    if final_payload:
        payload = {
            "type": "update_data",
            "data": final_payload
        }
        try:
            requests.post(WEBHOOK_URL, data=json.dumps(payload))
            print("Successfully updated data to Sheet.")
        except Exception as e:
            print(f"Upload failed: {e}")

if __name__ == "__main__":
    run_update()
