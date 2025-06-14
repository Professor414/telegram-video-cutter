import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import subprocess
import glob

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("splitter_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_videos = {}

@app.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply(
        "🤖 សួស្តី! ខ្ញុំអាចជួយអ្នកបែងចែកវីដេអូ 📽️\n\n"
        "▶️ សូមផ្ញើវីដេអូមក Bot\n"
        "▶️ បន្ទាប់មកប្រើ /split <នាទី>\n"
        "ឧ. `/split 5` ដើម្បីបែងចែករៀងរាល់ 5 នាទី។"
    )

@app.on_message(filters.video & filters.private)
async def save_video(_, message: Message):
    user_id = message.from_user.id
    file = await message.download()
    user_videos[user_id] = file
    await message.reply("✅ បានទទួលវីដេអូ! ប្រើ /split <នាទី>")

@app.on_message(filters.command("split"))
async def split_video(_, message: Message):
    user_id = message.from_user.id
    args = message.command

    if user_id not in user_videos:
        await message.reply("⚠️ សូមផ្ញើវីដេអូមុនសិន។")
        return

    if len(args) != 2 or not args[1].isdigit():
        await message.reply("❌ ប្រើ /split <នាទី> ឧ. /split 5")
        return

    minutes = int(args[1])
    seconds = minutes * 60
    input_path = user_videos[user_id]
    output_pattern = f"{user_id}_part_%03d.mp4"

    await message.reply("🔪 กំពុងបែងចែកវីដេអូ...")

    cmd = [
        "ffmpeg", "-i", input_path, "-c", "copy", "-map", "0",
        "-f", "segment", "-segment_time", str(seconds),
        "-reset_timestamps", "1", output_pattern
    ]

    try:
        subprocess.run(cmd, check=True)
        segments = sorted(glob.glob(f"{user_id}_part_*.mp4"))

        for part in segments:
            await message.reply_video(part)
            os.remove(part)

    except Exception as e:
        await message.reply(f"❌ បរាជ័យក្នុងការកាត់៖ {e}")

    finally:
        os.remove(input_path)
        user_videos.pop(user_id, None)

if __name__ == "__main__":
    print("✅ Split Video Bot is running...")
    app.run()
