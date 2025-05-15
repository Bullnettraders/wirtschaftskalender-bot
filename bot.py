import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, time
import os
from investing_scraper import get_investing_calendar

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot ist online als {bot.user}")
    post_daily_summary.start()
    check_new_events.start()

posted_events = set()

def format_event(event):
    arrow = "🔼" if event['actual'] and event['forecast'] and event['actual'] > event['forecast'] else "🔽"
    return {
        "title": event['title'],
        "description": f"🕐 {event['time']} Uhr\n\n"
                       f"**Ist**: {event['actual']} | **Erwartung**: {event['forecast']} | **Vorher**: {event['previous']}",
        "arrow": arrow
    }

@tasks.loop(minutes=1)
async def check_new_events():
    now = datetime.now()
    if now.hour < 7 or now.hour >= 22 or now.weekday() >= 5:
        return

    events = get_investing_calendar(for_tomorrow=False)
    channel = bot.get_channel(CHANNEL_ID)

    for event in events:
        event_id = (event['time'], event['title'])
        if event_id in posted_events:
            continue

        if event['actual']:
            formatted = format_event(event)
            embed = discord.Embed(
                title=f"📍 Wirtschaftsdaten veröffentlicht",
                description=f"📅 {now.strftime('%d.%m.%Y')} {event['time']} Uhr",
                color=discord.Color.blue()
            )
            embed.add_field(name=f"{formatted['arrow']} {formatted['title']}", value=formatted['description'], inline=False)
            await channel.send(embed=embed)
            posted_events.add(event_id)

@bot.command(name="kalender")
async def manual_calendar(ctx):
    await send_daily_calendar(ctx.channel)

@tasks.loop(time=time(hour=22, minute=0))
async def post_daily_summary():
    channel = bot.get_channel(CHANNEL_ID)
    await send_daily_calendar(channel, for_tomorrow=True)

async def send_daily_calendar(channel, for_tomorrow=False):
    events = get_investing_calendar(for_tomorrow)
    if not events:
        await channel.send("🔔 Heute keine wichtigen Termine für Deutschland 🇩🇪 oder USA 🇺🇸.")
        return

    embed = discord.Embed(
        title="📅 Wirtschaftskalender Heute" if not for_tomorrow else "📅 Wirtschaftskalender Morgen",
        description=f"📅 {datetime.now().strftime('%d.%m.%Y')} {datetime.now().strftime('%H:%M')} Uhr",
        color=discord.Color.green()
    )

    de_events = [e for e in events if e['country'] == 'germany']
    us_events = [e for e in events if e['country'] == 'united states']

    value = ""
    if de_events:
        for event in de_events:
            value += f"🕐 {event['time']} Uhr – {event['title']}\n"
    else:
        value += "🔔 Keine wichtigen Termine für Deutschland.\n"

    embed.add_field(name="🇩🇪 Deutschland", value=value, inline=False)

    value = ""
    if us_events:
        for event in us_events:
            value += f"🕐 {event['time']} Uhr – {event['title']}\n"
    else:
        value += "🔔 Keine wichtigen Termine für USA.\n"

    embed.add_field(name="🇺🇸 USA", value=value, inline=False)

    await channel.send(embed=embed)

bot.run(DISCORD_TOKEN)