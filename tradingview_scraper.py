import requests
from datetime import datetime, timezone

def get_tradingview_calendar():
    url = "https://economic-calendar.tradingview.com/events"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"❌ Fehler beim Abrufen: Status Code {response.status_code}")
            return []

        data = response.json()

        events = []
        today = datetime.now(timezone.utc).date()

        for event in data.get("events", []):
            event_timestamp = event.get("timestamp")
            event_country = event.get("country", "").upper()
            event_title = event.get("event", "Unbekanntes Event")

            if not event_timestamp or not event_country:
                continue

            event_time = datetime.fromtimestamp(event_timestamp, tz=timezone.utc)
            event_date = event_time.date()

            # Länder-Filter: Deutschland (DE), USA (US)
            if event_date == today and event_country in ["DE", "US"]:
                events.append({
                    "country": event_country,
                    "time": event_time.strftime("%H:%M"),
                    "title": event_title
                })

        return events

    except Exception as e:
        print(f"❌ Ausnahmefehler beim Abrufen: {e}")
        return []
@tasks.loop(minutes=30)
async def economic_calendar_loop():
    now = datetime.datetime.now()
    current_hour = now.hour

    if 8 <= current_hour <= 22:
        channel = bot.get_channel(CHANNEL_ID)
        events = get_tradingview_calendar()

        country_names = {
            "DE": "🇩🇪 Deutschland",
            "US": "🇺🇸 USA"
        }

        if not events:
            message = (
                f"📅 **Wirtschaftskalender Update {now.strftime('%H:%M')} Uhr**\n\n"
                "🔔 Heute keine wichtigen Termine für Deutschland 🇩🇪 oder USA 🇺🇸.\n"
                "Genießt euren Tag! 😎"
            )
            await safe_send(channel, message)
            return

        message = f"📅 **Wirtschaftskalender Update {now.strftime('%H:%M')} Uhr**\n\n"

        for country in ["DE", "US"]:
            country_events = [e for e in events if e['country'] == country]
            if country_events:
                message += f"{country_names[country]}:\n"
                for event in country_events:
                    message += f"- {event['time']} Uhr: {event['title']}\n"
            else:
                message += f"Keine Termine für {country_names[country]} heute.\n"
            message += "\n"

        await safe_send(channel, message)
