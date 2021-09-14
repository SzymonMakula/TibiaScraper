import discord
from discord.ext import commands
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


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="play", help="Plays music")
    async def play(self, ctx: discord.ext.commands.Context, url: str):
        with youtube_dl.YoutubeDL(YTDL_OPTIONS) as ydl:
            await self.summon(ctx)
            discord.utils.get(self.bot.voice_clients, guild=ctx.guild).play(
                discord.FFmpegPCMAudio(
                    ydl.extract_info(url, download=False)["formats"][0]["url"],
                    **FFMPEG_OPTIONS
                )
            )

    @commands.command(name="summon", help="Summons bot to voice channel")
    async def summon(self, ctx: discord.ext.commands.Context):
        if not ctx.message.author.voice:
            return await ctx.send("You are not connected to a voice channel!")
        await ctx.message.author.voice.channel.connect()


def setup(bot: commands.Bot):
    bot.add_cog(MusicCog(bot))
