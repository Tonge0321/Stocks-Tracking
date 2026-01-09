from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# 用來暫存公司名稱，避免每次都重新抓取導致速度變慢
NAME_CACHE = {
    '0050.TW': 'Yuanta/P-shares Taiwan Top 50 ETF', # 台股有時抓不到英文名，可手動預設
}

def get_stock_name(ticker_symbol):
    # 如果快取裡已經有，直接回傳
    if ticker_symbol in NAME_CACHE:
        return NAME_CACHE[ticker_symbol]
    
    # 嘗試抓取全名
    try:
        t = yf.Ticker(ticker_symbol)
        # 抓取 shortName (公司簡稱) 或 longName (全名)
        name = t.info.get('shortName') or t.info.get('longName') or ticker_symbol
        NAME_CACHE[ticker_symbol] = name
        return name
    except:
        return ticker_symbol

def get_stock_data(tickers):
    if not tickers:
        return []

    # 1. 批量抓取價格數據
    try:
        hist_data = yf.download(tickers, period="1d", interval="5m", group_by='ticker', auto_adjust=True, prepost=True, threads=True)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

    results = []

    for ticker in tickers:
        try:
            # 處理單一/多股票 DataFrame 結構差異
            if len(tickers) == 1:
                df = hist_data
            else:
                df = hist_data[ticker]
            
            df = df.dropna()
            if df.empty:
                continue

            # 取得價格資訊
            current_price = df['Close'].iloc[-1]
            open_price = df['Open'].iloc[0]
            high_price = df['High'].max()
            low_price = df['Low'].min()
            prev_close = open_price # 簡化計算
            
            change = current_price - prev_close
            pct = (change / prev_close) * 100

            # 取得公司全名 (使用快取功能)
            full_name = get_stock_name(ticker)

            # 準備圖表數據
            chart_data = []
            chart_labels = []
            dashed_data = []
            subset = df.tail(50)
            for index, row in subset.iterrows():
                chart_data.append(row['Close'])
                dashed_data.append(prev_close)
                dt_str = index.strftime('%H:%M')
                chart_labels.append(dt_str)

            # 模擬期貨價差
            spread = current_price * 0.0005
            
            results.append({
                'id': ticker,
                'name': full_name,  # 這裡是全名
                'price': round(current_price, 2),
                'change': round(change, 2),
                'pct': round(pct, 2),
                'open': round(open_price, 2),
                'low': round(low_price, 2),
                'high': round(high_price, 2),
                'futBid': round(current_price - spread, 2),
                'futAsk': round(current_price + spread, 2),
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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
