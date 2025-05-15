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
        date_str = target_date.strftime("%d.%m.%Y")

        table = soup.find("table", {"class": "genTbl"})
        if not table:
            print("❌ Tabelle nicht gefunden.")
            return []

        rows = table.find_all("tr", {"class": "js-event-item"})
        for row in rows:
            try:
                # Datum check
                date_attr = row.get("data-event-datetime")
                if not date_attr:
                    continue

                event_date = datetime.utcfromtimestamp(int(date_attr)).strftime("%d.%m.%Y")
                event_time = datetime.utcfromtimestamp(int(date_attr)).strftime("%H:%M")

                if event_date != date_str:
                    continue

                # Land
                country_code = row.get("data-country", "").lower()
                if country_code not in ["de", "us"]:
                    continue

                # Wichtigkeit
                importance = int(row.get("data-importance", 0))
                if importance < 2:
                    continue

                # Event Titel
                event_name_td = row.find("td", class_="event")
                event_name = event_name_td.get_text(strip=True) if event_name_td else "Unbekanntes Event"

                # Werte
                actual_td = row.find("td", class_="act")
                forecast_td = row.find("td", class_="fore")

                actual = actual_td.get_text(strip=True) if actual_td else ""
                forecast = forecast_td.get_text(strip=True) if forecast_td else ""

                events.append({
                    "country": country_code,
                    "time": event_time if event_time else "—",
                    "title": event_name,
                    "actual": actual,
                    "forecast": forecast
                })

            except Exception as e:
                print(f"⚠️ Fehler beim Parsen eines Events: {e}")
                continue

        print(f"🟢 Gefundene wichtige Events: {len(events)}")
        return events

    except Exception as e:
        print(f"❌ Fehler beim Scraping: {e}")
        return []