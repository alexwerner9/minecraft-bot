import discord
import asyncio
from discord.ext import commands

class VoiceBot(commands.Cog):
    def __init__(self):
        print('Starting Voice Bot')

    @commands.command(
        name='store_coords',
        pass_context=True
    )
    async def rick_roll(self, ctx):
        user = ctx.message.author
        voice_channel = user.voice.channel
        await self._play_audio('C:\\Users\\Alex\\Desktop\\Coding\\Downloads\\rickroll.mp3', voice_channel)


    @commands.command(
        name='dream_is_pog',
        pass_context=True
    )
    async def dream_is_pog(self, ctx):
        user = ctx.message.author
        voice_channel = user.voice.channel
        await self._play_audio('C:\\Users\\Alex\\Desktop\\Coding\\Downloads\\dream.mp3', voice_channel)

        
    @commands.command(
        name='stop_sound'
    )
    async def stop_sound(self, ctx):
        await self._stop_audio()
    

    async def _play_audio(self, path, voice_channel):
        if voice_channel == None:
            return
        self.vc = await voice_channel.connect()
        self.vc.play(discord.FFmpegPCMAudio(path))
        while self.vc.is_playing():
            await asyncio.sleep(1)
        self._stop_audio()

    async def _stop_audio(self):
        if self.vc.is_playing():
            self.vc.stop()
        await self.vc.disconnect()

def setup(bot):
    bot.add_cog(VoiceBot())