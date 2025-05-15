import requests
from bs4 import BeautifulSoup
from datetime import datetime

posted_events = set()

def get_investing_calendar(for_tomorrow=False):
    url = "https://m.investing.com/economic-calendar/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

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
    events = []

    today = datetime.now()
    target_date = today if not for_tomorrow else today.replace(day=today.day + 1)
    date_today = target_date.strftime("%Y-%m-%d")

    for row in rows:
        try:
            date_attr = row.get("data-event-datetime")
            if not date_attr:
                continue

            event_date = datetime.utcfromtimestamp(int(date_attr)).strftime("%Y-%m-%d")
            if event_date != date_today:
                continue

            country = row.get("data-country", "").lower()
            importance = int(row.get("data-importance", 0))

            if importance < 2 or country not in ["de", "us"]:
                continue

            event_time = datetime.utcfromtimestamp(int(date_attr)).strftime("%H:%M") if date_attr else "—"
            title = row.find("td", class_="event").get_text(strip=True) if row.find("td", class_="event") else "Unbekanntes Event"

            events.append({
                "country": country,
                "time": event_time if event_time else "—",
                "title": title
            })

        except Exception as e:
            print(f"⚠️ Fehler beim Parsen eines Events: {e}")
            continue

    print(f"🟢 Gefundene wichtige Events: {len(events)}")
    return events