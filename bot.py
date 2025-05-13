import discord
from discord.ext import commands, tasks
import datetime
import asyncio
import os
from tradingview_scraper import get_tradingview_calendar

# Intents setzen
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

@bot.event
async def on_ready():
    if not economic_calendar_loop.is_running():
        print(f"✅ Bot ist online als {bot.user}")
        economic_calendar_loop.start()

async def safe_send(channel, content):
    """Sicheres Senden, wartet bei Rate-Limit automatisch."""
    try:
        await channel.send(content)
    except discord.errors.HTTPException as e:
        if e.status == 429:
            print("⚠️ Rate Limit erreicht! Warte 10 Sekunden...")
            await asyncio.sleep(10)
            await channel.send(content)
        else:
            raise e

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
            await safe_send(channel, f"📅 Keine Wirtschaftstermine gefunden ({now.strftime('%d.%m.%Y')})")
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

        await safe_send(channel, message)
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
        await safe_send(ctx, f"📅 Keine Wirtschaftstermine gefunden ({datetime.datetime.now().strftime('%d.%m.%Y')})")
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

    await safe_send(ctx, message)

bot.run(DISCORD_TOKEN)
