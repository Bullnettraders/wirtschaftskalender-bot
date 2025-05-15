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
            print(f"❌ Fehler beim Abrufen: {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find("table", {"class": "genTbl"})

        if not table:
            print("❌ Keine Tabelle gefunden.")
            return []

        rows = table.find_all("tr", {"class": "js-event-item"})

        today = datetime.now()
        target_date = today if not for_tomorrow else today + timedelta(days=1)
        date_today = target_date.strftime("%Y-%m-%d")

        events = []

        for row in rows:
            try:
                date_attr = row.get("data-event-datetime")
                if not date_attr:
                    continue

                event_time_obj = datetime.strptime(date_attr, "%Y/%m/%d %H:%M:%S")
                event_date = event_time_obj.strftime("%Y-%m-%d")
                event_time = event_time_obj.strftime("%H:%M")

                if event_date != date_today:
                    continue

                country = row.get("data-country", "").lower()
                importance = int(row.get("data-importance", 0))

                if importance < 2 or country not in ["de", "us"]:
                    continue

                title_td = row.find("td", class_="event")
                event_name = title_td.get_text(strip=True) if title_td else "Unbekanntes Event"

                actual_td = row.find("td", class_="act")
                forecast_td = row.find("td", class_="fore")

                actual = actual_td.get_text(strip=True) if actual_td else ""
                forecast = forecast_td.get_text(strip=True) if forecast_td else ""

                events.append({
                    "country": country,
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
        print(f"❌ Fehler beim Abrufen der Daten: {e}")
        return []