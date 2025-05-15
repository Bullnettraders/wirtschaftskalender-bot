import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

posted_events = set()

def get_investing_calendar(for_tomorrow=False):
    url = "https://m.investing.com/economic-calendar/"
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
        date_str = target_date.strftime("%b %d, %Y")

        table = soup.find("table", {"class": "genTbl"})
        if not table:
            print("❌ Tabelle nicht gefunden.")
            return []

        rows = table.find_all("tr", {"class": "js-event-item"})
        for row in rows:
            try:
                date_attr = row.get("data-event-datetime")
                if not date_attr:
                    continue

                event_time_dt = datetime.utcfromtimestamp(int(date_attr))
                event_date_str = event_time_dt.strftime("%b %d, %Y")
                event_time = event_time_dt.strftime("%H:%M")

                if event_date_str != date_str:
                    continue

                country = row.get("data-country", "").lower()
                title_td = row.find("td", class_="event")
                event_name = title_td.text.strip() if title_td else ""
                importance = len(row.find_all("i", {"class": "grayFullBullishIcon"}))

                actual_td = row.find("td", class_="act")
                forecast_td = row.find("td", class_="fore")
                previous_td = row.find("td", class_="prev")

                actual = actual_td.text.strip() if actual_td else ""
                forecast = forecast_td.text.strip() if forecast_td else ""
                previous = previous_td.text.strip() if previous_td else ""

                time_final = event_time if event_time != "00:00" else "—"

                if importance >= 2 and country in ["de", "us"]:
                    events.append({
                        "country": country,
                        "time": time_final,
                        "title": event_name,
                        "actual": actual,
                        "forecast": forecast,
                        "previous": previous,
                        "importance": importance
                    })

            except Exception as e:
                print(f"⚠️ Fehler beim Parsen eines Events: {e}")
                continue

        print(f"🟢 Gefundene wichtige Events: {len(events)}")
        return events

    except Exception as e:
        print(f"❌ Fehler beim Scraping: {e}")
        return []