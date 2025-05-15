import requests
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
    from_date = target_date.strftime("%Y-%m-%d")
    to_date = target_date.strftime("%Y-%m-%d")

    payload = {
        "country[]": ["4", "5"],  # 4 = USA, 5 = Deutschland
        "importance[]": ["2", "3"],  # Nur ab 2 Sternen Wichtigkeit
        "timeZone": "55",  # Europa/Berlin
        "timeFilter": "timeRemain",  # Zeige nur relevante Zeiten
        "dateFrom": from_date,
        "dateTo": to_date
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code != 200:
            print(f"❌ Fehler beim Abrufen: Status {response.status_code}")
            return []

        data = response.json()

        if not data or 'data' not in data:
            print("❌ Keine Daten zurückbekommen.")
            return []

        events_raw_html = data['data']
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(events_raw_html, "lxml")
        rows = soup.find_all("tr", class_="js-event-item")

        events = []

        for row in rows:
            try:
                country = row.get("data-country", "").lower()
                timestamp = row.get("data-event-datetime")
                importance = int(row.get("data-importance", "0"))

                title_td = row.find("td", class_="event")
                event_name = title_td.get_text(strip=True) if title_td else "Unbekanntes Event"

                actual_td = row.find("td", class_="act")
                forecast_td = row.find("td", class_="fore")
                previous_td = row.find("td", class_="prev")

                actual = actual_td.get_text(strip=True) if actual_td else "n/a"
                forecast = forecast_td.get_text(strip=True) if forecast_td else "n/a"
                previous = previous_td.get_text(strip=True) if previous_td else "n/a"

                if timestamp:
                    event_time = datetime.utcfromtimestamp(int(timestamp)).strftime("%H:%M")
                else:
                    event_time = "—"

                if importance >= 2 and country in ["united states", "germany"]:
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
        print(f"❌ Fehler beim Abrufen der Events: {e}")
        return []