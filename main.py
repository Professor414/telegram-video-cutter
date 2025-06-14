import os
import subprocess
import glob
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from text_to_pdf import get_handler  # PDF command handler

# Get the bot token from environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN not found in environment variables!")

# Dictionary to temporarily store uploaded video paths by user
user_video_files = {}

# /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "🤖 សូមស្វាគមន៍មកកាន់ Bot!\n\n"
        "📌 មុខងារដែលអាចប្រើបាន:\n"
        "🔹 /split <នាទី> – កាត់វីដេអូចេញជាចំណែកៗ (ត្រូវផ្ញើវីដេអូមុន)\n"
        "🔹 /texttopdf <អត្ថបទ> – បំលែងអត្ថបទទៅជា PDF (គាំទ្រភាសាខ្មែរ)\n"
        "\nℹ️ បញ្ជាក់៖ សូមបញ្ចូលពាក្យបញ្ជាដោយត្រឹមត្រូវ។"
    )
    await update.message.reply_text(message)

# Handle video file upload
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    file = await update.message.video.get_file()
    input_path = f"{user_id}_input.mp4"
    await file.download_to_drive(custom_path=input_path)
    user_video_files[user_id] = input_path
    await update.message.reply_text("✅ បានទទួលវីដេអូ! ប្រើ /split <នាទី> ដើម្បីកាត់")

# Handle /split command
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
        "-segmen
