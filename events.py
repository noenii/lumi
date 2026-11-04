import discord, traceback, psutil, colorama

from colorama import Fore, Style
from stuff.handlers import ERROR_HANDLERS
from setup.config import DEV_CMD

colorama.init(autoreset = True)

def register_events(bot):
    @bot.event
    async def on_ready():
        if bot.ready:
            return

        bot.ready = True

        await bot.change_presence(
            status = discord.Status.dnd,
            activity = discord.CustomActivity(name = "it's a beautiful day outside")
        )

        print(Style.BRIGHT + Fore.BLUE +
            "\n=========================================\n\n"
            "      _           _                 \n"
            "     | |_ _ _____|_|___ ___ ___ _ _ \n"
            "     | | | |     | |   | .'|  _| | |\n"
            "     |_|___|_|_|_|_|_|_|__,|_| |___|\n\n"
            "               a cool bot?\n\n"
            "=========================================\n\n"
            f"   Successfully logged in as {bot.user}\n\n"
            "=========================================\n"
        )

        print(Style.BRIGHT + Fore.BLUE + "[SYS] Bot Started up")
        bot.system_logger.info("[SYS] Bot started up")
        psutil.cpu_percent(interval = None)

    '''
    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        await bot.process_commands(message)
    '''

    @bot.event
    async def on_command_completion(ctx):
        if ctx.command and ctx.command.name not in DEV_CMD:
            print(Style.BRIGHT + Fore.BLUE + f"[CMD] Command: {ctx.command}, Requested by: {ctx.author}, Server: {ctx.guild}, Channel: {ctx.channel}")

    @bot.event
    async def on_error(event, *args, **kwargs):
        traceback.print_exc()

    @bot.event
    async def on_command_error(ctx, error):
        error = getattr(error, "original", error)

        handler = ERROR_HANDLERS.get(type(error))

        if handler:
            return await handler(ctx, error)

        await ctx.send("-# Something went wrong!")

        tb = traceback.format_exception(type(error), error, error.__traceback__)
        print(Style.BRIGHT + Fore.RED + f"[ERR] Command: {ctx.command}, Requested by: {ctx.author}, Server: {ctx.guild}, Channel: {ctx.channel}, Type: {type(error).__name__}")
        print(Style.DIM + Fore.RED + f"{tb}")
        bot.error_logger.error(f"Command: {ctx.command}, Requested by: {ctx.author.id}, Server: {ctx.guild.id}, Channel: {ctx.channel.id}, Message: {ctx.message.content}, Type: {type(error).__name__}")
