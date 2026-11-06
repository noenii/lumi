import discord

from discord.ext import commands
from stuff.funcs import container, ts

class Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # needed: emojis, stickers, sounds, channels, boosters,
    # features, owner, member count, invites, events, security, rules

    # owner = ctx.guild.owner or await self.bot.fetch_user(ctx.guild.owner_id)

    @commands.hybrid_group(name = "server", invoke_without_command = True)
    async def server(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.server_info)

    @server.command(name = "info")
    async def server_info(self, ctx: commands.Context):
        guild = ctx.guild

        e = discord.Embed()
        e.set_author(
            name = f"{guild.name}",
            icon_url = guild.icon.url if guild.icon else None
        )

        if guild.icon:
            e.set_thumbnail(url = guild.icon.url)

        e.add_field(
            name = "Created",
            value = f"> {ts(int(guild.created_at.timestamp()), 'D')} ({ts(int(guild.created_at.timestamp()), 'R')})",
            inline = False
        )

        total_counts = len(guild.stickers) + len(guild.emojis) + len(guild.roles)
        e.add_field(
            name = f"Assets - **{total_counts}**",
            value = (
                f"> Stickers: `{len(guild.stickers)}`\n"
                f"> Emojis: `{len(guild.emojis)}`\n"
                f"> Roles: `{len(guild.roles)}`"
            ),
            inline = True
        )

        e.add_field(
            name = f"Channels - **{len(guild.channels)}**",
            value = (
                f"> Categories: `{len(guild.categories)}`\n"
                f"> Text: `{len(guild.text_channels)}`\n"
                f"> Voice: `{len(guild.voice_channels)}`"
            ),
            inline = True
        )

        e.add_field(
            name = f"Members - **{guild.member_count}**",
            value = (
                f"> Total: `{guild.member_count}`\n"
                f"> Boosters: `{len(guild.premium_subscribers)}`"
            ),
            inline = True
        )

        e.add_field(
            name = "Boosts",
            value = (
                f"> Level: `{guild.premium_tier}`\n"
                f"> Boosts: `{guild.premium_subscription_count or 0}`\n"
                f"> Boosters: `{len(guild.premium_subscribers)}`"
            ),
            inline = True
        )

        e.add_field(
            name = "Design",
            value = (
                f"> Icon: {f"[View]({guild.icon.url})" if guild.icon else "`None`"}\n"
                f"> Banner: {f"[View]({guild.banner.url})" if guild.banner else "`None`"}\n"
                f"> Splash: {f"[View]({guild.splash.url})" if guild.splash else "`None`"}"
            ),
            inline = True
        )

        e.add_field(
            name = "System",
            value = (
                f"> Verification: `{guild.verification_level.name}`\n"
                f"> MFA: `{"Enabled" if guild.mfa_level else "Disabled"}`\n"
                f"> Vanity: `{f"{guild.vanity_url_code}" if guild.vanity_url_code else "`None`"}`"
            ),
            inline = True
        )

        e.set_footer(text = f"ID: {guild.id}")

        await ctx.send(embed = e)

    @server.command(name = "icon")
    async def server_icon(self, ctx: commands.Context):
        if not ctx.guild.icon:
            return await ctx.send("-# Server has No Icon")

        v = container(
            ctx,
            image = ctx.guild.icon.url,
            buttons = [(ctx.guild.icon.url, None, "<:discord:1567438524108636241>")]
        )

        await ctx.send(view = v)

    @server.command(name = "banner")
    async def server_banner(self, ctx: commands.Context):
        if not ctx.guild.banner:
            return await ctx.send("-# Server has No Banner")

        v = container(
            ctx,
            image = ctx.guild.banner.url,
            buttons = [(ctx.guild.banner.url, None, "<:discord:1567438524108636241>")]
        )

        await ctx.send(view = v)

    @server.command(name = "splash")
    async def splash(self, ctx: commands.Context):
        if not ctx.guild.splash:
            return await ctx.send("-# Server has No Splash Banner")

        v = container(
            ctx,
            image = ctx.guild.splash.url,
            buttons = [(ctx.guild.splash.url, None, "<:discord:1567438524108636241>")]
        )

        await ctx.send(view = v)

async def setup(bot):
    await bot.add_cog(Server(bot))
