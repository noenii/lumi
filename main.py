import discord, asyncio, time, threading, colorama, os, logging

from discord.ext import commands
from colorama import Fore, Style

from setup.config import TOKEN, PREFIX, ROOT

from events import register_events

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix = PREFIX, intents = intents, chunk_guilds_at_startup = True)

colorama.init(autoreset = True)

bot.ready = False
bot.start_time = time.time()

os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
os.makedirs(ROOT/"logs", exist_ok = True)

def mklog(name, filename, level):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        file_path = os.path.join(ROOT/"logs", filename)

        handler = logging.FileHandler(file_path, encoding = "utf-8")
        handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s - Time: %(asctime)s"))
        logger.addHandler(handler)

    return logger

bot.system_logger = mklog("sys", "sys.log", logging.INFO)
bot.error_logger = mklog("err", "err.log", logging.ERROR)

async def main():
    print(Style.BRIGHT + Fore.BLUE + "\n[SYS] Starting up...")

    extension_dir = os.path.join(ROOT, "commands")
    if os.path.exists(extension_dir):
        filez = [f for f in os.listdir(extension_dir) if f.endswith(".py") and not f.startswith("_")]
    else:
        filez = []

    tf = len(filez)
    fe = []

    print(Style.BRIGHT + Fore.BLUE + "[SYS] Loading Extensions...\n")

    for fn in filez:
        print(Style.BRIGHT + Fore.BLUE + f"[SYS] Loading: {fn}")

        try:
            await bot.load_extension(f"commands.{fn[:-3]}")
        except Exception as e:
            print(Style.BRIGHT + Fore.RED + f"[ERR] {e}")
            bot.system_logger.error(f"Failed to load extension {fn}, Error: {e}")
            fe.append(fn)

    print(Style.BRIGHT + Fore.BLUE + f"\n[SYS] Successfully Loaded Extensions ({tf - len(fe)}/{tf})")

    if fe:
        failed_str = ", ".join(fe)
        print(Style.BRIGHT + Fore.YELLOW + f"[WRN] Failed to Load: {failed_str}")
        bot.system_logger.warning(f" [WRN] Failed to load extensions: {failed_str}")

    register_events(bot)

    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Style.BRIGHT + Fore.BLUE + "\n[SYS] Bot Shutdown")
        bot.system_logger.info("[SYS] Bot Shutdown")
