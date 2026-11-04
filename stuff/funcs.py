import discord

def container(ctx, title = None, desc = None, image = None, buttons = None):
    view = discord.ui.LayoutView()
    items = []

    if title:
        items.append(discord.ui.TextDisplay(title))
    if desc:
        items.append(discord.ui.TextDisplay(desc))

    if image:
        items.append(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(
                    media = image
                )
            )
        )

    if buttons:
        row = discord.ui.ActionRow()

        for url, label, emoji in buttons:
            row.add_item(
                discord.ui.Button(
                    style = discord.ButtonStyle.link,
                    url = url,
                    label = label,
                    emoji = discord.PartialEmoji.from_str(emoji)
                )
            )

        items.append(row)

    view.add_item(
        discord.ui.Container(
            *items
            # accent_color = c
        )
    )

    return view

def ts(t, style: str = "R"):
    return f"<t:{int(t)}:{style}>"

def fmt_time(seconds: int):
    intervals = (
        ("y", 31536000),
        ("mo", 2592000),
        ("d", 86400),
        ("h", 3600),
        ("m", 60),
        ("s", 1),
    )

    parts = []

    for name, amount in intervals:
        value, seconds = divmod(seconds, amount)

        if value:
            parts.append(f"{value}{name}")

    return " ".join(parts) or "0s"

def fetch_status(ctx, member: discord.Member = None):
    member = member or ctx.author

    status_map = {
        discord.Status.online: "Online",
        discord.Status.idle: "Idle",
        discord.Status.dnd: "DND",
        discord.Status.offline: "Offline",
    }

    status = status_map.get(member.status, "Offline")

    stat = ""
    custom_act = discord.utils.get(
        member.activities, type=discord.ActivityType.custom
    )

    if custom_act:
        status_text = custom_act.state or ""
        emoji_text = f"{custom_act.emoji} " if custom_act.emoji else ""

        if status_text or emoji_text:
            stat = f"{emoji_text}**{status_text}**"

    lines = []
    for act in member.activities:
        if isinstance(act, discord.CustomActivity):
            continue

        if isinstance(act, discord.Game):
            lines.append(f"-# Playing **{act.name}**")

        elif isinstance(act, discord.Streaming):
            lines.append(f"-# Streaming **{act.name}** ({act.platform})")

        elif isinstance(act, discord.Spotify):
            lines.append(f"-# Listening to **{act.title}** by **{act.artist}**")

        elif isinstance(act, discord.Activity):
            if act.type == discord.ActivityType.watching:
                lines.append(f"-# Watching **{act.name}**")
            elif act.type == discord.ActivityType.listening:
                lines.append(f"-# Listening to **{act.name}**")
            elif act.type == discord.ActivityType.playing:
                lines.append(f"-# Playing **{act.name}**")
            elif act.type == discord.ActivityType.competing:
                lines.append(f"-# Competing in **{act.name}**")
            else:
                lines.append(f"-# {act.type.name.title()} **{act.name}**")

    s = f"-# {stat}, **{status}**" if stat else f"-# **{status}**"
    a = "\n".join(lines) if lines else ""

    return s, a

async def joinpos(ctx, member: discord.Member):
    guild = ctx.guild
    if not guild:
        return 0

    if not guild.chunked:
        await guild.chunk()

    sorted_members = sorted(
        [m for m in guild.members if m.joined_at is not None],
        key = lambda m: m.joined_at
    )

    try:
        return sorted_members.index(member) + 1
    except ValueError:
        return 0

def list_roles(ctx, member: discord.Member = None):
    member = member or ctx.author
    f_roles = [r for r in member.roles if not r.is_default()]
    f_roles.sort(key = lambda x: x.position, reverse = True)

    roles = " ".join([r.mention for r in f_roles]) or ""

    return roles

def list_perms(member: discord.Member):
    if member.guild_permissions.administrator:
        return ["Administrator"]

    return [
        perm.replace("_", " ").title()
        for perm, value in member.guild_permissions
        if value
    ]

def perm_check(role: discord.Role):
    p = (
        'administrator',
        'manage_guild',
        'manage_roles',
        'manage_channels',
        'manage_webhooks',
        'manage_expressions',
        'kick_members',
        'ban_members',
        'mention_everyone',
        'moderate_members',
    )

    return any(getattr(role.permissions, flag, False) for flag in p)
