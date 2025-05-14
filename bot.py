import discord
from discord.ext import commands, tasks
import datetime
import os
from investing_scraper import get_investing_calendar, posted_events
from yahoo_earnings_scraper import get_yahoo_earnings

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID_CALENDAR = int(os.getenv("CHANNEL_ID_CALENDAR"))
CHANNEL_ID_EARNINGS = int(os.getenv("CHANNEL_ID_EARNINGS"))

@bot.event
async def on_ready():
    if not economic_calendar_loop.is_running():
        print(f"✅ Bot ist online als {bot.user}")
        economic_calendar_loop.start()

def create_embed(events, title="Wirtschaftskalender Update"):
    embed = discord.Embed(
        title=title,
        description=f"📅 {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')} Uhr",
        color=0x1abc9c
    )

    country_names = {
        "germany": "🇩🇪 Deutschland",
        "united states": "🇺🇸 USA"
    }

    if not events:
        embed.add_field(name="Keine wichtigen Termine", value="🔔 Genießt euren Tag! 😎", inline=False)
        return embed

    for country in ["germany", "united states"]:
        country_events = [e for e in events if e['country'] == country]
        if country_events:
            value = ""
            for event in country_events:
                value += f"🕐 {event['time']} Uhr – {event['title']}\n"
            embed.add_field(name=country_names[country], value=value, inline=False)
        else:
            embed.add_field(name=country_names[country], value="Keine Termine heute.", inline=False)

    return embed

def create_earnings_embed(earnings, title="Earnings Update"):
    embed = discord.Embed(
        title=title,
        description=f"📅 {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')} Uhr",
        color=0x9b59b6
    )

    if not earnings:
        embed.add_field(name="Keine Earnings heute", value="📈 Genießt euren Tag! 😎", inline=False)
        return embed

    for event in earnings:
        embed.add_field(
            name=f"{event['company']} ({event['ticker']})",
            value=f"🕐 {event['time']} Uhr\n"
                  f"**EPS Erwartung:** {event['eps_estimate']}\n"
                  f"**Umsatz Erwartung:** {event['revenue_estimate']}",
            inline=False
        )
    return embed

@tasks.loop(minutes=1)
async def economic_calendar_loop():
    now = datetime.datetime.now()
    weekday = now.weekday()

    if 0 <= weekday <= 4 and (8 <= now.hour <= 22):
        if now.minute == 0 or now.minute == 30:
            print(f"🔵 Abruf um {now.strftime('%H:%M')}")
            calendar_channel = bot.get_channel(CHANNEL_ID_CALENDAR)
            earnings_channel = bot.get_channel(CHANNEL_ID_EARNINGS)

            # Wirtschaftskalender
            events = get_investing_calendar()
            if now.hour == 8 and now.minute == 0:
                embed = create_embed(events, title="📅 Tageskalender Wirtschaft")
                await calendar_channel.send(embed=embed)
            else:
                for event in events:
                    identifier = f"{event['time']} {event['title']}"
                    if event['actual'] and identifier not in posted_events:
                        embed = create_embed([event], title="📢 Neues Wirtschaftsevent!")
                        await calendar_channel.send(embed=embed)
                        posted_events.add(identifier)

            # Earnings Kalender
            earnings = get_yahoo_earnings()
            if now.hour == 8 and now.minute == 0:
                earnings_embed = create_earnings_embed(earnings, title="📈 Tageskalender Earnings")
                await earnings_channel.send(embed=earnings_embed)

    else:
        print(f"🕗 Ignoriert um {now.strftime('%H:%M')} (außerhalb 08:00–22:00 Uhr oder Wochenende)")

@bot.command()
async def hilfe(ctx):
    """Zeigt alle Befehle an"""
    embed = discord.Embed(
        title="📖 Bot Hilfe",
        description="Hier sind die verfügbaren Befehle:",
        color=0x3498db
    )
    embed.add_field(name="`!update`", value="📅 Holt manuell die aktuelle Tagesübersicht.", inline=False)
    embed.add_field(name="`!hilfe`", value="❓ Zeigt diese Hilfeseite.", inline=False)
    await ctx.send(embed=embed)

bot.run(DISCORD_TOKEN)
