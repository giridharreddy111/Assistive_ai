import asyncio
import edge_tts
import os

VOICE = "en-US-GuyNeural"

async def generate_voice(text):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save("voice.mp3")

def speak(text):
    print("VOICE:", text)

    try:
        asyncio.run(generate_voice(text))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(generate_voice(text))

    os.system("start voice.mp3")