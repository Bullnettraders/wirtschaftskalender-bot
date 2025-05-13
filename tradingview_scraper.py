import requests
from datetime import datetime, timezone

def get_tradingview_calendar():
    url = "https://economic-calendar.tradingview.com/events"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers)
        print("🔵 API Antwort von TradingView:")
        print(response.text)

        if response.status_code != 200:
            print(f"❌ Fehler beim Abrufen: Status Code {response.status_code}")
            return []

        data = response.json()

        events = []
        today = datetime.now(timezone.utc).date()

        for event in data.get("events", []):
            event_time = datetime.fromtimestamp(event.get("timestamp", 0), tz=timezone.utc)
            event_date = event_time.date()

            country = event.get("country", "").lower()

            if event_date == today and country in ["de", "us"]:
                events.append({
                    "country": country,
                    "time": event_time.strftime("%H:%M"),
                    "title": event.get("event", "Keine Beschreibung")
                })

        if not events:
            print("⚠️ Heute keine Events gefunden für Deutschland oder USA.")

        return events

    except Exception as e:
        print(f"❌ Ausnahmefehler beim Abrufen von TradingView: {e}")
        return []
import discord
from discord.ext import commands, tasks
import datetime
import os
from tradingview_scraper import get_tradingview_calendar  # Neu: Import aus tradingview_scraper

# Intents setzen
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

@bot.event
async def on_ready():
    print(f"✅ Bot ist online als {bot.user}")
    economic_calendar_loop.start()

@tasks.loop(minutes=30)
async def economic_calendar_loop():
    now = datetime.datetime.now()
    current_hour = now.hour

    if 8 <= current_hour <= 22:
        channel = bot.get_channel(CHANNEL_ID)
        events = get_tradingview_calendar()

        country_names = {
            "de": "🇩🇪 Deutschland",
            "us": "🇺🇸 USA"
        }

        if not events:
            await channel.send(f"📅 Keine Wirtschaftstermine gefunden ({now.strftime('%d.%m.%Y')})")
            return

        message = f"📅 **Wirtschaftskalender Update {now.strftime('%H:%M')} Uhr**\n\n"

        countries = ["de", "us"]

        for country in countries:
            country_events = [e for e in events if e['country'] == country]
            if country_events:
                message += f"{country_names[country]}:\n"
                for event in country_events:
                    message += f"- {event['time']} Uhr: {event['title']}\n"
            else:
                message += f"Keine Termine für {country_names[country]} heute.\n"
            message += "\n"

        await channel.send(message)
    else:
        print(f"🕗 Ignoriert um {now.strftime('%H:%M')} (außerhalb 8-22 Uhr)")

@bot.command()
async def update(ctx):
    """Manuelles Abrufen der aktuellen Wirtschaftstermine"""
    events = get_tradingview_calendar()

    country_names = {
        "de": "🇩🇪 Deutschland",
        "us": "🇺🇸 USA"
    }

    if not events:
        await ctx.send(f"📅 Keine Wirtschaftstermine gefunden ({datetime.datetime.now().strftime('%d.%m.%Y')})")
        return

    message = f"📅 **Manuelles Wirtschaftskalender Update {datetime.datetime.now().strftime('%H:%M')} Uhr**\n\n"

    countries = ["de", "us"]

    for country in countries:
        country_events = [e for e in events if e['country'] == country]
        if country_events:
            message += f"{country_names[country]}:\n"
            for event in country_events:
                message += f"- {event['time']} Uhr: {event['title']}\n"
        else:
            message += f"Keine Termine für {country_names[country]} heute.\n"
        message += "\n"

    await ctx.send(message)

bot.run(DISCORD_TOKEN)
