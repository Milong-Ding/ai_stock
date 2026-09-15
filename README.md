# 📈 台股 AI 自動化盤後分析與 LINE 推播機器人

本專案使用 Python 自動抓取每日台股盤後數據，結合 Google Gemini AI 進行技術面與決策分析，並透過 GitHub Actions 實現每日定時（14:30）自動執行，將即時報告推送至個人 LINE 帳號。

---

## 🛠️ 技術架構與使用套件

* **程式語言**：Python 3.11+
* **數據來源**：`yfinance` / `pandas`
* **AI 分析模型**：Google Gemini API (`gemini-2.5-flash` via `google-genai`)
* **通訊推播**：LINE Messaging API
* **自動化部署**：GitHub Actions (`cron` 定時觸發)

---

## 🚀 專案檔案結構

```text
ai_stock/
├── .github/
│   └── workflows/
│       └── daily_stock.yml   # GitHub Actions 自動排程設定檔
├── stock_ai_bot.py           # 主程式（抓取數據、AI 分析、LINE 推播）
├── README.md                 # 專案說明文件
└── .gitignore                # Git 忽略檔案設定