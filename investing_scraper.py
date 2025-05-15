import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

posted_events = set()

def get_investing_calendar(for_tomorrow=False):
    url = "https://www.investing.com/economic-calendar/Service/getCalendarFilteredData"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    today = datetime.now()
    target_date = today + timedelta(days=1) if for_tomorrow else today
    date_str = target_date.strftime("%Y-%m-%d")

    payload = {
        "country[]": ["4", "5"],  # 4 = USA, 5 = Deutschland
        "importance[]": ["2", "3"],  # nur 2 und 3 Sterne Events
        "timeZone": "55",  # Europa/Berlin
        "timeFilter": "timeRemain",
        "dateFrom": date_str,
        "dateTo": date_str
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code != 200:
            print(f"❌ Fehler beim Abrufen: Status {response.status_code}")
            return []

        data = response.json()

        if not data or 'data' not in data:
            print("❌ Keine Daten erhalten.")
            return []

        events_html = data['data']
        soup = BeautifulSoup(events_html, "lxml")
        rows = soup.find_all("tr", class_="js-event-item")

        events = []

        for row in rows:
            try:
                country = row.get("data-country", "").lower()
                importance = int(row.get("data-importance", "0"))
                timestamp = row.get("data-event-datetime", None)

                if not timestamp or importance < 2:
                    continue

                try:
                    event_time_dt = datetime.strptime(timestamp, "%Y/%m/%d %H:%M")
                    event_time = event_time_dt.strftime("%H:%M")
                except Exception:
                    event_time = "—"

                title_td = row.find("td", class_="event")
                event_name = title_td.get_text(strip=True) if title_td else "Unbekanntes Event"

                actual_td = row.find("td", class_="act")
                forecast_td = row.find("td", class_="fore")
                previous_td = row.find("td", class_="prev")

                actual = actual_td.get_text(strip=True) if actual_td else "n/a"
                forecast = forecast_td.get_text(strip=True) if forecast_td else "n/a"
                previous = previous_td.get_text(strip=True) if previous_td else "n/a"

                if country in ["united states", "germany"]:
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
                print(f"⚠️ Fehler beim Parsen eines Events: {e}")
                continue

        print(f"🟢 Gefundene wichtige Events: {len(events)}")
        return events

    except Exception as e:
        print(f"❌ Fehler beim Abrufen der Daten: {e}")
        return []