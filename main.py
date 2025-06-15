import os
import math
import shutil
import subprocess
import asyncio
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message

# ✅ Load .env values
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("split_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

DEFAULT_SPLIT_MINUTES = 5  # ✅ Auto split in 5-minute chunks

@app.on_message(filters.video & filters.private)
async def save_video_and_split(client: Client, message: Message):
    user_id = message.from_user.id
    file_path = f"{user_id}_input.mp4"
    await message.reply_text("📥 កំពុងទាញយកវីដេអូ...")
    await message.download(file_name=file_path)
    await asyncio.sleep(1)  # 🕒 Wait to ensure file is written
    await message.reply_text(f"✅ ទាញយករួច! ✂️ กំពុងបំបែកវីដេអូជាប្រភាគ {DEFAULT_SPLIT_MINUTES} នាទី...")
    await auto_split_video(client, message, file_path, DEFAULT_SPLIT_MINUTES)

async def auto_split_video(client: Client, message: Message, file_path: str, minutes: int):
    duration_per_part = minutes * 60

    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    try:
        total_duration = float(result.stdout.decode().strip())
    except Exception as e:
        await message.reply_text(f"❌ មិនអាចអានរយៈពេលវីដេអូបានទេ\n{e}")
        return

    total_parts = math.ceil(total_duration / duration_per_part)
    os.makedirs("segments", exist_ok=True)

    for i in range(total_parts):
        start = i * duration_per_part
        output_file = f"segments/part_{i+1}.mp4"
        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error",
            "-ss", str(start), "-i", file_path,
            "-t", str(duration_per_part),
            "-c", "copy", output_file
        ]

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0 and os.path.exists(output_file):
            await client.send_video(message.chat.id, output_file, caption=f"📦 Part {i+1}")
            os.remove(output_file)
        else:
            error_log = result.stderr.decode().strip()
            print(f"❌ ffmpeg error on part {i+1}:\n{error_log}")
            await message.reply_text(f"❌ ffmpeg error on part {i+1}:\n{error_log}")

    os.remove(file_path)
    shutil.rmtree("segments", ignore_errors=True)
    await message.reply_text("✅ កាត់រួចរាល់!")

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text(
        "👋 សូមស្វាគមន៍! ផ្ញើវីដេអូ .mp4 មក bot នេះ ហើយវានឹងបំបែកវា (auto split 5 នាទី)។"
    )

print("🤖 Bot is running with FFmpeg slicing and auto-split enabled...")
app.run()
