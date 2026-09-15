import os
import requests
import yfinance as yf
from google import genai

# 1. 指定監控的股票與 ETF 清單 (上市加 .TW，上櫃加 .TWO)
STOCK_LIST = {
    "0050.TW": "元大台灣50",
    "009816.TW": "009816",
    "6488.TWO": "環球晶",
    "2327.TW": "國巨"
}

def get_multiple_stocks_data(stock_dict):
    """批次抓取清單中所有股票的盤後數據"""
    summary_text = "📊 【多股盤後數據摘要】\n"
    
    for symbol, name in stock_dict.items():
        print(f"正在抓取 {name} ({symbol}) 股市數據...")
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1mo")
        
        if df.empty:
            summary_text += f"\n- {name} ({symbol}): 無法取得數據\n"
            continue
            
        latest_price = round(df['Close'].iloc[-1], 2)
        ma5 = round(df['Close'].tail(5).mean(), 2)
        ma20 = round(df['Close'].tail(20).mean(), 2)
        volume = int(df['Volume'].iloc[-1])
        
        summary_text += (
            f"\n🔹 【{name} ({symbol})】\n"
            f"• 最新收盤價：{latest_price} 元\n"
            f"• 5日均線 (MA5)：{ma5} 元\n"
            f"• 20日均線 (MA20)：{ma20} 元\n"
            f"• 當日成交量：{volume:,} 股\n"
        )
        
    return summary_text

def analyze_with_ai(data_summary, api_key):
    """將指定標的數據傳送給 Gemini 進行整合分析"""
    print("正在將多股數據傳送給 Gemini AI 進行分析...")
    clean_api_key = str(api_key).strip()
    client = genai.Client(api_key=clean_api_key)
    
    prompt = f"""
    你是一位專業的台股與 ETF 投資分析師。以下是指定的 4 檔個股與 ETF 盤後數據：
    
    {data_summary}
    
    請依據上述數據完成簡報分析：
    1. 針對每檔標的（包含 ETF、半導體矽晶圓與被動元件），用 1~2 句話評估其目前技術面趨勢（如相對於 MA5/MA20 的強弱與多空型態）。
    2. 給予整體持股與資金分配的綜合決策建議（條列式說明，文字親切專業，總字數控制在 250 字內）。
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text

def send_line_message(message, line_access_token, line_user_id):
    """發送訊息至 LINE"""
    print("正在發送 LINE 推播訊息...")
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {line_access_token.strip()}"
    }
    payload = {
        "to": line_user_id.strip(),
        "messages": [{"type": "text", "text": message}]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("✅ LINE 訊息發送成功！")
    else:
        print(f"❌ 發送失敗，錯誤碼：{response.status_code}")
        print(response.text)

if __name__ == "__main__":
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN", "").strip()
    LINE_USER_ID = os.getenv("LINE_USER_ID", "").strip()

    if GEMINI_API_KEY and LINE_ACCESS_TOKEN and LINE_USER_ID:
        # 抓取指定標的數據
        data_summary = get_multiple_stocks_data(STOCK_LIST)
        # 讓 AI 進行綜合分析
        ai_report = analyze_with_ai(data_summary, GEMINI_API_KEY)
        
        final_message = f"{data_summary}\n🧠【AI 盤後綜合分析與建議】\n{ai_report}"
        send_line_message(final_message, LINE_ACCESS_TOKEN, LINE_USER_ID)
    else:
        print("💡 提示：未完整偵測到環境變數密鑰，請確認 GEMINI_API_KEY、LINE_ACCESS_TOKEN 與 LINE_USER_ID 是否已設定。")