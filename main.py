import os
from pyrogram import Client, filters
from pyrogram.types import Message
from moviepy.editor import VideoFileClip
import math
import shutil

# Load API credentials
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client(
    "split_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

MAX_FILE_SIZE = 2000 * 1024 * 1024  # 2GB

@app.on_message(filters.video & filters.private)
async def split_and_send(client: Client, message: Message):
    await message.reply_text("📥 กำลังទាញយកវីដេអូ...")
    video = message.video
    file = await message.download()
    size = os.path.getsize(file)

    if size <= MAX_FILE_SIZE:
        await message.reply_video(video=file, caption="✅ មិនចាំបាច់បំបែក")
        os.remove(file)
        return

    # ចាប់ផ្តើមបំបែក
    await message.reply_text("✂️ កំពុងបំបែកវីដេអូ...")

    clip = VideoFileClip(file)
    duration = clip.duration
    avg_bitrate = size / duration  # bytes/sec

    segment_duration = MAX_FILE_SIZE / avg_bitrate  # seconds
    segment_duration = math.floor(segment_duration)

    total_parts = math.ceil(duration / segment_duration)
    basename = os.path.splitext(file)[0]

    os.makedirs("segments", exist_ok=True)

    for i in range(total_parts):
        start = i * segment_duration
        end = min((i + 1) * segment_duration, duration)
        segment_file = f"segments/{basename}_part{i+1}.mp4"

        clip.subclip(start, end).write_videofile(
            segment_file,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            threads=4,
            logger=None
        )

        await message.reply_video(video=segment_file, caption=f"📦 Part {i+1}")
        os.remove(segment_file)

    clip.close()
    os.remove(file)
    shutil.rmtree("segments", ignore_errors=True)
    await message.reply_text("✅ បញ្ជូនរួចរាល់!")

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("👋 សួស្តី! ផ្ញើវីដេអូនៅទីនេះ ខ្ញុំនឹងបំបែកវាបើវាធំជាង 2GB។")

app.run()
