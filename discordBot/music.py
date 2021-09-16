import asyncio
import logging
import time

import discord
from discord.ext import commands
import queue
import youtube_dl

YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "extractaudio": True,
    "audioformat": "mp3",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",
}
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_clients = {}
        self.queues = {}

    @commands.command(name="play", help="Plays music")
    async def play(self, ctx: discord.ext.commands.Context, url: str):
        with youtube_dl.YoutubeDL(YTDL_OPTIONS) as ydl:
            if self.get_vc(ctx).is_playing():
                return self.enqueue(ctx, url)
            await self.summon(ctx)
            self.get_vc(ctx).play(
                discord.FFmpegPCMAudio(
                    ydl.extract_info(url, download=False)["formats"][0]["url"],
                    **FFMPEG_OPTIONS
                ),
                after=lambda x: self.play_next_song(ctx, x)
            )

    @commands.command(name="summon", help="Summons bot to voice channel")
    async def summon(self, ctx: discord.ext.commands.Context):
        # snap 1984
        # snap na ciebie cwelu
        if not ctx.message.author.voice:
            return await ctx.send("You are not connected to a voice channel!")
        if self.get_vc(ctx):
            logging.info(ctx.voice_client)
            return await self.get_vc(ctx).move_to(channel=ctx.message.author.voice.channel)
        self.voice_clients[ctx.guild.id] = await ctx.message.author.voice.channel.connect()

    @commands.command(name="leave", help="Leaves voice channel")
    async def leave(self, ctx: discord.ext.commands.Context):
        await self.get_vc(ctx).disconnect()
        del self.voice_clients[ctx.guild.id]

    def get_vc(self, ctx: commands.Context) -> discord.VoiceClient:
        return self.voice_clients.get(ctx.guild.id)

    def get_queue(self, ctx: commands.Context) -> queue.Queue:
        return self.queues.get(ctx.guild.id)

    def enqueue(self, ctx, url):
        if not self.get_queue(ctx):
            self.queues[ctx.guild.id] = queue.Queue()
        self.get_queue(ctx).put(url)

    def play_next_song(self, ctx, error):
        if error:
            logging.error(error)
        time.sleep(1)
        with youtube_dl.YoutubeDL(YTDL_OPTIONS) as ydl:
            self.get_vc(ctx).play(
                discord.FFmpegPCMAudio(
                    ydl.extract_info(self.get_queue(ctx).get(), download=False)["formats"][0]["url"],
                    **FFMPEG_OPTIONS
                ),
                after=lambda x: self.play_next_song(ctx, x)
            )

# TODO add asyncio loop


def setup(bot: commands.Bot):
    bot.add_cog(Music(bot))
