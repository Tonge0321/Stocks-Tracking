from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# --- 修正重點：預先定義好公司名稱，解決 yfinance 抓不到或逾時的問題 ---
NAME_CACHE = {
    '0050.TW': 'Yuanta/P-shares Taiwan Top 50 ETF',
    'VRT': 'Vertiv Holdings Co',
    'SOFI': 'SoFi Technologies Inc',
    'S': 'SentinelOne Inc',
    'RCAT': 'Red Cat Holdings Inc',
    'ONDS': 'Ondas Holdings Inc',
    'NVDA': 'NVIDIA Corp',
    'SMR': 'NuScale Power Corp',
    'NKE': 'Nike Inc',
    'EOSE': 'Eos Energy Enterprises Inc',
    'CRWV': 'CoreWeave Inc'  # 私有/未上市櫃公司手動定義
}

def get_stock_name(ticker_symbol):
    # 1. 優先從 Cache 拿，速度最快且最穩定
    if ticker_symbol in NAME_CACHE:
        return NAME_CACHE[ticker_symbol]
    
    # 2. 如果 Cache 沒有，才嘗試去網路抓 (作為備案)
    try:
        t = yf.Ticker(ticker_symbol)
        name = t.info.get('shortName') or t.info.get('longName') or ticker_symbol
        NAME_CACHE[ticker_symbol] = name # 抓到後存入 Cache
        return name
    except:
        return ticker_symbol

def get_stock_data(tickers):
    if not tickers:
        return []

    try:
        # 批量抓取當日價格數據
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
                # 確保 ticker 在 columns 中
                if ticker not in hist_data.columns.levels[0]:
                    continue
                df = hist_data[ticker]
            
            # 清理空值
            df = df.dropna()
            if df.empty:
                continue

            # 取得基本價格
            current_price = df['Close'].iloc[-1]
            open_price = df['Open'].iloc[0]
            high_price = df['High'].max()
            low_price = df['Low'].min()
            # 簡單使用第一筆 Open 當作昨日收盤參考，或使用 yfinance 的 previousClose
            prev_close = open_price 
            
            change = current_price - prev_close
            pct = (change / prev_close) * 100

            # 取得名稱 (現在會優先讀取我們設定好的 Cache)
            full_name = get_stock_name(ticker)

            # 準備走勢圖數據
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
                'name': full_name,
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
