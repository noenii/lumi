import discord, time, psutil, platform, asyncio, os, sys, colorama

from discord.ext import commands
from colorama import Fore, Style

from stuff.funcs import fmt_time
from setup.config import ROOT

colorama.init(autoreset = True)

class System(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def ping(self, ctx: commands.Context):
        start = time.time()

        if ctx.interaction:
            await ctx.defer()
            end = time.time()
        elif ctx.message:
            try:
                await ctx.message.add_reaction(discord.PartialEmoji(name = "loading", id = 1490220248475893892, animated = True))
            except Exception:
                pass
            end = time.time()

        await ctx.send(f"-# WS: **{round(self.bot.latency * 1000)} ms**, API: **{round((end - start) * 1000)} ms**")

        if ctx.message:
            try:
                await ctx.message.remove_reaction(discord.PartialEmoji(name = "loading", id = 1490220248475893892, animated = True), self.bot.user)
            except Exception:
                pass

    @commands.hybrid_command()
    @commands.is_owner()
    async def sys(self, ctx: commands.Context):
        await ctx.send(f"-# CPU: **{psutil.cpu_percent(interval = 0.1):.1f}%**, RAM: **{psutil.virtual_memory().percent}%**")

    @commands.hybrid_command()
    @commands.is_owner()
    async def env(self, ctx: commands.Context):
        await ctx.send(f"-# Py: **{platform.python_version()}**, DPY: **{discord.__version__}**, OS: **{platform.system()} {platform.release()} {platform.machine()}**")

    @commands.hybrid_command()
    @commands.is_owner()
    async def uptime(self, ctx: commands.Context):
        await ctx.send(f"-# **{fmt_time(int(time.time() - self.bot.start_time))}**")

    @commands.hybrid_command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("-# Shutting Down")
        print(Style.BRIGHT + Fore.MAGENTA + "[DEV] Bot Shutdown")
        self.bot.system_logger.info("[SYS] Bot Shutdown")

        async def close():
            await asyncio.sleep(0)
            await self.bot.close()

        asyncio.create_task(close())

    @commands.hybrid_command()
    @commands.is_owner()
    async def restart(self, ctx):
        await ctx.send("-# Restarting...")
        print(Style.BRIGHT + Fore.MAGENTA + "[DEV] Bot Restarting...")
        self.bot.system_logger.info("[SYS] Bot Restarted")
        os.execv(sys.executable, [sys.executable] + sys.argv)

    @commands.hybrid_command()
    @commands.is_owner()
    async def load(self, ctx, *, extensions: str = None):
        await self.p_ext(ctx, extensions, self.bot.load_extension, "Load")

    @commands.hybrid_command()
    @commands.is_owner()
    async def unload(self, ctx, *, extensions: str = None):
        await self.p_ext(ctx, extensions, self.bot.unload_extension, "Unload")

    @commands.hybrid_command()
    @commands.is_owner()
    async def reload(self, ctx, *, extensions: str = None):
        await self.p_ext(ctx, extensions, self.bot.reload_extension, "Reload")

    @commands.hybrid_command()
    @commands.is_owner()
    async def sync(self, ctx):
        try:
            synced = await self.bot.tree.sync()
            print(Style.BRIGHT + Fore.MAGENTA + f"[DEV] Synced {len(synced)} Commands")
            await ctx.send(f"-# Successfully synced {len(synced)} commands")
        except Exception as e:
            print(Style.BRIGHT + Fore.RED + "[ERR] Failed to Sync Commands")
            await ctx.send("-# Failed to Sync Commands")

    @commands.hybrid_command()
    @commands.is_owner()
    async def extensions(self, ctx):
        loaded = sorted(
            ext.removeprefix("commands.")
            for ext in self.bot.extensions
        )

        if not loaded:
            return await ctx.send("-# No Extensions Loaded")

        await ctx.send(f"-# **{len(loaded)}**: **{'**, **'.join(loaded)}**")

    @commands.hybrid_command()
    @commands.is_owner()
    async def logs(self, ctx, log: str, lines: commands.Range[int, 1, 500] = 50):
        logs = {
            p.stem: p
            for p in (ROOT/"logs").glob("*.log")
        }

        path = logs.get(log.lower())

        if path is None:
            return await ctx.send("-# Available Logs: `sys`, `err`")

        try:
            with path.open("r", encoding = "utf-8") as f:
                text = "".join(f.readlines()[-lines:])

            if not text:
                text = "-# File is Empty."

            if len(text) > 1900:
                text = text[-1900:]

            await ctx.send(f"```log\n{text}\n```")

        except FileNotFoundError:
            await ctx.send("-# File not Found")

    async def p_ext(self, ctx, ext, afunc, a):
        if not ext:
            ext_l = [file.stem for file in (ROOT/"commands").glob("*.py") if not file.stem.startswith("_")]
        else:
            ext_l = ext.split()

        if len(ext_l) == 1:
            e = ext_l[0]
            full_ext = f"commands.{e}"
            if not (ROOT / "commands" / f"{e}.py").exists():
                return await ctx.send(f"-# **{e}** was not Found")
            try:
                await afunc(full_ext)
                await ctx.send(f"-# Successfully {a}ed **{e}**")
                print(Style.BRIGHT + Fore.MAGENTA + f"[DEV] {a}ed {e}")
            except Exception as err:
                if isinstance(err, commands.ExtensionNotFound):
                    msg = f"-# **{e}** was not Found"
                elif isinstance(err, commands.ExtensionNotLoaded):
                    msg = f"-# **{e}** is not Loaded"
                elif isinstance(err, commands.ExtensionAlreadyLoaded):
                    msg = f"-# **{e}** is already Loaded"
                else:
                    raise err
                await ctx.send(msg)
        else:
            s, f = [], []

            for item in ext_l:
                full_ext = f"commands.{item}"
                try:
                    await afunc(full_ext)
                    s.append(item)
                    print(Style.BRIGHT + Fore.MAGENTA + f"[DEV] {a}ed {item}")
                except Exception as err:
                    f.append(item)
                    print(Style.BRIGHT + Fore.YELLOW + f"[WRN] Failed to {a.lower()} {item}: {err}")

            m = "-# "
            if s:
                m += f"{a}ed **{'**, **'.join(s)}**"
            if s and f:
                m += ". "
            if f:
                m += f"Failed **{'**, **'.join(f)}**"

            await ctx.send(m)

async def setup(bot):
    await bot.add_cog(System(bot))
