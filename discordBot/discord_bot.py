import discord
from discord.ext import commands
import os
import random
import datetime
import emoji
import time
import logging

logging.basicConfig(level=logging.INFO)
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

bot.load_extension('music')
bot.load_extension('tibia')
bot.run(os.getenv('DISCORD_TOKEN'))
