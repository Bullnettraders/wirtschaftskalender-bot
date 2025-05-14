import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_nasdaq_earnings():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://www.nasdaq.com/market-activity/earnings?date={today}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        events = []
        table = soup.find("table", {"class": "earnings-calendar__table"})

        if not table:
            print("❌ Keine Tabelle gefunden.")
            return []

        rows = table.find_all("tr")
        for row in rows[1:]:  # Skip header row
            cols = row.find_all("td")
            if len(cols) < 5:
                continue

            ticker = cols[0].text.strip()
            company = cols[1].text.strip()
            report_time = cols[2].text.strip()
            eps_estimate = cols[3].text.strip()
            revenue_estimate = cols[4].text.strip()

            events.append({
                "ticker": ticker,
                "company": company,
                "report_time": report_time,
                "eps_estimate": eps_estimate,
                "revenue_estimate": revenue_estimate
            })

        print(f"🟢 Gefundene Nasdaq Earnings: {len(events)}")
        return events

    except Exception as e:
        print(f"❌ Fehler beim Abrufen von Nasdaq Earnings: {e}")
        return []
