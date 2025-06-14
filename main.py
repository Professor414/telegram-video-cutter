import os
import asyncio
from pyrogram import Client, filters
from moviepy.editor import VideoFileClip

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

app = Client("split_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Receive and store video file
@app.on_message(filters.video & filters.private)
async def receive_video(client, message):
    user_id = message.from_user.id
    video_path = f"{user_id}_input.mp4"
    await message.download(file_name=video_path)
    await message.reply_text("✅ បានទទួលវីដេអូ! បញ្ជា /split <នាទី> ដើម្បីកាត់វីដេអូ")

# Handle the /split command
@app.on_message(filters.command("split") & filters.private)
async def split_video(client, message):
    user_id = message.from_user.id
    video_path = f"{user_id}_input.mp4"
    if not os.path.exists(video_path):
        await message.reply_text("⚠️ សូមផ្ញើវីដេអូមុនសិន")
        return

    try:
        minutes = int(message.text.split()[1])
        duration_per_clip = minutes * 60
    except:
        await message.reply_text("❌ ប្រើបញ្ជា /split <នាទី> ប៉ុណ្ណោះ!")
        return

    try:
        clip = VideoFileClip(video_path)
        duration = int(clip.duration)
        parts = (duration + duration_per_clip - 1) // duration_per_clip
        await message.reply_text(f"🔪 កំពុងកាត់ជា {parts} part...")

        for i in range(parts):
            start = i * duration_per_clip
            end = min((i + 1) * duration_per_clip, duration)
            subclip = clip.subclip(start, end)
            output_path = f"{user_id}_part{i+1}.mp4"
            subclip.write_videofile(output_path, codec="libx264", audio_codec="aac")
            await client.send_video(message.chat.id, video=output_path)
            os.remove(output_path)

        clip.close()
        os.remove(video_path)
        await message.reply_text("✅ កាត់រួចរាល់!")

    except Exception as e:
        await message.reply_text(f"❌ កំហុស: {e}")
        if os.path.exists(video_path):
            os.remove(video_path)

print("🤖 Split video bot is running...")
app.run()
