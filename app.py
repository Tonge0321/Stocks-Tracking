import yfinance as yf
import requests
import json
from datetime import datetime

# 1. 設定您的 Google Apps Script 網址
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwbZ-6VDAPGy6j3GOV64WAdgR5JSPZaYpXqoDr7Y5iLCoCOUYF10RNtywY52gntnsWp/exec"

# 2. 設定股票清單 (依照您要求的排序)
tickers_list = [
    '0050.TW', 'ONDS', 'RCAT', 'SMR', 'NVDA', 
    'SOFI', 'EOSE', 'S', 'CRWV', 'VRT', 'NKE'
]

def get_stock_data(tickers):
    data_payload = []
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 開始抓取數據...")
    
    for ticker in tickers:
        try:
            # 抓取股票資訊
            stock = yf.Ticker(ticker)
            # 使用 fast_info 獲取最新即時價格 (比 history 更快且即時)
            price = stock.fast_info.last_price
            prev_close = stock.fast_info.previous_close
            
            # 計算漲跌幅
            change = price - prev_close
            change_percent = (change / prev_close) * 100
            
            # 獲取其他資訊 (成交量, 市值等，視需要可自行調整)
            # 注意: 不同市場(台股/美股)的欄位可能會有微小差異，這裡取通用欄位
            
            # 建立單一股票的數據物件
            stock_info = {
                "symbol": ticker,
                "price": round(price, 2),
                "change": round(change, 2),
                "changePercent": round(change_percent, 2) + "%",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            data_payload.append(stock_info)
            print(f"成功抓取: {ticker} | 價格: {price:.2f}")
            
        except Exception as e:
            print(f"抓取失敗: {ticker} | 錯誤: {e}")
            # 即使失敗也放入一個空數據或錯誤標記，保持順序
            data_payload.append({
                "symbol": ticker,
                "price": "Error",
                "change": 0,
                "changePercent": "0%"
            })

    return data_payload

def send_to_sheet(data):
    try:
        # 將數據轉換為 JSON 字串
        headers = {'Content-Type': 'application/json'}
        response = requests.post(WEBHOOK_URL, data=json.dumps(data), headers=headers)
        
        if response.status_code == 200:
            print("\n數據已成功發送至 Google Script！")
            print("伺服器回應:", response.text)
        else:
            print(f"\n發送失敗，狀態碼: {response.status_code}")
            print("回應內容:", response.text)
            
    except Exception as e:
        print(f"\n發送過程中發生錯誤: {e}")

if __name__ == "__main__":
    # 執行主程序
    stock_data = get_stock_data(tickers_list)
    
    # 檢查是否有抓到數據
    if stock_data:
        send_to_sheet(stock_data)
    else:
        print("未獲取任何數據，停止發送。")
