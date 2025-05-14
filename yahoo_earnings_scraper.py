import requests
from datetime import datetime

def get_yahoo_earnings():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://query1.finance.yahoo.com/v7/finance/calendar/earnings?day={today}"

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        data = response.json()

        events = []
        earnings = data.get("finance", {}).get("result", [])
        if not earnings:
            return events

        for item in earnings:
            ticker = item.get("ticker", "N/A")
            company = item.get("companyshortname", "N/A")
            eps_estimate = item.get("epsestimate", "N/A")
            revenue_estimate = item.get("revenueestimate", "N/A")
            starttime = item.get("startdatetime", "")

            if starttime:
                time = datetime.fromtimestamp(starttime).strftime("%H:%M")
            else:
                time = "n/a"

            events.append({
                "ticker": ticker,
                "company": company,
                "eps_estimate": eps_estimate,
                "revenue_estimate": revenue_estimate,
                "time": time
            })

        print(f"🟢 Gefundene Earnings heute: {len(events)}")
        return events

    except Exception as e:
        print(f"❌ Fehler beim Abrufen der Yahoo Earnings: {e}")
        return []
