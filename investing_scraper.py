import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

posted_events = set()

def get_investing_calendar(for_tomorrow=False):
    url = "https://www.investing.com/economic-calendar/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Fehler beim Abrufen: Status {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "lxml")
        events = []

        today = datetime.now()
        target_date = today + timedelta(days=1) if for_tomorrow else today
        target_day = target_date.day
        target_month = target_date.month
        target_year = target_date.year

        table = soup.find("table", {"id": "economicCalendarData"})
        if not table:
            print("❌ Tabelle nicht gefunden.")
            return []

        rows = table.find_all("tr", {"event_timestamp": True})
        for row in rows:
            try:
                event_timestamp = int(row.get("event_timestamp"))
                event_datetime = datetime.utcfromtimestamp(event_timestamp)
                event_datetime_local = event_datetime  # Already adjusted by Investing

                if event_datetime_local.day != target_day or event_datetime_local.month != target_month:
                    continue

                country_td = row.find("td", class_="flagCur")
                country = country_td.get("title", "").lower() if country_td else ""

                event_time = event_datetime_local.strftime("%H:%M")

                event_td = row.find("td", class_="event")
                event_name = event_td.text.strip() if event_td else ""

                actual_td = row.find("td", class_="act")
                forecast_td = row.find("td", class_="fore")
                previous_td = row.find("td", class_="prev")

                actual = actual_td.text.strip() if actual_td else ""
                forecast = forecast_td.text.strip() if forecast_td else ""
                previous = previous_td.text.strip() if previous_td else ""

                importance_td = row.find("td", class_="sentiment")
                importance = 0
                if importance_td:
                    importance = len(importance_td.find_all("i", class_="grayFullBullishIcon"))

                if importance >= 2 and country in ["germany", "united states"]:
                    events.append({
                        "country": country,
                        "time": event_time,
                        "title": event_name,
                        "actual": actual,
                        "forecast": forecast,
                        "previous": previous,
                        "importance": importance
                    })

            except Exception as e:
                print(f"⚠️ Fehler beim Parsen einer Zeile: {e}")
                continue

        print(f"🟢 Gefundene wichtige Events: {len(events)}")
        return events

    except Exception as e:
        print(f"❌ Fehler beim Scraping: {e}")
        return []