import yfinance as yf
import requests
import json
import pandas as pd
from datetime import datetime

# 1. 設定您的 Google Apps Script 網址
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwbZ-6VDAPGy6j3GOV64WAdgR5JSPZaYpXqoDr7Y5iLCoCOUYF10RNtywY52gntnsWp/exec"

# 2. 設定股票清單
tickers_list = [
    '0050.TW', 'ONDS', 'RCAT', 'SMR', 'NVDA', 
    'SOFI', 'EOSE', 'S', 'CRWV', 'VRT', 'NKE'
]

def get_robust_data(tickers):
    data_payload = []
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 開始抓取數據 (修正版)...")
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            # 改用 history 抓取過去 5 天，確保能拿到最新的「收盤」數據
            hist = stock.history(period="5d")
            
            if hist.empty:
                print(f"警告: {ticker} 抓不到數據")
                continue

            # 取得最後一筆有效收盤價 (Last Close)
            last_row = hist.iloc[-1]
            # 取得前一筆收盤價 (Previous Close) 用來算漲跌
            prev_row = hist.iloc[-2] if len(hist) > 1 else last_row
            
            price = last_row['Close']
            prev_close = prev_row['Close']
            
            # 計算漲跌
            change = price - prev_close
            change_percent = (change / prev_close) * 100
            
            # 格式化日期 (方便確認是哪一天的價格)
            date_str = last_row.name.strftime('%m-%d')

            stock_info = {
                "symbol": ticker,
                "price": round(price, 2),
                "change": round(change, 2),
                "changePercent": f"{round(change_percent, 2)}%",
                "timestamp": f"{date_str} Close" # 標記這是哪一天的收盤
            }
            
            data_payload.append(stock_info)
            print(f"成功: {ticker:<8} | 日期: {date_str} | 價格: {price:.2f}")
            
        except Exception as e:
            print(f"錯誤: {ticker} | {e}")
            data_payload.append({
                "symbol": ticker,
                "price": "Error",
                "change": 0,
                "changePercent": "0%",
                "timestamp": "N/A"
            })

    return data_payload

def send_to_sheet(data):
    try:
        headers = {'Content-Type': 'application/json'}
        # 設定 timeout 避免卡住
        response = requests.post(WEBHOOK_URL, data=json.dumps(data), headers=headers, timeout=10)
        print(f"\n傳送狀態: {response.status_code}")
        print("回應:", response.text)
    except Exception as e:
        print(f"\n傳送失敗: {e}")

if __name__ == "__main__":
    stock_data = get_robust_data(tickers_list)
    if stock_data:
        send_to_sheet(stock_data)
