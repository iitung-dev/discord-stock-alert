import yfinance as yf
import requests
from datetime import datetime, timedelta
import pandas as pd
import os

# --- CONFIG ---
DISCORD_URL = os.environ.get('DISCORD_WEBHOOK')
STOCKS = ["TSLA", "AAPL", "NVDA", "BTC-USD"]

def send_alert(ticker, drop_percent, scenario, reason_source):
    payload = {
        "embeds": [{
            "title": f"🚨 {scenario} Alert: {ticker}",
            "color": 15158332,
            "description": f"**Drop:** {drop_percent:.2f}%\n**Potential Reason:** {reason_source['title']}",
            "url": reason_source['link'],
            "footer": {"text": f"Scanned at {datetime.now().strftime('%Y-%m-%d %H:%M')}"}
        }]
    }
    requests.post(DISCORD_URL, json=payload)

def get_news(ticker):
    stock = yf.Ticker(ticker)
    news = stock.news
    return news[0] if news else {"title": "No recent news found.", "link": "#"}

def check_logic():
    now = datetime.now()
    is_friday = now.weekday() == 4
    # Check if today is the last business day of the month
    is_month_end = (now + timedelta(days=1)).month != now.month

    for ticker in STOCKS:
        stock = yf.Ticker(ticker)
        
        # Scenario 1: Daily Drop > 5% (Open Market)
        hist_1d = stock.history(period="1d")
        if not hist_1d.empty:
            day_open = hist_1d['Open'].iloc[0]
            day_current = hist_1d['Close'].iloc[0]
            day_drop = ((day_current - day_open) / day_open) * 100
            
            if day_drop <= -5:
                send_alert(ticker, day_drop, "Intraday 5% Drop", get_news(ticker))

        # Scenario 2: Friday Weekly Drop > 10% (Monday Open to Friday Close)
        if is_friday:
            # We fetch 5 days of data to get the Monday of the current week
            hist_5d = stock.history(period="5d")
            if len(hist_5d) >= 5:
                monday_open = hist_5d['Open'].iloc[0]
                friday_close = hist_5d['Close'].iloc[-1]
                weekly_drop = ((friday_close - monday_open) / monday_open) * 100
                
                if weekly_drop <= -10:
                    send_alert(ticker, weekly_drop, "Weekly 10% Drop (Mon-Fri)"),

        # Scenario 3: Monthly Drop > 15%
        if is_month_end:
            hist_1mo = stock.history(period="1mo")
            if len(hist_1mo) > 1:
                month_start = hist_1mo['Open'].iloc[0]
                month_end = hist_1mo['Close'].iloc[-1]
                monthly_drop = ((month_end - month_start) / month_start) * 100
                
                if monthly_drop <= -15:
                    send_alert(ticker, monthly_drop, "Monthly 15% Drop", get_news(ticker))

if __name__ == "__main__":
    check_logic()