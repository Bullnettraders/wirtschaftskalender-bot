@tasks.loop(time=time(hour=22, minute=0))
async def daily_summary():
    channel = bot.get_channel(CHANNEL_ID)
    events = get_investing_calendar(for_tomorrow=True)

    embed = discord.Embed(
        title="📅 Wirtschaftskalender Morgen",
        description=f"📅 {(datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y')}",
        color=0x3498db
    )

    germany_events = [e for e in events if e['country'] == "germany"]
    us_events = [e for e in events if e['country'] == "united states"]

    if germany_events:
        embed.add_field(
            name="🇩🇪 Deutschland",
            value="\n".join([f"🕐 {e['time']} – {e['title']}" for e in germany_events]),
            inline=False
        )
    else:
        embed.add_field(name="🇩🇪 Deutschland", value="🔔 Keine wichtigen Termine.", inline=False)

    if us_events:
        embed.add_field(
            name="🇺🇸 USA",
            value="\n".join([f"🕐 {e['time']} – {e['title']}" for e in us_events]),
            inline=False
        )
    else:
        embed.add_field(name="🇺🇸 USA", value="🔔 Keine wichtigen Termine.", inline=False)

    await channel.send(embed=embed)

@bot.command(name="kalender")
async def kalender(ctx):
    events = get_investing_calendar(for_tomorrow=False)

    embed = discord.Embed(
        title="📅 Wirtschaftskalender Heute",
        description=f"📅 {datetime.now().strftime('%d.%m.%Y')}",
        color=0x2ecc71
    )

    germany_events = [e for e in events if e['country'] == "germany"]
    us_events = [e for e in events if e['country'] == "united states"]

    if germany_events:
        embed.add_field(
            name="🇩🇪 Deutschland",
            value="\n".join([f"🕐 {e['time']} – {e['title']}" for e in germany_events]),
            inline=False
        )
    else:
        embed.add_field(name="🇩🇪 Deutschland", value="🔔 Keine wichtigen Termine.", inline=False)

    if us_events:
        embed.add_field(
            name="🇺🇸 USA",
            value="\n".join([f"🕐 {e['time']} – {e['title']}" for e in us_events]),
            inline=False
        )
    else:
        embed.add_field(name="🇺🇸 USA", value="🔔 Keine wichtigen Termine.", inline=False)

    await ctx.send(embed=embed)