import asyncio
import os
import time

from discord.ext.commands import Bot
from dotenv import load_dotenv
from navertts import NaverTTS
import discord

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
VOICE_CHANNEL_ID = os.getenv('VOICE_CHANNEL_ID')

intents = discord.Intents.default()
intents.message_content = True

bot = Bot('', intents=intents)

disconnect_timer = None


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.event
async def on_message(message):
    global disconnect_timer

    if message.author.bot:
        return

    if bot.voice_clients == []:
        channel = bot.get_channel(int(VOICE_CHANNEL_ID))
        await channel.connect()

    voice = bot.voice_clients[0]

    tts = NaverTTS(message.content, speed=0)
    tts.save('tts.mp3')

    if voice.is_playing():
        voice.stop()

    voice.play(discord.FFmpegPCMAudio('tts.mp3'), after=lambda e: print('done', e))

    while voice.is_playing():
        await asyncio.sleep(1)

    # 새로운 메세지가 올라올 때마다 타이머 초기화
    if disconnect_timer:
        disconnect_timer.cancel()

    disconnect_timer = asyncio.create_task(voice_disconnect_after_delay(5.0))


async def voice_disconnect_after_delay(delay):
    await asyncio.sleep(delay)
    await voice_disconnect()


async def voice_disconnect():
    global disconnect_timer

    voice = bot.voice_clients[0]
    if voice.is_connected():
        tts = NaverTTS('저는 이만 들어가볼게요', speed=0)
        tts.save('tts.mp3')

        voice.play(discord.FFmpegPCMAudio('tts.mp3'))

        time.sleep(3)

        await voice.disconnect()


bot.run(BOT_TOKEN)
