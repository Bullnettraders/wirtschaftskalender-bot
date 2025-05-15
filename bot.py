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

    # Sortieren nach Uhrzeit
    def event_sort_key(e):
        try:
            return datetime.datetime.strptime(e['time'], "%H:%M")
        except:
            return datetime.datetime.min  # Falls keine Zeit vorhanden (—)

    germany_events = sorted(germany_events, key=event_sort_key)
    usa_events = sorted(usa_events, key=event_sort_key)

    if germany_events:
        value = ""
        for event in germany_events:
            event_time = event['time'] if event['time'] != "—" else "—"
            value += f"🕐 {event_time} – {event['title']}\n"
        embed.add_field(name="🇩🇪 Deutschland", value=value, inline=False)
    else:
        embed.add_field(name="🇩🇪 Deutschland", value="🔔 Keine wichtigen Termine für Deutschland.", inline=False)

    if usa_events:
        value = ""
        for event in usa_events:
            event_time = event['time'] if event['time'] != "—" else "—"
            value += f"🕐 {event_time} – {event['title']}\n"
        embed.add_field(name="🇺🇸 USA", value=value, inline=False)
    else:
        embed.add_field(name="🇺🇸 USA", value="🔔 Keine wichtigen Termine für USA.", inline=False)

    return embed