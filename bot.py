import discord
from discord.ext import commands, tasks
import datetime
import os
from investing_scraper import get_investing_calendar, posted_events
from nasdaq_earnings_scraper import get_nasdaq_earnings

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

def create_calendar_embed(events, title="Wirtschaftskalender Update"):
    embed = discord.Embed(
        title=title,
        description=f"📅 {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')} Uhr",
        color=0x1abc9c
    )

    if not events:
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d.%m.%Y")
        embed.add_field(
            name=f"📅 {tomorrow} – Keine wichtigen Termine",
            value="🔔 Genießt euren Tag! 😎",
            inline=False
        )
        return embed

    germany_events = [e for e in events if "germany" in e['country']]
    usa_events = [e for e in events if "united states" in e['country']]

    if germany_events:
        value = ""
        for event in germany_events:
            value += f"🕐 {event['time']} Uhr – {event['title']}\n"
        embed.add_field(name="🇩🇪 Deutschland", value=value, inline=False)

    if usa_events:
        value = ""
        for event in usa_events:
            value += f"🕐 {event['time']} Uhr – {event['title']}\n"
        embed.add_field(name="🇺🇸 USA", value=value, inline=False)

    return embed

def create_calendar_result_embed(event):
    embed = discord.Embed(
        title="📢 Wirtschaftsdaten veröffentlicht",
        description=f"📅 {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')} Uhr",
        color=0xe67e22
    )

    country_flags = {
        "germany": "🇩🇪",
        "united states": "🇺🇸"
    }

    flag = country_flags.get(event['country'], "")

    embed.add_field(
        name=f"{flag} {event['title']}",
        value=f"🕐 {event['time']} Uhr\n"
              f"**Ist:** {event['actual']}\n"
              f"**Erwartung:** {event['forecast']}\n"
              f"**Vorher:** {event['previous']}",
        inline=False
    )
    return embed

def create_nasdaq_earnings_embed(earnings, title="Nasdaq Earnings"):
    embed = discord.Embed(
        title=title,
        description=f"📅 {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')} Uhr",
        color=0x9b59b6
    )

    if not earnings:
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d.%m.%Y")
        embed.add_field(
            name=f"📅 {tomorrow} – Keine Earnings morgen",
            value="📈 Genießt euren Tag! 😎",
            inline=False
        )
        return embed

    for event in earnings:
        embed.add_field(
            name=f"{event['company']} ({event['ticker']})",
            value=f"🕐 {event['report_time']}\n"
                  f"**EPS Erwartung:** {event['eps_estimate']}\n"
                  f"**Umsatz Erwartung:** {event['revenue_estimate']}",
            inline=False
        )
    return embed

@tasks.loop(minutes=1)
async def economic_calendar_loop():
    now = datetime.datetime.now()
    weekday = now.weekday()

    if 0 <= weekday <= 4 and (7 <= now.hour <= 22):
        print(f"🔵 Abfrage um {now.strftime('%H:%M')}")
        calendar_channel = bot.get_channel(CHANNEL_ID_CALENDAR)
        earnings_channel = bot.get_channel(CHANNEL_ID_EARNINGS)

        # 22:00 Uhr ➔ Tagesübersicht für Morgen posten
        if now.hour == 22 and now.minute <= 5:
            tomorrow_events = get_investing_calendar(for_tomorrow=True)
            embed = create_calendar_embed(tomorrow_events, title="📅 Tageskalender Wirtschaft (Morgen)")
            await calendar_channel.send(embed=embed)

            tomorrow_earnings = get_nasdaq_earnings(for_tomorrow=True)
            earnings_embed = create_nasdaq_earnings_embed(tomorrow_earnings, title="📈 Tageskalender Earnings (Morgen)")
            await earnings_channel.send(embed=earnings_embed)

        # Tagsüber: Veröffentlichte Einzelereignisse posten
        today_events = get_investing_calendar()
        for event in today_events:
            identifier = f"{event['time']} {event['title']}"
            if event['actual'] and identifier not in posted_events:
                embed = create_calendar_result_embed(event)
                await calendar_channel.send(embed=embed)
                posted_events.add(identifier)

    else:
        print(f"🕗 Ignoriert um {now.strftime('%H:%M')} (außerhalb 07–22 Uhr oder Wochenende)")

@bot.command()
async def hilfe(ctx):
    embed = discord.Embed(
        title="📖 Bot Hilfe",
        description="Hier sind die verfügbaren Befehle:",
        color=0x3498db
    )
    embed.add_field(name="`!kalender`", value="📅 Holt die morgigen Wirtschaftstermine.", inline=False)
    embed.add_field(name="`!earnings`", value="📈 Holt die morgigen Earnings.", inline=False)
    embed.add_field(name="`!hilfe`", value="❓ Zeigt diese Hilfeseite.", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def kalender(ctx):
    tomorrow_events = get_investing_calendar(for_tomorrow=True)
    embed = create_calendar_embed(tomorrow_events, title="📅 Tageskalender Wirtschaft (Manuell)")
    await ctx.send(embed=embed)

@bot.command()
async def earnings(ctx):
    tomorrow_earnings = get_nasdaq_earnings(for_tomorrow=True)
    embed = create_nasdaq_earnings_embed(tomorrow_earnings, title="📈 Tageskalender Earnings (Manuell)")
    await ctx.send(embed=embed)

bot.run(DISCORD_TOKEN)
