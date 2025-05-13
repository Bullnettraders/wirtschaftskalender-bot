import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_investing_calendar():
    url = "https://www.investing.com/economic-calendar/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    events = []

    table = soup.find("table", id="economicCalendarData")
    if not table:
        return events

    rows = table.find_all("tr", class_="js-event-item")
    today = datetime.now().strftime("%Y/%m/%d")

    for row in rows:
        date_attr = row.get("data-event-datetime")
        if not date_attr:
            continue

        if date_attr.startswith(today):
            try:
                event_time = datetime.strptime(date_attr, "%Y/%m/%d %H:%M:%S")
                event_time_local = event_time.strftime("%H:%M")
                country = row.get("data-country")
                title = row.find("td", class_="event").get_text(strip=True)

                if country in ["de", "us"]:
                    events.append({
                        "country": country,
                        "time": event_time_local,
                        "title": title
                    })
            except Exception as e:
                print(f"Fehler beim Verarbeiten eines Events: {e}")

    return events
