import discord

from discord.ext import commands
from stuff.funcs import container, ts

class Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # needed: emojis, stickers, sounds, channels, boosters,
    # features, owner, member count, invites, events, security, rules

    # owner = ctx.guild.owner or await self.bot.fetch_user(ctx.guild.owner_id)

    @commands.hybrid_command()
    async def server(self, ctx: commands.Context):
        guild = ctx.guild

        e = discord.Embed()
        e.set_author(
            name = f"{ctx.guild.name}",
            icon_url = ctx.guild.icon.url if ctx.guild.icon else None
        )

        if guild.icon:
            e.set_thumbnail(url = ctx.guild.icon.url)

        e.add_field(
            name = "Created",
            value = f"> {ts(int(ctx.guild.created_at.timestamp()), 'D')} ({ts(int(ctx.guild.created_at.timestamp()), 'R')})",
            inline = False
        )

        total_counts = len(ctx.guild.stickers) + len(ctx.guild.emojis) + len(ctx.guild.roles)
        e.add_field(
            name = f"Assets - **{total_counts}**",
            value = (
                f"> Stickers: `{len(ctx.guild.stickers)}`\n"
                f"> Emojis: `{len(ctx.guild.emojis)}`\n"
                f"> Roles: `{len(ctx.guild.roles)}`"
            ),
            inline = True
        )

        e.add_field(
            name = f"Channels - **{len(ctx.guild.channels)}**",
            value = (
                f"> Categories: `{len(ctx.guild.categories)}`\n"
                f"> Text: `{len(ctx.guild.text_channels)}`\n"
                f"> Voice: `{len(ctx.guild.voice_channels)}`"
            ),
            inline = True
        )

        e.add_field(
            name = f"Members - **{ctx.guild.member_count}**",
            value = (
                f"> Total: `{ctx.guild.member_count}`\n"
                f"> Boosters: `{len(ctx.guild.premium_subscribers)}`"
            ),
            inline = True
        )

        e.add_field(
            name = "Boosts",
            value = (
                f"> Level: `{ctx.guild.premium_tier}`\n"
                f"> Boosts: `{ctx.guild.premium_subscription_count or 0}`\n"
                f"> Boosters: `{len(ctx.guild.premium_subscribers)}`"
            ),
            inline = True
        )

        e.add_field(
            name = "Design",
            value = (
                f"> Icon: {f"[View]({ctx.guild.icon.url})" if guild.icon else "`None`"}\n"
                f"> Banner: {f"[View]({ctx.guild.banner.url})" if guild.banner else "`None`"}\n"
                f"> Splash: {f"[View]({ctx.guild.splash.url})" if guild.splash else "`None`"}"
            ),
            inline = True
        )

        e.add_field(
            name = "System",
            value = (
                f"> Verification: `{guild.verification_level.name}`\n"
                f"> MFA: `{"Enabled" if ctx.guild.mfa_level else "Disabled"}`\n"
                f"> Vanity: `{f"{ctx.guild.vanity_url_code}" if ctx.guild.vanity_url_code else "`None`"}`"
            ),
            inline = True
        )

        e.set_footer(text = f"ID: {ctx.guild.id}")

        await ctx.send(embed = e)

    @commands.hybrid_command()
    async def icon(self, ctx: commands.Context):
        if not ctx.guild.icon:
            return await ctx.send("-# Server has No Icon")

        v = container(
            ctx,
            image = ctx.guild.icon.url,
            buttons = [(ctx.guild.icon.url, None, "<:discord:1567438524108636241>")]
        )

        await ctx.send(view = v)

    @commands.hybrid_command()
    async def banner(self, ctx: commands.Context):
        if not ctx.guild.banner:
            return await ctx.send("-# Server has No Banner")

        v = container(
            ctx,
            image = ctx.guild.banner.url,
            buttons = [(ctx.guild.banner.url, None, "<:discord:1567438524108636241>")]
        )

        await ctx.send(view = v)

    @commands.hybrid_command()
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
