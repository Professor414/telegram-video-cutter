import os
import subprocess
import glob
import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Load BOT_TOKEN from environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN not found in environment variables!")

# Store user's uploaded video path
user_video_files = {}

# /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 សួស្តី! ខ្ញុំអាចជួយអ្នក:\n\n"
        "🎞️ កាត់វីដេអូ: ផ្ញើវីដេអូហើយវាយ /split <នាទី>\n"
        "\nសូមចាប់ផ្តើមដោយផ្ញើវីដេអូឬវាយបញ្ជា។"
    )

# Receive video
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    file = await update.message.video.get_file()
    input_path = f"{user_id}_input.mp4"

    await file.download_to_drive(custom_path=input_path)
    user_video_files[user_id] = input_path

    await update.message.reply_text("✅ បានទទួលវីដេអូ! ប្រើ /split <នាទី> ដើម្បីកាត់។")

# /split command
async def split_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_video_files:
        await update.message.reply_text("⚠️ សូមផ្ញើវីដេអូមុនសិន")
        return

    try:
        minutes = int(context.args[0])
        segment_time = f"00:{minutes:02d}:00"
    except:
        await update.message.reply_text("❌ សូមប្រើ /split <នាទី> (ឧ. /split 5)")
        return

    input_path = user_video_files[user_id]
    output_pattern = f"{user_id}_segment_%03d.mp4"
    command = [
        "ffmpeg", "-i", input_path, "-c", "copy", "-map", "0",
        "-segment_time", segment_time, "-f", "segment",
        "-reset_timestamps", "1", output_pattern
    ]

    await update.message.reply_text("🔪 កំពុងកាត់វីដេអូ...")

    try:
        subprocess.run(command, check=True)
        segments = sorted(glob.glob(f"{user_id}_segment_*.mp4"))

        for seg in segments:
            with open(seg, "rb") as video:
                await update.message.reply_video(video=video)

        await update.message.reply_text("✅ ការកាត់វីដេអូបានជោគជ័យ!")

    except Exception as e:
        logging.error(f"Error splitting video: {e}")
        await update.message.reply_text(f"❌ មានបញ្ហា: {e}")
    finally:
        # Cleanup
        if os.path.exists(input_path):
            os.remove(input_path)
        for seg in glob.glob(f"{user_id}_segment_*.mp4"):
            os.remove(seg)
        user_video_files.pop(user_id, None)

# Error handler
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error("Unhandled exception:", exc_info=context.error)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("❌ បញ្ហាក្នុងប្រតិបត្តិការណ៍។ សូមសាកល្បងម្ដងទៀត។")

# --- Start bot ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("split", split_command))

    # Accept videos in group & private
    app.add_handler(MessageHandler(filters.VIDEO & filters.ChatType.GROUPS, handle_video))
    app.add_handler(MessageHandler(filters.VIDEO & filters.ChatType.PRIVATE, handle_video))

    app.add_error_handler(error_handler)

    print("✅ Bot is running...")
    app.run_polling()
