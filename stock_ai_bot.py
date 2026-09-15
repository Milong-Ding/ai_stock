import os
import requests
import pandas as pd
import yfinance as yf
from google import genai

# 1. 抓取股票盤後數據
def get_stock_data(symbol="2330.TW"):
    print(f"正在抓取 {symbol} 股市數據...")
    stock = yf.Ticker(symbol)
    df = stock.history(period="1mo")
    
    if df.empty:
        return "無法取得股票資料，請檢查股票代號。"
        
    latest_price = round(df['Close'].iloc[-1], 2)
    ma5 = round(df['Close'].rolling(5).mean().iloc[-1], 2)
    ma20 = round(df['Close'].rolling(20).mean().iloc[-1], 2)
    monthly_change = round(((latest_price - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100, 2)
    
    summary = f"""📊【標的代號】：{symbol}
【最新收盤價】：{latest_price} 元
【5日均線 (MA5)】：{ma5} 元
【20日均線 (MA20)】：{ma20} 元
【近一個月漲跌幅】：{monthly_change}%"""
    return summary

# 2. 呼叫 Gemini AI 分析
def analyze_with_ai(stock_info, api_key):
    print("正在將數據傳送給 Gemini AI 進行分析...")
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    你是一位專業的股市財務與趨勢分析師。請根據以下股票數據進行簡短分析：
    {stock_info}
    
    請提供：
    1. 短期技術面評估（例如：目前股價相對於 5日/20日 均線的位置與型態）。
    2. 給予投資人的決策參考建議（不超過 120 字，條列式說明，文字親切專業）。
    """
    
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )
    return response.text

# 3. 發送 LINE 訊息
def send_line_message(message, access_token, user_id):
    print("正在發送訊息至 LINE...")
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": message}]
    }
    res = requests.post(url, json=payload, headers=headers)
    if res.status_code == 200:
        print("✅ 訊息已成功推送到 LINE！")
    else:
        print(f"❌ 發送失敗，錯誤碼：{res.status_code}, 內容：{res.text}")

if __name__ == "__main__":
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN", "").strip()
    LINE_USER_ID = os.getenv("LINE_USER_ID", "").strip()

    # 嚴謹檢查：必須三個 Key 都有值才執行主程式
    if GEMINI_API_KEY and LINE_ACCESS_TOKEN and LINE_USER_ID:
        data_summary = get_stock_data("2330.TW")
        ai_report = analyze_with_ai(data_summary, GEMINI_API_KEY)
        final_message = f"{data_summary}\n\n🧠【AI 趨勢與決策建議】\n{ai_report}"
        send_line_message(final_message, LINE_ACCESS_TOKEN, LINE_USER_ID)
    else:
        print("💡 提示：未完整偵測到環境變數密鑰，請確認 GEMINI_API_KEY、LINE_ACCESS_TOKEN 與 LINE_USER_ID 是否已設定。")