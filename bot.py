import discord
from discord.ext import commands, tasks
from datetime import datetime, time
import os
from investing_scraper import get_investing_calendar, posted_events

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID_CALENDAR"))

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot ist online als {bot.user}")
    daily_summary.start()
    live_updates.start()

@tasks.loop(time=time(hour=22, minute=0))
async def daily_summary():
    channel = bot.get_channel(CHANNEL_ID)
    events = get_investing_calendar(for_tomorrow=True)
    embed = discord.Embed(title="📅 Wirtschaftskalender Morgen", description="", color=0x3498db)

    if not events:
        embed.description = "Keine wichtigen Termine."
    else:
        for country in ["germany", "united states"]:
            country_events = [e for e in events if e["country"] == country]
            text = "\n".join([f"{e['time']} – {e['title']}" for e in country_events]) or "Keine Termine"
            embed.add_field(name=country.capitalize(), value=text, inline=False)

    await channel.send(embed=embed)

@tasks.loop(minutes=1)
async def live_updates():
    now = datetime.now()
    if now.hour < 7 or now.hour >= 22 or now.weekday() >= 5:
        return

    channel = bot.get_channel(CHANNEL_ID)
    events = get_investing_calendar()
    for event in events:
        event_id = (event["time"], event["title"])
        if event["actual"] and event_id not in posted_events:
            arrow = "🔼" if event["actual"] > event["forecast"] else "🔽"
            embed = discord.Embed(
                title=f"{arrow} {event['title']}",
                description=f"**Zeit:** {event['time']} Uhr\n**Ist:** {event['actual']} | **Erwartet:** {event['forecast']} | **Vorher:** {event['previous']}",
                color=0xe67e22
            )
            await channel.send(embed=embed)
            posted_events.add(event_id)

@bot.command(name="kalender")
async def kalender(ctx):
    events = get_investing_calendar()
    embed = discord.Embed(title="📅 Wirtschaftskalender Heute", description="", color=0x2ecc71)

    if not events:
        embed.description = "Keine wichtigen Termine heute."
    else:
        for country in ["germany", "united states"]:
            country_events = [e for e in events if e["country"] == country]
            text = "\n".join([f"{e['time']} – {e['title']}" for e in country_events]) or "Keine Termine"
            embed.add_field(name=country.capitalize(), value=text, inline=False)

    await ctx.send(embed=embed)

bot.run(DISCORD_TOKEN)