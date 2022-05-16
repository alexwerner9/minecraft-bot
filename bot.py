import os

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
bot = commands.Bot(command_prefix = "!")
bot.remove_command('help')
TOKEN = os.getenv('DISCORD_TOKEN')

initial_extension = ['cogs.voice_bot', 'cogs.storage_bot', 'cogs.resources_bot', 'cogs.helper_bot']

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    for ext in initial_extension:
        bot.load_extension(ext)

@bot.command()
async def shutdown(ctx):
    await ctx.bot.logout()

bot.run(TOKEN)
