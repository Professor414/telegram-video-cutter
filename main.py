import os
import asyncio
from pyrogram import Client, filters
from moviepy.editor import VideoFileClip

# Load API credentials from environment variables
api_id = int(os.getenv("API_ID", "0"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

if not all([api_id, api_hash, bot_token]):
    raise EnvironmentError("❌ API_ID, API_HASH, or BOT_TOKEN is missing from environment variables.")

app = Client("split_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Receive and store video file
@app.on_message(filters.video & filters.private)
async def receive_video(client, message):
    user_id = message.from_user.id
    video_path = f"{user_id}_input.mp4"

    await message.download(file_name=video_path)
    await message.reply_text(
        "✅ បានទទួលវីដេអូរួចហើយ!\n\n"
        "➡️ សូមប្រើបញ្ជា: /split <នាទី> ដើម្បីកាត់វីដេអូ\n"
        "ឧ. /split 5"
    )

# Handle the /split command
@app.on_message(filters.command("split") & filters.private)
async def split_video(client, message):
    user_id = message.from_user.id
    video_path = f"{user_id}_input.mp4"

    if not os.path.exists(video_path):
        await message.reply_text("⚠️ សូមផ្ញើវីដេអូមុនសិនមុននឹងប្រើ /split")
        return

    try:
        parts = message.text.strip().split()
        if len(parts) < 2 or not parts[1].isdigit():
            raise ValueError

        minutes = int(parts[1])
        duration_per_clip = minutes * 60
    except ValueError:
        await message.reply_text("❌ បញ្ជាមិនត្រឹមត្រូវ។ សូមប្រើ /split <នាទី> ឧ. /split 3")
        return

    try:
        clip = VideoFileClip(video_path)
        total_duration = int(clip.duration)
        segment_count = (total_duration + duration_per_clip - 1) // duration_per_clip

        await message.reply_text(f"🔪 กำลังแยกវីដេអូជា {segment_count} ផ្នែក...")

        for i in range(segment_count):
            start = i * duration_per_clip
            end = min((i + 1) * duration_per_clip, total_duration)
            subclip = clip.subclip(start, end)

            output_path = f"{user_id}_part_{i + 1}.mp4"
            subclip.write_videofile(output_path, codec="libx264", audio_codec="aac", logger=None)

            await client.send_video(chat_id=message.chat.id, video=output_path)
            os.remove(output_path)

        clip.close()
        os.remove(video_path)
        await message.reply_text("✅ កាត់វីដេអូរួចរាល់!")

    except Exception as e:
        await message.reply_text(f"❌ កំហុសកើតឡើង៖ {e}")
        if os.path.exists(video_path):
            os.remove(video_path)

# Start the bot
print("🤖 Split video bot is running...")
app.run()
