import discord
from discord.ext import commands, tasks
import datetime
import os
from investing_scraper import get_investing_calendar, posted_events
from earnings_scraper import get_earnings_calendar

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

def create_calendar_embed(events, title="Wirtschaftskalender Update", for_tomorrow=False):
    date = datetime.datetime.now() + datetime.timedelta(days=1) if for_tomorrow else datetime.datetime.now()
    embed = discord.Embed(
        title=title,
        description=f"📅 {date.strftime('%d.%m.%Y %H:%M')} Uhr",
        color=0x1abc9c
    )

    if not events:
        embed.add_field(
            name=f"📅 {date.strftime('%d.%m.%Y')} – Keine wichtigen Termine",
            value="🔔 Genießt euren Tag! 😎\n⏳ Nächster Check in 24 Stunden!",
            inline=False
        )
        return embed

    germany_events = [e for e in events if e['country'] in ['de', 'germany']]
    usa_events = [e for e in events if e['country'] in ['us', 'united states']]

    def event_sort_key(e):
        try:
            return datetime.datetime.strptime(e['time'], "%H:%M")
        except:
            return datetime.datetime.min

    germany_events = sorted(germany_events, key=event_sort_key)
    usa_events = sorted(usa_events, key=event_sort_key)

    if germany_events:
        value = ""
        for event in germany_events:
            event_time = event['time'] if event['time'] else "—"
            value += f"🕐 {event_time} – {event['title']}\n"
        embed.add_field(name="🇩🇪 Deutschland", value=value, inline=False)
    else:
        embed.add_field(name="🇩🇪 Deutschland", value="🔔 Keine wichtigen Termine für Deutschland.", inline=False)

    if usa_events:
        value = ""
        for event in usa_events:
            event_time = event['time'] if event['time'] else "—"
            value += f"🕐 {event_time} – {event['title']}\n"
        embed.add_field(name="🇺🇸 USA", value=value, inline=False)
    else:
        embed.add_field(name="🇺🇸 USA", value="🔔 Keine wichtigen Termine für USA.", inline=False)

    return embed

def create_calendar_result_embed(event):
    embed = discord.Embed(
        title="📢 Wirtschaftsdaten veröffentlicht",
        description=f"📅 {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')} Uhr",
        color=0xe67e22
    )

    country_flags = {
        "de": "🇩🇪",
        "us": "🇺🇸"
    }
    flag = country_flags.get(event['country'], "")

    try:
        actual_value = float(event['actual'].replace('%', '').replace(',', '').replace('+', ''))
        forecast_value = float(event['forecast'].replace('%', '').replace(',', '').replace('+', ''))

        if actual_value > forecast_value:
            direction = "🔼"
        else:
            direction = "🔽"
    except:
        direction = "❔"

    embed.add_field(
        name=f"{flag} {event['title']} {direction}",
        value=f"🕐 {event['time']} Uhr\n"
              f"**Ist:** {event['actual']}\n"
              f"**Erwartung:** {event['forecast']}\n"
              f"**Vorher:** {event['previous']}",
        inline=False
    )
    return embed

def create_earnings_embed(earnings, title="Earnings Update", for_tomorrow=False):
    date = datetime.datetime.now() + datetime.timedelta(days=1) if for_tomorrow else datetime.datetime.now()
    embed = discord.Embed(
        title=title,
        description=f"📅 {date.strftime('%d.%m.%Y %H:%M')} Uhr",
        color=0x9b59b6
    )

    if not earnings:
        embed.add_field(
            name=f"📅 {date.strftime('%d.%m.%Y')} – Keine Earnings",
            value="📈 Genießt euren Tag! 😎\n⏳ Nächster Check in 24 Stunden!",
            inline=False
        )
        return embed

    for event in earnings:
        embed.add_field(
            name=f"{event['company']} ({event['symbol']})",
            value=f"🕐 Bericht: {event['report_time']}\n"
                  f"**EPS erwartet:** {event['eps_estimate']}\n"
                  f"**Umsatz erwartet:** {event['revenue_estimate']}",
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

        if now.hour == 22 and now.minute <= 5:
            tomorrow_events = get_investing_calendar(for_tomorrow=True)
            embed = create_calendar_embed(tomorrow_events, title="📅 Wirtschaftskalender Morgen", for_tomorrow=True)
            await calendar_channel.send(embed=embed)

            tomorrow_earnings = get_earnings_calendar(for_tomorrow=True)
            earnings_embed = create_earnings_embed(tomorrow_earnings, title="📈 Earnings Kalender Morgen", for_tomorrow=True)
            await earnings_channel.send(embed=earnings_embed)

        today_events = get_investing_calendar()
        for event in today_events:
            identifier = f"{event['time']} {event['title']}"
            if event['actual'] and identifier not in posted_events:
                embed = create_calendar_result_embed(event)
                await calendar_channel.send(embed=embed)
                posted_events.add(identifier)

    else:
        print(f"🕗 Ignoriert um {now.strftime('%H:%M')} (Wochenende oder außerhalb 07–22 Uhr)")

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong! Der Bot ist aktiv!")

@bot.command()
async def status(ctx):
    now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    await ctx.send(f"✅ Bot läuft! Serverzeit: {now}")

@bot.command()
async def hilfe(ctx):
    embed = discord.Embed(
        title="📖 Hilfe",
        description="Hier sind die verfügbaren Befehle:",
        color=0x3498db
    )
    embed.add_field(name="`!kalender`", value="📅 Holt die heutigen Wirtschaftstermine.", inline=False)
    embed.add_field(name="`!earnings`", value="📈 Holt die heutigen Earnings.", inline=False)
    embed.add_field(name="`!ping`", value="🏓 Testet ob der Bot aktiv ist.", inline=False)
    embed.add_field(name="`!status`", value="📊 Zeigt den Status des Bots.", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def kalender(ctx):
    today_events = get_investing_calendar(for_tomorrow=False)
    embed = create_calendar_embed(today_events, title="📅 Wirtschaftskalender Heute", for_tomorrow=False)
    await ctx.send(embed=embed)

@bot.command()
async def earnings(ctx):
    today_earnings = get_earnings_calendar(for_tomorrow=False)
    embed = create_earnings_embed(today_earnings, title="📈 Earnings Heute", for_tomorrow=False)
    await ctx.send(embed=embed)

bot.run(DISCORD_TOKEN)