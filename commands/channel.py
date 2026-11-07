import discord
from discord.ext import commands

from stuff.funcs import ts, closest
from stuff.views import vPaginator, chunk_list
from setup.config import EMBED_COLOR

class Channel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(name = "channel", invoke_without_command = True)
    async def channel(self, ctx: commands.Context, *, q: str = None):
        if q:
            s = closest(q.split()[0], [cmd.name for cmd in self.channel.commands])
            return await ctx.send(f"-# Did you Mean: {s}" if s else "-# Subcommand not Found")

        await ctx.invoke(self.channel_info, q = q)

    @channel.command(name = "info")
    async def channel_info(self, ctx: commands.Context, *, q: str = None):
        channel = None
        if q:
            c = q.strip("<#!&>")
            if c.isdigit():
                channel = ctx.guild.get_channel(int(c)) or ctx.guild.get_thread(int(c))
            if not channel:
                ac = list(ctx.guild.channels) + list(ctx.guild.threads)
                qn = q.strip("#").lower()
                channel = discord.utils.find(lambda c: c.name.lower() == qn, ac)
            if not channel:
                raise commands.ChannelNotFound(channel)
        else:
            channel = ctx.channel

        topic = getattr(channel, 'topic', None) or ""
        e = discord.Embed(
            title = f"#{channel.name} — ({channel.id})",
            description = f"\n> {topic}" if topic else "",
            color = EMBED_COLOR
        )
        e.url = f"https://discord.com/channels/{ctx.guild.id}/{channel.id}"
        e.set_author(name = f"{ctx.guild.name}", icon_url = ctx.guild.icon.url if ctx.guild.icon else None)

        e.add_field(
            name = "Created",
            value = f"{ts(int(channel.created_at.timestamp()), 'D')} ({ts(int(channel.created_at.timestamp()), 'R')})",
            inline = False
        )

        match channel:
            case discord.TextChannel():
                e.add_field(
                    name = "Details",
                    value = f"> NSFW: **{channel.is_nsfw()}**\n"
                    f"> Category: **{channel.category.name if channel.category else 'None'}**\n"
                    f"> Slowmode: {f'**{channel.slowmode_delay} s**' if channel.slowmode_delay else '**None**'}\n"
                    f"> Active Threads: **{len(channel.threads) if hasattr(channel, 'threads') else 0}**",
                    inline = True
                )

            case discord.VoiceChannel() | discord.StageChannel():
                e.add_field(
                    name = "Details",
                    value = f"> Type: **{'Stage' if isinstance(channel, discord.StageChannel) else 'Voice'}**\n"
                    f"> Bitrate: **{channel.bitrate // 1000} kbps**\n"
                    f"> User Limit: **{channel.user_limit if channel.user_limit else 'Unlimited'}**\n"
                    f"> Category: **{channel.category.name if channel.category else 'None'}**",
                    inline = True
                )

            case discord.Thread():
                e.add_field(
                    name = "Details",
                    value = f"> Type: **Thread**\n"
                    f"> Parent Channel: {channel.parent.mention if channel.parent else 'Unknown'}\n"
                    f"> Archived: **{'True' if channel.archived else 'False'}**\n"
                    f"> Locked: **{'True' if channel.locked else 'False'}**\n"
                    f"> Slowmode: {f'**{channel.slowmode_delay}s**' if channel.slowmode_delay else '**None**'}",
                    inline = True
                )
                e.add_field(
                    name = "Thread Stats",
                    value = f"> Owner: <@{channel.owner_id}>\n"
                    f"> Members: **{channel.member_count}**",
                    inline = True
                )

            case discord.ForumChannel():
                e.add_field(
                    name = "Details",
                    value = f"> Type: **Forum**\n"
                    f"> Category: **{channel.category.name if channel.category else 'None'}**\n"
                    f"> Delay: **{f'{channel.default_auto_archive_duration} m' if channel.default_auto_archive_duration else 'None'}**\n"
                    f"> Total Tags: **{len(channel.available_tags)}**",
                    inline = True
                )

            case discord.CategoryChannel():
                e.add_field(
                    name = "Details",
                    value = f"> Type: **Category**\n"
                    f"> Text Channels: **{len(channel.text_channels)}**\n"
                    f"> Voice Channels: **{len(channel.voice_channels)}**\n"
                    f"> Total Channels: **{len(channel.channels)}**",
                    inline = True
                )

        if hasattr(channel, "invites"):
            try:
                i = await channel.invites()
                if i:
                    invite_lines = [f"[{inv.code}](https://discord.gg/{inv.code}) — **{inv.uses}** uses" for inv in i[:3]]
                    iv = "\n".join(invite_lines)
                else:
                    iv = "-# None"
            except discord.Forbidden:
                iv = "-# Missing Permissions"

            e.add_field(name = "Invites", value = iv, inline = True)

        await ctx.send(embed = e)

    @channel.command(name = "perms")
    async def channel_perms(self, ctx: commands.Context, channel: discord.abc.GuildChannel = None):
        channel = channel or ctx.channel

        if not channel.overwrites:
            return await ctx.send(f"-# {channel.mention} has no Permission Overrides")

        entries = []
        for target, overwrite in channel.overwrites.items():
            if isinstance(target, discord.Role):
                target_str = f"-# Role: {target.mention}"
            elif isinstance(target, discord.Member):
                target_str = f"-# Member: {target.mention}"
            else:
                target_str = f"-# Target: {target.id}"

            allowed_perms = [perm.replace("_", " ").title() for perm, val in overwrite if val is True]
            denied_perms = [perm.replace("_", " ").title() for perm, val in overwrite if val is False]

            allows_text = "**, **".join(allowed_perms) if allowed_perms else "None"
            denies_text = "**, **".join(denied_perms) if denied_perms else "None"

            entry = (
                f"{target_str}\n"
                f"> Allowed: **{allows_text}**\n"
                f"> Denied: **{denies_text}**"
            )
            entries.append(entry)

        chunks = list(chunk_list(entries, 2))
        total_pages = len(chunks)

        pages_data = []
        for i, chunk in enumerate(chunks, start = 1):
            items = [
                discord.ui.TextDisplay(f"## Permissions for #{channel.name}"),
                discord.ui.Separator(),
                discord.ui.TextDisplay("\n\n".join(chunk)),
                discord.ui.Separator(),
                discord.ui.TextDisplay(f"-# Page {i}/{total_pages}")
            ]
            pages_data.append(items)

        if len(pages_data) == 1:
            view = vPaginator(pages_data = pages_data, buttons = [], timeout = 120)
            message = await ctx.send(view = view, allowed_mentions = discord.AllowedMentions(roles = False, users = False, everyone = False))
            view.message = message
            return

        view = vPaginator(
            pages_data = pages_data,
            buttons = ["prev", "next", "search", "exit"],
            timeout = 120
        )
        message = await ctx.send(view = view, allowed_mentions = discord.AllowedMentions(roles = False, users = False, everyone = False))
        view.message = message

    @channel.command(name = "threads")
    async def channel_threads(self, ctx: commands.Context, channel: discord.TextChannel = None):
        channel = channel or ctx.channel

        act = channel.threads if hasattr(channel, "threads") else []

        try:
            art = []
            async for thread in channel.archived_threads(limit = 50):
                art.append(thread)
        except (discord.Forbidden, AttributeError):
            art = []

        a = act + art

        if not a:
            return await ctx.send(f"-# No Threads found in {channel.mention}")

        entries = []
        for thread in a:
            entries.append(
                f"{thread.mention} (**{thread.id}**)\n"
                f"> Status: **{'Locked' if thread.locked else ('Archived' if thread.archived else 'Active')}**\n"
                f"> Parent: {thread.parent.mention if thread.parent else '**Unknown**'}\n"
                f"> Members: {thread.member_count}\n"
                f"> Owner: <@{thread.owner_id}>"
            )

        chunks = list(chunk_list(entries, 5))
        total_pages = len(chunks)

        pages_data = []
        for i, chunk in enumerate(chunks, start=1):
            items = [
                discord.ui.TextDisplay(f"## Threads in #{channel.name}"),
                discord.ui.Separator(),
                discord.ui.TextDisplay("\n\n".join(chunk)),
                discord.ui.Separator(),
                discord.ui.TextDisplay(f"-# Page {i}/{total_pages}")
            ]
            pages_data.append(items)

        if len(pages_data) == 1:
            view = vPaginator(pages_data = pages_data, buttons = [], timeout = 120)
            message = await ctx.send(view = view, allowed_mentions = discord.AllowedMentions(roles = False, users = False, everyone = False))
            view.message = message
            return

        view = vPaginator(
            pages_data = pages_data,
            buttons = ["prev", "next", "search", "exit"]
        )
        message = await ctx.send(view = view, allowed_mentions = discord.AllowedMentions(roles = False, users = False, everyone = False))
        view.message = message

    @commands.hybrid_command(name = "channels")
    async def channels(self, ctx: commands.Context):
        guild = ctx.guild

        e = discord.Embed(
            title = f"Channels in {guild.name}",
            description = f"> **Count**: `{len(guild.channels)}`",
            color = EMBED_COLOR
        )

        if guild.categories:
            e.add_field(
                name = f"Categories - **{len(guild.categories)}**",
                value = "\n".join([f"> `{i.name}`" for i in guild.categories]),
                inline = True
            )

        if guild.text_channels:
            e.add_field(
                name = f"Channels - **{len(guild.text_channels)}**",
                value = "\n".join([f"> {i.mention}" for i in guild.text_channels]),
                inline = True
            )

        if guild.voice_channels:
            e.add_field(
                name = f"Voice - **{len(guild.voice_channels)}**",
                value = "\n".join([f"> {i.mention}" for i in guild.voice_channels]),
                inline = True
            )

        if guild.stage_channels:
            e.add_field(
                name = f"Stage - **{len(guild.stage_channels)}**",
                value = "\n".join([f"> {i.mention}" for i in guild.stage_channels]),
                inline = True
            )

        forum_channels = [c for c in guild.channels if isinstance(c, discord.ForumChannel)]

        if forum_channels:
            e.add_field(
                name = f"Forums - **{len(forum_channels)}**",
                value = "\n".join([f"> {i.mention}" for i in forum_channels]),
                inline = True
            )

        await ctx.send(embed = e)

async def setup(bot):
    await bot.add_cog(Channel(bot))
