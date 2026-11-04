import discord

from discord.ext import commands

from stuff.funcs import container, fetch_status, joinpos, list_roles, list_perms, ts
from stuff.views import vPaginator, chunk_list
from setup.config import EMBED_COLOR

class Member(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def member(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author

        e = discord.Embed()

        e.add_field(
            name = "Joined",
            value = f"> {ts(int(member.joined_at.timestamp()), 'D')} ({ts(int(member.joined_at.timestamp()), 'R')})",
            inline = False
        )

        e.add_field(
            name = "Created",
            value = f"> {ts(int(member.created_at.timestamp()), 'D')} ({ts(int(member.created_at.timestamp()), 'R')})",
            inline = False
        )

        rc = len(member.roles) - 1
        msg = f"-# {list_roles(ctx, member)}" if rc > 0 else "None"

        e.add_field(
            name = f"Roles ({len(member.roles) - 1})",
            value = msg,
            inline = False
        )

        e.set_author(
            icon_url = member.display_avatar.url,
            name = f"{member.global_name or member.display_name} ({member.name})",
            url = f"https://www.discord.com/users/{member.id}"
        )

        e.set_thumbnail(url = member.display_avatar.url)
        pos = await joinpos(ctx, member)
        p = f"{pos}" if pos > 0 else "**None**"
        e.set_footer(text = f"ID: {member.id} ∙ Join Pos: {(p)}")

        await ctx.send(embed = e)

    @commands.hybrid_command()
    async def avatar(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author

        v = container(
            ctx,
            image = member.display_avatar.url,
            buttons = [(member.display_avatar.url, None, "<:discord:1567438524108636241>")]
        )

        await ctx.send(view = v)

    @commands.hybrid_command()
    async def status(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author

        status_map = {
            discord.Status.online: "Online",
            discord.Status.idle: "Idle",
            discord.Status.dnd: "DND",
            discord.Status.offline: "Offline",
        }

        status = status_map.get(member.status, "Offline")
        stat = ""

        custom_act = discord.utils.get(member.activities, type = discord.ActivityType.custom)
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

        await ctx.send(f"{s}\n{a}" if a else s)

    @commands.hybrid_command()
    async def boost(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author

        if member.premium_since:
            await ctx.send(f"-# Boosting: **True**, Since: {ts(int(member.premium_since.timestamp()), 'D')} ({ts(int(member.premium_since.timestamp()), 'R')})")
        else:
            await ctx.send("-# Boosting: **False**")

    @commands.hybrid_command()
    async def perms(self, ctx: commands.Context, member: discord.Member = None):
        member = member or ctx.author
        if member.guild_permissions.administrator:
            return await ctx.send("-# User has Administrator")

        p = [
            f"**{perm.replace('_', ' ').title()}**"
            for perm, value in member.guild_permissions if value
        ]

        if not p:
            return await ctx.send("-# User Has no Perms")

        chunks = list(chunk_list(p, 10))
        total_pages = len(chunks)

        pages_data = []
        for i, chunk in enumerate(chunks, start=1):
            items = [
                discord.ui.Section(
                    discord.ui.TextDisplay(f"## {member.display_name}'s permissions — {len(p)}"),
                    accessory = discord.ui.Thumbnail(member.display_avatar.url)
                ),
                discord.ui.Separator(),
                discord.ui.TextDisplay("\n".join(chunk)),
                discord.ui.Separator(),
                discord.ui.TextDisplay(f"-# Page {i}/{total_pages}")
            ]
            pages_data.append(items)

        view = vPaginator(pages_data = pages_data, buttons = ["prev", "next", "search", "exit"])

        message = await ctx.send(view = view)
        view.message = message

async def setup(bot):
    await bot.add_cog(Member(bot))
