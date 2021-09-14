import discord
import os
from discord.ext import commands
import random
from DatabaseConnector.DatabaseConnector import DatabaseConnector
import datetime
import emoji
import time
import logging

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv('DISCORD_TOKEN')
main_channel_name = os.getenv('MAIN_CHANNEL')

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!cho ', intents=intents)
tibia_db = DatabaseConnector()


@bot.event
async def on_ready():
    # connect to db and fetch random nickname
    random_nickname = tibia_db.get_polack_nickname()
    members = bot.get_all_members()
    for member in members:
        if member.name == "ChoBot":
            await member.edit(nick=random_nickname)


@bot.command(name='orwell', help='Responds with random Orwell quote')
async def type_orwell_quote(ctx):
    orwell_quote = get_orwell_quote()
    embed = discord.Embed(
        title="George Orwell Daily",
        value="Daily quote for your intellectual needs",
        color=3447003,
        timestamp=datetime.datetime(1984, 1, 1, 1, 1, 1, 1 ),
    )

    embed.add_field(name="His quote", value=orwell_quote)
    embed.add_field(name="Author", value="George Orwell, 1984")
    await ctx.send(content=None, embed=embed)


@bot.command(name="top.poles", help='List top 8 Polish Tibians')
async def type_top_ten_pollacks(ctx):
    page_number = 1
    embed = create_embed_of_polacks(page_number)
    bot_message = await ctx.send(content=None, embed=embed)
    await bot_message.add_reaction("◀")
    await bot_message.add_reaction("▶")

    @bot.event
    async def on_reaction_add(reaction, user):
        page_number = reaction.message.embeds[0].footer.text
        page_number = int(page_number)

        if reaction.emoji == "▶" and reaction.message == bot_message and not user.bot:
            page_number = page_number + 7
            embed = create_embed_of_polacks(page_number)
            await reaction.message.edit(content=None, embed=embed)
            await reaction.remove(user)

        if reaction.emoji == "◀" and reaction.message == bot_message and not user.bot:
            await reaction.remove(user)
            if page_number > 1:
                page_number = page_number - 7
                embed = create_embed_of_polacks(page_number)
                await reaction.message.edit(content=None, embed=embed)


@bot.command(name="tibians", help='List top Tibians')
async def type_top_ten_tibians(ctx):
    page_number = 1
    embed = create_embed_of_tibians(page_number)
    bot_message = await ctx.send(content=None, embed=embed)
    await bot_message.add_reaction("◀")
    await bot_message.add_reaction("▶")

    @bot.event
    async def on_reaction_add(reaction, user):
        page_number = reaction.message.embeds[0].footer.text
        page_number = int(page_number)

        if reaction.emoji == "▶" and reaction.message == bot_message and not user.bot:
            page_number = page_number + 6
            embed = create_embed_of_tibians(page_number)
            await reaction.message.edit(content=None, embed=embed)
            await reaction.remove(user)

        if reaction.emoji == "◀" and reaction.message == bot_message and not user.bot:
            await reaction.remove(user)
            if page_number > 1:
                page_number = page_number - 6
                embed = create_embed_of_tibians(page_number)
                await reaction.message.edit(content=None, embed=embed)


def create_embed_of_tibians(page_number):
    tibians = tibia_db.get_tibians()

    embed = discord.Embed(
        title="Top Tibians",
        value="Comprehensive list of top Tibians",
        color=3447003,
        url="https://d-art.ppstatic.pl/kadry/k/r/1/4f/28/5e47a43b03f0a_o_full.jpg",
        timestamp=datetime.datetime.now(),
    )
    for i in range(page_number, page_number + 6):
        nickname = tibians[i][0]
        level = tibians[i][1]
        vocation = tibians[i][2]
        id = tibians[i][3]
        nationality = tibians[i][4]

        embed.add_field(name="Nickname", value="[" + nickname +
                                               "](https://www.tibia.com/charactertrade/?subtopic=currentcharactertrades"
                                               "&page=details&auctionid={})".format(id), inline=False)
        embed.add_field(name="Level", value=level, inline=True)
        embed.add_field(name="Vocation", value=vocation, inline=True)
        embed.add_field(name="nationality", value=emoji.emojize(f":flag_{nationality}:"), inline=True)
        embed.add_field(name="\u200B", value="\u200B", inline=False)
        embed.set_footer(text=f"{page_number}")

    return embed



def create_embed_of_polacks(page_number):
    top_polacks = tibia_db.get_polacks() # a list of polack tuples

    embed = discord.Embed(
        title="Top Poles",
        value="Comprehensive list of top Polish Tibians",
        color=3447003,
        url="https://d-art.ppstatic.pl/kadry/k/r/1/4f/28/5e47a43b03f0a_o_full.jpg",
        timestamp=datetime.datetime.now(),
    )

    for i in range(page_number, page_number + 7):
        nickname = top_polacks[i][0]
        level = top_polacks[i][1]
        vocation = top_polacks[i][2]
        id = top_polacks[i][3]

        embed.add_field(name="Nickname", value="[" + nickname +
                                               "](https://www.tibia.com/charactertrade/?subtopic=currentcharactertrades"
                                               "&page=details&auctionid={})".format(id))
        embed.add_field(name="Level", value=level)
        embed.add_field(name="Vocation", value=vocation)
        embed.set_footer(text=page_number)

    return embed


def get_channel_id():
    channels = bot.get_all_channels()
    for channel in channels:
        if channel.name == main_channel_name:
            main_channel_id = channel.id
            return main_channel_id


def get_orwell_quote():
    with open('orwell_quotes', 'rt') as fin:
        lines = fin.readlines()
        orwell_quote = random.choice(lines)
        return orwell_quote


bot.load_extension('music')
bot.run(TOKEN)
