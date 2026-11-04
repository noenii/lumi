import discord

from discord.ext import commands

from stuff.funcs import ts, perm_check, list_roles
from stuff.views import vPaginator, ePaginator, chunk_list
from setup.config import EMBED_COLOR

class Role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def role(self, ctx: commands.Context, role: discord.Role):
        m = len(role.members)
        e = discord.Embed(
            title = f"**{role.name}**",
            description = f"-# There {'is' if m == 1 else 'are'} **{m}** member{'s' if m == 1 else ''} with this role\n"
            f"-# This role **{'is' if role.hoist else 'isn\'t'}** hoisted"
        )

        e.add_field(
            name = "__**Information**__ ",
            value = f"-# Created: {ts(int(role.created_at.timestamp()), 'D')} ({ts(int(role.created_at.timestamp()), 'R')})\n"
            f"-# Dangerous: **{perm_check(role)}**",
            inline = False
        )

        await ctx.send(embed = e)

    @commands.hybrid_command()
    async def roleinfo(self, ctx: commands.Context, role: discord.Role):
        await ctx.send(f"-# Role: **{role.name}**, ID: **{role.id}**, Pos: **{role.position}**, Hoist: **{role.hoist}**, Mention: **{role.mentionable}**")

    @commands.hybrid_command()
    async def roles(self, ctx: commands.Context, member: discord.Member = None):
        if member:
            roles = [role for role in reversed(member.roles) if role != ctx.guild.default_role]

            if not roles:
                return await ctx.send("User has no Roles")

            role_lines = []
            for index, role in enumerate(roles, start = 1):
                role_lines.append(f"`{index:02d}` {role.mention} - `{role.id}`")

            chunks = list(chunk_list(role_lines, 5))
            total_pages = len(chunks)

            pages_data = []
            for page_idx, chunk in enumerate(chunks, start = 1):
                items = [
                    discord.ui.Section(
                        discord.ui.TextDisplay(f"## Roles for {member.display_name}"),
                        accessory = discord.ui.Thumbnail(member.display_avatar.url)
                    ),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay("\n".join(chunk)),
                    discord.ui.Separator(),
                    discord.ui.TextDisplay(f"-# Page {page_idx}/{total_pages}")
                ]
                pages_data.append(items)

            view = vPaginator(pages_data = pages_data, buttons = ["prev", "next", "search", "exit"])
            message = await ctx.send(view = view, allowed_mentions = discord.AllowedMentions(roles = False, users = False, everyone = False))
            view.message = message
            return

        rs = [r for r in ctx.guild.roles if r != ctx.guild.default_role]

        if not rs:
            return await ctx.send("-# This Server has no Roles")

        bp = sorted(rs, key = lambda r: r.position, reverse = True)
        bc = sorted(rs, key = lambda r: len(r.members), reverse = True)

        pl = [f"> `{r.position}` | {r.mention}" for r in bp]
        cl = [f"> `{len(r.members)}` | {r.mention}" for r in bc]

        pc = list(chunk_list(pl, 20))
        cc = list(chunk_list(cl, 20))
        tp = len(pc)

        embeds = []
        for i in range(tp):
            embed = discord.Embed(
                title = "Roles Information",
                description = f"> **Count**: `{len(rs)}`",
                color = EMBED_COLOR
            )

            embed.add_field(
                name = "Sorted by position",
                value = "\n".join(pc[i]),
                inline = True
            )

            embed.add_field(
                name = "Sorted by member count",
                value = "\n".join(cc[i]),
                inline = True
            )
            embed.set_footer(text = f"Page {i + 1}/{tp}")
            embeds.append(embed)

        if len(embeds) == 1:
            return await ctx.send(embed = embeds[0])

        view = ePaginator(embeds = embeds, buttons = ["prev", "next", "search", "exit"])
        message = await ctx.send(embed = embeds[0], view = view)
        view.message = message

    @commands.hybrid_command()
    async def withrole(self, ctx: commands.Context, role: discord.Role):
        if not role.members:
            return await ctx.send("-# Role has no Members")

        bj = sorted(role.members, key = lambda m: m.joined_at)
        ba = sorted(role.members, key = lambda m: m.display_name.lower())

        jl = [f"> `{i}` | {r.mention}" for i, r in enumerate(bj)]
        al = [f"> `{i}` | {r.mention}" for i, r in enumerate(ba)]

        pj = list(chunk_list(jl, 20))
        pa = list(chunk_list(al, 20))

        l = len(pj)

        embeds = []
        for i in range(l):
            embed = discord.Embed(
                title = f"Members with {role.name}",
                description = f"> **Count**: `{len(role.members)}`",
                color = EMBED_COLOR
            )

            embed.add_field(
                name = "Sorted by Join Date",
                value = "\n".join(pj[i]),
                inline = True
            )

            embed.add_field(
                name = "Sorted Alphabetically",
                value = "\n".join(pa[i]),
                inline = True
            )
            embed.set_footer(text = f"Page {i + 1}/{l}")
            embeds.append(embed)

        if len(embeds) == 1:
            return await ctx.send(embed = embeds[0])

        view = ePaginator(embeds = embeds, buttons = ["prev", "next", "search", "exit"])
        message = await ctx.send(embed = embeds[0], view = view)
        view.message = message

async def setup(bot):
    await bot.add_cog(Role(bot))
