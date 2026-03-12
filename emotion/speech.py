import asyncio
import edge_tts
import os

VOICE = "en-US-GuyNeural"
OUTPUT_FILE = "voice.mp3"

async def generate_voice(text):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(OUTPUT_FILE)
    os.system(f"start {OUTPUT_FILE}")

def speak(text):
    print("VOICE:", text)

    try:
        loop = asyncio.get_event_loop()
        loop.create_task(generate_voice(text))
    except RuntimeError:
        asyncio.run(generate_voice(text))