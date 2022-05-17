import discord
import asyncio
import os

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
SOUND_PATH = os.getenv('SOUND_PATH')

class VoiceBot(commands.Cog):
    def __init__(self, bot):
        print('Starting Voice Bot')
        

    @commands.command(
        name='store_coords',
        pass_context=True
    )
    async def rick_roll(self, ctx):
        user = ctx.message.author
        voice_channel = user.voice.channel
        await self._play_audio(f'{SOUND_PATH}rickroll.mp3', voice_channel)


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
    bot.add_cog(VoiceBot(bot))