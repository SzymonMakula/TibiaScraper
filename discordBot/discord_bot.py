import discord
from discord.ext import commands
import os
import random
import datetime
import emoji
import time
import logging

from DatabaseConnector.DatabaseConnector import DatabaseConnector

logging.basicConfig(level=logging.INFO)
tibia_db = DatabaseConnector()
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents, chunk_guilds_at_startup=False)


@bot.event
async def on_ready():
    # connect to db and fetch random nickname
    random_nickname = list(tibia_db.get_polack_nickname())[0]
    logging.info(random_nickname)
    for guild in bot.guilds:
        member = await guild.fetch_member(bot.user.id)
        await member.edit(nick=random_nickname)


bot.load_extension("music")
bot.load_extension("tibia")
bot.run(os.getenv("DISCORD_TOKEN"))
