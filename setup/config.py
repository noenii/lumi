import os
from dotenv import load_dotenv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "."

EMBED_COLOR = 0xFFFFFF
# 0x242429
# 16566995
# 0x36393F is embed color i think

DEV_CMD = {"shutdown", "restart", "load", "unload", "reload", "sync"}
