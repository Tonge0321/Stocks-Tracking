from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import time

app = Flask(__name__)
CORS(app)  # 允許前端網頁存取

def get_stock_data(tickers):
    if not tickers:
        return []

    # 1. 批量抓取歷史數據 (用於畫圖和計算當日高低)
    # period='1d' (當日), interval='5m' (5分鐘線，兼顧速度與細節)
    try:
        hist_data = yf.download(tickers, period="1d", interval="5m", group_by='ticker', auto_adjust=True, prepost=True, threads=True)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

    results = []

    for ticker in tickers:
        try:
            # 處理單一股票或多股票回傳的 DataFrame 結構差異
            if len(tickers) == 1:
                df = hist_data
            else:
                df = hist_data[ticker]
            
            # 移除空值
            df = df.dropna()

            if df.empty:
                continue

            # 取得基本資訊
            current_price = df['Close'].iloc[-1]
            open_price = df['Open'].iloc[0] # 當日開盤
            high_price = df['High'].max()
            low_price = df['Low'].min()
            
            # 嘗試取得前一日收盤價 (計算漲跌幅用)
            # 這裡簡單用開盤價當作基準，因為 yf.download 有時不含昨收
            # 若要精確昨收需額外呼叫 yf.Ticker(ticker).info，但會拖慢速度
            prev_close = open_price 
            
            change = current_price - prev_close
            pct = (change / prev_close) * 100

            # 準備走勢圖數據 (將時間轉為字串 HH:MM)
            chart_data = []
            chart_labels = []
            dashed_data = [] # 基準線
            
            # 取樣：為了傳輸效率，每隔一點取一個值，或取最後 50 筆
            subset = df.tail(50) 
            for index, row in subset.iterrows():
                chart_data.append(row['Close'])
                dashed_data.append(prev_close)
                # 轉換時間格式
                dt_str = index.strftime('%H:%M')
                chart_labels.append(dt_str)

            # 模擬期貨 Bid/Ask (免費 API 抓不到即時報價，為了介面效果做模擬)
            # 在真實場景這需要付費 API
            spread = current_price * 0.0005 # 萬分之五價差
            bid = current_price - spread
            ask = current_price + spread

            results.append({
                'id': ticker,
                'name': ticker, # 免費版 info 抓取慢，暫用代號
                'price': round(current_price, 2),
                'change': round(change, 2),
                'pct': round(pct, 2),
                'open': round(open_price, 2),
                'low': round(low_price, 2),
                'high': round(high_price, 2),
                'futBid': round(bid, 2),
                'futAsk': round(ask, 2),
                'chartData': chart_data,
                'chartLabels': chart_labels,
                'dashedData': dashed_data
            })

        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            continue

    return results

@app.route('/api/stocks', methods=['POST'])
def get_stocks():
    req_data = request.get_json()
    tickers = req_data.get('tickers', [])
    data = get_stock_data(tickers)
    return jsonify(data)

import os
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)