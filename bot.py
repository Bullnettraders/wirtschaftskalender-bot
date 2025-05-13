import discord
from discord.ext import commands, tasks
import datetime
import os
from forexfactory_scraper import get_forex_calendar  # NEU: Forex Scraper importieren

# Intents korrekt setzen
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# Bot einrichten
bot = commands.Bot(command_prefix="!", intents=intents)

# Token und Channel-ID aus Render Environment Variables laden
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

@bot.event
async def on_ready():
    print(f"Bot ist online als {bot.user}")
    economic_calendar_loop.start()

# Hintergrundtask: Holt alle 30 Minuten Kalenderdaten
@tasks.loop(minutes=30)
async def economic_calendar_loop():
    now = datetime.datetime.now()
    current_hour = now.hour

    if 8 <= current_hour <= 22:
        channel = bot.get_channel(CHANNEL_ID)
        events = get_forex_calendar()

        if not events:
            await channel.send(f"📅 Keine Wirtschaftstermine gefunden ({now.strftime('%d.%m.%Y')})")
            return

        message = f"📅 **Wirtschaftskalender Update {now.strftime('%H:%M')} Uhr**\n\n"

        de_events = [e for e in events if e['country'] == 'de']
        us_events = [e for e in events if e['country'] == 'us']

        if de_events:
            message += "🇩🇪 **Deutschland**:\n"
            for event in de_events:
                message += f"- {event['time']} Uhr: {event['title']}\n"
        else:
            message += "Keine Termine für Deutschland heute.\n"

        message += "\n"

        if us_events:
            message += "🇺🇸 **USA**:\n"
            for event in us_events:
                message += f"- {event['time']} Uhr: {event['title']}\n"
        else:
            message += "Keine Termine für USA heute.\n"

        await channel.send(message)
    else:
        print(f"Ignoriert um {now.strftime('%H:%M')} (außerhalb 8-22 Uhr)")

# MANUELL: Update Befehl (!update)
@bot.command()
async def update(ctx):
    """Manuelles Abrufen der Wirtschaftsdaten"""
    events = get_forex_calendar()

    if not events:
        await ctx.send(f"📅 Keine Wirtschaftstermine gefunden ({datetime.datetime.now().strftime('%d.%m.%Y')})")
        return

    message = f"📅 **Manuelles Wirtschaftskalender Update {datetime.datetime.now().strftime('%H:%M')} Uhr**\n\n"

    de_events = [e for e in events if e['country'] == 'de']
    us_events = [e for e in events if e['country'] == 'us']

    if de_events:
        message += "🇩🇪 **Deutschland**:\n"
        for event in de_events:
            message += f"- {event['time']} Uhr: {event['title']}\n"
    else:
        message += "Keine Termine für Deutschland heute.\n"

    message += "\n"

    if us_events:
        message += "🇺🇸 **USA**:\n"
        for event in us_events:
            message += f"- {event['time']} Uhr: {event['title']}\n"
    else:
        message += "Keine Termine für USA heute.\n"

    await ctx.send(message)

# Bot starten
bot.run(DISCORD_TOKEN)
