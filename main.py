
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import subprocess
import glob

BOT_TOKEN = os.environ.get("BOT_TOKEN")
user_video_files = {}

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    file = await update.message.video.get_file()
    input_path = f"{user_id}_input.mp4"
    await file.download_to_drive(custom_path=input_path)
    user_video_files[user_id] = input_path
    await update.message.reply_text("✅ បានទទួលវីដេអូរួច។ វាយ /split 5 ដើម្បីកាត់វាជាបំណែក 5 នាទី។")

async def split_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_video_files:
        await update.message.reply_text("⚠️ សូមផ្ញើវីដេអូជាមុនសិន។")
        return

    try:
        minutes = int(context.args[0])
        segment_time = f"00:{minutes:02d}:00"
    except:
        await update.message.reply_text("❌ ប្រើត្រឹមត្រូវ: /split 5")
        return

    input_path = user_video_files[user_id]
    output_pattern = f"{user_id}_segment_%03d.mp4"

    command = [
        "ffmpeg", "-i", input_path, "-c", "copy", "-map", "0",
        "-segment_time", segment_time, "-f", "segment",
        "-reset_timestamps", "1", output_pattern
    ]

    await update.message.reply_text("🔄 កំពុងកាត់វីដេអូ...")

    try:
        subprocess.run(command, check=True)
        segments = sorted(glob.glob(f"{user_id}_segment_*.mp4"))
        for path in segments:
            await update.message.reply_video(video=open(path, 'rb'))
            os.remove(path)
    except Exception as e:
        await update.message.reply_text(f"❌ កើតបញ្ហា: {e}")
    finally:
        os.remove(input_path)
        del user_video_files[user_id]

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(CommandHandler("split", split_command))
    print("🎬 Bot is running...")
    app.run_polling()
