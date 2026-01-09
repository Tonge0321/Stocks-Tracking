import requests
import json
from datetime import datetime

# 1. 您的 Google Apps Script 網址
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwbZ-6VDAPGy6j3GOV64WAdgR5JSPZaYpXqoDr7Y5iLCoCOUYF10RNtywY52gntnsWp/exec"

# 2. 2026/1/9 完整股票數據庫
stock_db = {
    '0050.TW': { 'regular': 70.00,  'futures': 69.85,  'change_pct': 0.21 },
    'ONDS':    { 'regular': 14.01,  'futures': 14.05,  'change_pct': 15.02 },
    'RCAT':    { 'regular': 10.82,  'futures': 10.75,  'change_pct': -0.73 },
    'SMR':     { 'regular': 19.66,  'futures': 19.80,  'change_pct': 0.97 },
    'NVDA':    { 'regular': 185.08, 'futures': 184.90, 'change_pct': -2.13 },
    'SOFI':    { 'regular': 27.72,  'futures': 27.85,  'change_pct': 2.67 },
    'EOSE':    { 'regular': 14.02,  'futures': 14.00,  'change_pct': 0.29 },
    'S':       { 'regular': 15.33,  'futures': 15.40,  'change_pct': -1.29 },
    'CRWV':    { 'regular': 77.09,  'futures': 76.80,  'change_pct': -0.12 },
    'VRT':     { 'regular': 160.73, 'futures': 161.50, 'change_pct': -6.30 },
    'NKE':     { 'regular': 65.24,  'futures': 65.30,  'change_pct': 3.20 }
}

tickers_list = ['0050.TW', 'ONDS', 'RCAT', 'SMR', 'NVDA', 'SOFI', 'EOSE', 'S', 'CRWV', 'VRT', 'NKE']

def run_full_update():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 開始生成數據...")
    
    payload = []
    for ticker in tickers_list:
        stock = stock_db.get(ticker)
        if stock:
            payload.append({
                "symbol": ticker,
                "price": f"{stock['regular']:.2f}",
                "futuresPrice": f"{stock['futures']:.2f}",
                "changePercent": f"{stock['change_pct']}%",
                "timestamp": "1/9 Close"
            })
            
    print(f"準備發送 {len(payload)} 筆股票資料至 Google Sheet...")
    
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(WEBHOOK_URL, data=json.dumps(payload), headers=headers)
        
        print(f"伺服器狀態碼: {response.status_code}")
        print(f"伺服器回應: {response.text}")
        
        if "Success" in response.text or "Updated" in response.text:
            print("\n✅ 更新成功！")
        else:
            print("\n❌ 更新失敗")
            
    except Exception as e:
        print(f"\n❌ 連線發生錯誤: {e}")

if __name__ == "__main__":
    run_full_update()
