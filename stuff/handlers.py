import discord, difflib

from sys import path
from discord.ext import commands
from stuff.funcs import closest

async def command_not_found(ctx, error):
    s = closest(ctx.invoked_with, [cmd.name for cmd in ctx.bot.commands])
    return await ctx.send(f"-# Did you Mean: {s}" if s else "-# Command not Found")

async def missing_required_argument(ctx, error):
    u = f"{ctx.prefix}{ctx.command.qualified_name} {' '.join(f'<{p}>' for p in ctx.command.clean_params)}"
    return await ctx.send(f"-# Correct Usage: **{u}**")

async def bad_argument(ctx, error):
    u = f"{ctx.prefix}{ctx.command.qualified_name} {' '.join(f'<{p}>' for p in ctx.command.clean_params)}"
    return await ctx.send(f"-# Bad Arg: **{error}**, Usage: **{u}**")

async def missing_permissions(ctx, error):
    p = "**, **".join(p.replace("_", " ").title() for p in error.missing_permissions)
    return await ctx.send(f"-# Missing Permissions: **{p}**")

async def missing_role(ctx, error):
    return await ctx.send(f"-# Missing Role: **{error.missing_role}**")

async def missing_any_role(ctx, error):
    r = "**, **".join(str(role) for role in error.missing_roles)
    return await ctx.send(f"-# Missing Roles: **{r}**")

async def command_on_cooldown(ctx, error):
    return await ctx.send(content = f"-# Wait **{round(error.retry_after, 1)} s**", delete_after = error.retry_after)

async def bot_missing_permissions(ctx, error):
    p = "**, **".join(p.replace("_", " ").title() for p in error.missing_permissions)
    return await ctx.send(f"-# I am Missing Permissions to do This, I Need: **{p}**")

async def not_owner(ctx, error):
    return await ctx.send("-# You Can't use Dev Commands")

async def server_only(ctx, error):
    return await ctx.send("-# This is a Server only Command")

async def dm_only(ctx, error):
    return await ctx.send("-# This is a DM only Command")

async def many_args(ctx, error):
    u = f"{ctx.prefix}{ctx.command.qualified_name} {' '.join(f'<{p}>' for p in ctx.command.clean_params)}"
    return await ctx.send(f"-# Correct Usage: **{u}**")

async def bad_color(ctx, error):
    return await ctx.send("-# Invalid Hex")

async def msg_not_found(ctx, error):
    return await ctx.send("-# Message was not Found")

async def ch_not_found(ctx, error):
    return await ctx.send("-# Channel was not Found")

async def th_not_found(ctx, error):
    return await ctx.send("-# Thread was not Found")

async def r_not_found(ctx, error):
    return await ctx.send("-# Role was not Found")

async def g_not_found(ctx, error):
    return await ctx.send("-# Server was not Found")

async def m_not_found(ctx, error):
    return await ctx.send("-# Member was not Found")

ERROR_HANDLERS = {
    commands.CommandNotFound: command_not_found,
    commands.MissingRequiredArgument: missing_required_argument,
    commands.BadArgument: bad_argument,
    commands.MissingPermissions: missing_permissions,
    commands.MissingRole: missing_role,
    commands.MissingAnyRole: missing_any_role,
    commands.CommandOnCooldown: command_on_cooldown,
    commands.BotMissingPermissions: bot_missing_permissions,
    commands.NotOwner: not_owner,
    commands.NoPrivateMessage: server_only,
    commands.PrivateMessageOnly: dm_only,
    commands.TooManyArguments: many_args,
    commands.BadColorArgument: bad_color,
    commands.MessageNotFound: msg_not_found,
    commands.ChannelNotFound: ch_not_found,
    commands.ThreadNotFound: th_not_found,
    commands.RoleNotFound: r_not_found,
    commands.GuildNotFound: g_not_found,
    commands.MemberNotFound: m_not_found
}
