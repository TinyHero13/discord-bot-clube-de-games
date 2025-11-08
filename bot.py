import asyncio
import os
from dotenv import load_dotenv
from discord.ext import commands
import discord
import pkgutil

load_dotenv()

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, case_insensitive=True)

async def load_all_commands():
    package_path = os.path.join(os.path.dirname(__file__), "src", "commands")
    if not os.path.isdir(package_path):
        return
    for finder, name, ispkg in pkgutil.iter_modules([package_path]):
        module_path = f"src.commands.{name}"
        try:
            await bot.load_extension(module_path)
            print(f"Loaded: {module_path}")
        except Exception as e:
            print(f"Failed to load {module_path}: {e}")

@bot.event
async def on_ready():
    print(f"Bot loaded {bot.user}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.send("Não consegui executar esse comando. Tente novamente.")
    print(f"Command error in {ctx.command}: {error}")

async def main():
    await load_all_commands()
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())