import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def get_nasdaq_earnings(for_tomorrow=False):
    target_date = datetime.now()
    if for_tomorrow:
        target_date += timedelta(days=1)
    date_str = target_date.strftime("%Y-%m-%d")

    url = f"https://www.nasdaq.com/market-activity/earnings?date={date_str}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Fehler beim Abrufen: Status {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        earnings_section = soup.find('div', class_="earnings-calendar__table-wrapper")
        if not earnings_section:
            print("❌ Earnings Bereich nicht gefunden.")
            return []

        table = earnings_section.find("table")
        if not table:
            print("❌ Tabelle nicht gefunden.")
            return []

        events = []
        rows = table.find_all("tr")[1:]  # Skip header

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 5:
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
        print(f"❌ Fehler beim Abrufen der Nasdaq Earnings: {e}")
        return []
