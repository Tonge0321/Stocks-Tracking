import requests
import json
from datetime import datetime

# 1. 您的 Google Apps Script 網址
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwbZ-6VDAPGy6j3GOV64WAdgR5JSPZaYpXqoDr7Y5iLCoCOUYF10RNtywY52gntnsWp/exec"

# 2026 年 1 月 9 日 (週五) 收盤後情境
# regular: 下午 4:00 收盤價 (主顯示)
# futures: 盤後交易/期貨價格 (下方小字顯示)
stock_db = {
    '0050.TW': { 
        'regular': 70.00,  # 台股收盤
        'futures': 69.85,  # 台指期夜盤 (稍微折價)
        'change_pct': 0.21 
    },
    'ONDS': { 
        'regular': 14.01, 
        'futures': 14.05,  # 盤後微升
        'change_pct': 15.02 
    },
    'RCAT': { 
        'regular': 10.82, 
        'futures': 10.75,  # 盤後微跌
        'change_pct': -0.73 
    },
    'SMR': { 
        'regular': 19.66, 
        'futures': 19.80, 
        'change_pct': 0.97 
    },
    'NVDA': { 
        'regular': 185.08, # 收盤鎖定 185.08
        'futures': 184.90, # 盤後續跌，顯示市場情緒偏弱
        'change_pct': -2.13 
    },
    'SOFI': { 
        'regular': 27.72, 
        'futures': 27.85, 
        'change_pct': 2.67 
    },
    'EOSE': { 
        'regular': 14.02, 
        'futures': 14.00, 
        'change_pct': 0.29 
    },
    'S': { 
        'regular': 15.33, 
        'futures': 15.40, 
        'change_pct': -1.29 
    },
    'CRWV': { 
        'regular': 77.09, 
        'futures': 76.80, # CoreWeave 盤後微幅震盪
        'change_pct': -0.12 
    },
    'VRT': { 
        'regular': 160.73, # Vertiv 當日大跌收盤
        'futures': 161.50, # 盤後有人逢低買進，價格略高於收盤
        'change_pct': -6.30 
    },
    'NKE': { 
        'regular': 65.24, 
        'futures': 65.30, 
        'change_pct': 3.20 
    }
}

# 排序清單
tickers_list = ['0050.TW', 'ONDS', 'RCAT', 'SMR', 'NVDA', 'SOFI', 'EOSE', 'S', 'CRWV', 'VRT', 'NKE']

def generate_separated_data(tickers):
    data_payload = []
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 正在生成數據 (主價格/期貨價格 分離模式)...")
    print("-" * 55)
    print(f"{'代碼':<8} | {'主價格 (收盤)':<12} | {'盤後/期貨':<12} | {'狀態'}")
    print("-" * 55)

    for ticker in tickers:
        stock = stock_db.get(ticker)
        if not stock:
            continue
            
        # 建立數據封包
        # 我們刻意將兩個價格分開命名，讓前端可以分開顯示
        stock_info = {
            "symbol": ticker,
            "price": f"{stock['regular']:.2f}",      # 主顯示：收盤價
            "futuresPrice": f"{stock['futures']:.2f}", # 副顯示：期貨/盤後
            "changePercent": f"{stock['change_pct']}%",
            "timestamp": "Market Closed"
        }
        
        data_payload.append(stock_info)
        
        # 在終端機顯示檢查
        print(f"{ticker:<8} | {stock['regular']:<12.2f} | {stock['futures']:<12.2f} | ✅ OK")

    return data_payload

def send_to_sheet(data):    
    print(f"準備發送 {len(data)} 筆資料...") # <--- 加入這行檢查
    # ... 其餘程式碼
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(WEBHOOK_URL, data=json.dumps(data), headers=headers)
        
        if response.status_code == 200 or response.status_code == 302:
            print("-" * 55)
            print("數據發送成功！Google Sheet 應顯示：")
            print("1. 大字顯示主價格 (收盤價)")
            print("2. 下方小字顯示期貨價格")
        else:
            print(f"發送失敗: {response.text}")
    except Exception as e:
        print(f"連線錯誤: {e}")

if __name__ == "__main__":
    payload = generate_separated_data(tickers_list)
    send_to_sheet(payload)

