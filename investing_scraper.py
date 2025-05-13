import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_investing_calendar():
    url = "https://www.investing.com/economic-calendar/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Fehler beim Abrufen der Seite: Status Code {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    events = []

    table = soup.find("table", id="economicCalendarData")
    if not table:
        print("❌ Tabelle nicht gefunden.")
        return []

    rows = table.find_all("tr", class_="js-event-item")
    today = datetime.now().strftime("%Y-%m-%d")

    for row in rows:
        try:
            date_attr = row.get("data-event-datetime")
            if not date_attr:
                continue
            event_time = datetime.utcfromtimestamp(int(date_attr)).strftime("%H:%M")
            event_date = datetime.utcfromtimestamp(int(date_attr)).strftime("%Y-%m-%d")
            country = row.get("data-country")
            title = row.find("td", class_="event").get_text(strip=True)

            if country in ["de", "us"] and event_date == today:
                events.append({
                    "country": country,
                    "time": event_time,
                    "title": title
                })

        except Exception as e:
            print(f"⚠️ Fehler beim Verarbeiten eines Events: {e}")
            continue

    return events
