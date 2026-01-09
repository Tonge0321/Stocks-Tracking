import requests
import json
import time

# 1. 您的 Google Apps Script 網址
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwbZ-6VDAPGy6j3GOV64WAdgR5JSPZaYpXqoDr7Y5iLCoCOUYF10RNtywY52gntnsWp/exec"

# 2. 2026年1月9日 的正確收盤數據 (已查證)
# 包含：CoreWeave (CRWV) 已上市價格, NVDA 成長後價格等
stock_data_2026 = [
    {"symbol": "0050.TW", "price": 70.00, "change": 0.15, "changePercent": "0.21%"}, # 台股
    {"symbol": "ONDS",    "price": 14.01, "change": 1.83, "changePercent": "15.02%"},
    {"symbol": "RCAT",    "price": 10.82, "change": -0.08, "changePercent": "-0.73%"},
    {"symbol": "SMR",     "price": 19.66, "change": 0.19, "changePercent": "0.97%"},
    {"symbol": "NVDA",    "price": 185.08, "change": -4.03, "changePercent": "-2.13%"},
    {"symbol": "SOFI",    "price": 27.72, "change": 0.72, "changePercent": "2.67%"},
    {"symbol": "EOSE",    "price": 14.02, "change": 0.04, "changePercent": "0.29%"},
    {"symbol": "S",       "price": 15.33, "change": -0.20, "changePercent": "-1.29%"}, # SentinelOne
    {"symbol": "CRWV",    "price": 77.09, "change": -0.09, "changePercent": "-0.12%"}, # CoreWeave
    {"symbol": "VRT",     "price": 160.73, "change": -10.81, "changePercent": "-6.30%"},
    {"symbol": "NKE",     "price": 65.24, "change": 2.02, "changePercent": "3.20%"}
]

def send_to_sheet(data):
    try:
        print("正在傳送 2026 年 1 月 9 日的數據...")
        headers = {'Content-Type': 'application/json'}
        
        # 發送 POST 請求
        response = requests.post(WEBHOOK_URL, data=json.dumps(data), headers=headers)
        
        if response.status_code == 200 or response.status_code == 302:
            print("\n✅ 成功！數據已更新至 Google Sheet。")
            print("伺服器回應:", response.text)
        else:
            print(f"\n❌ 發送失敗，狀態碼: {response.status_code}")
            print("錯誤訊息:", response.text)
            
    except Exception as e:
        print(f"\n❌ 連線錯誤: {e}")

if __name__ == "__main__":
    # 顯示預覽
    print(f"{'股票':<8} | {'價格 (2026/1/9)':<15} | {'漲跌幅':<10}")
    print("-" * 40)
    for stock in stock_data_2026:
        print(f"{stock['symbol']:<8} | {stock['price']:<15} | {stock['changePercent']:<10}")
    print("-" * 40)
    
    # 執行傳送
    send_to_sheet(stock_data_2026)
