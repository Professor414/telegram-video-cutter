import os
import subprocess
import math
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# កំណត់ States សម្រាប់ Conversation
RECEIVING_VIDEO, RECEIVING_SPLIT_CHOICE = range(2)

# ដាក់ Token របស់អ្នកនៅទីនេះ
TELEGRAM_TOKEN = "YOUR_HTTP_API_TOKEN"

# Function ដើម្បីចាប់ផ្តើម Bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "សួស្តី! សូមផ្ញើវីដេអូដែលអ្នកចង់កាត់ (ទំហំរហូតដល់ 500MB)។\n"
        "បន្ទាប់ពីផ្ញើវីដេអូរួច សូម Reply ទៅលើសាររបស់ខ្ញុំដោយបញ្ជាក់ចំនួនផ្នែកដែលអ្នកចង់កាត់។"
    )

# Function សម្រាប់ទទួលវីដេអូ
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video_file = update.message.video
    
    # ពិនិត្យទំហំវីដេអូ (500MB = 500 * 1024 * 1024 bytes)
    if video_file.file_size > 500 * 1024 * 1024:
        await update.message.reply_text("សូមអភ័យទោស! វីដេអូមានទំហំធំជាង 500MB។")
        return ConversationHandler.END

    # រក្សាទុក file_id របស់វីដេអូ ដើម្បីប្រើនៅជំហានបន្ទាប់
    context.user_data['video_file_id'] = video_file.file_id
    
    # សួរសំណួរទៅអ្នកប្រើប្រាស់
    await update.message.reply_text("ទទួលបានវីដេអូហើយ! តើអ្នកចង់កាត់វាជាប៉ុន្មានផ្នែក? សូម Reply មកសារនេះ។")

    return RECEIVING_SPLIT_CHOICE

# Function ដើម្បីទទួលការឆ្លើយតប (ចំនួនផ្នែក) និងចាប់ផ្តើមកាត់
async def handle_split_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        num_parts = int(update.message.text)
        if num_parts <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("សូម Reply ដោយវាយជាលេខវិជ្ជមាន (ឧ. 2, 3, 4)។")
        return RECEIVING_SPLIT_CHOICE

    await update.message.reply_text(f"កំពុងដំណើរការ... សូមរង់ចាំបន្តិច។ ការកាត់ជា {num_parts} ផ្នែកអាចនឹងใช้ពេលយូរ។")

    # ទាញយកវីដេអូ
    try:
        video_file_id = context.user_data['video_file_id']
        bot = context.bot
        file = await bot.get_file(video_file_id)
        
        # បង្កើតឈ្មោះไฟล์បណ្តោះអាសន្ន
        original_video_path = f"original_{update.message.from_user.id}.mp4"
        await file.download_to_drive(original_video_path)
    except Exception as e:
        await update.message.reply_text(f"មានបញ្ហាក្នុងការទាញយកវីដេអូ: {e}")
        return ConversationHandler.END

    # ចាប់ផ្តើមកាត់វីដេអូដោយប្រើ FFmpeg
    try:
        # យកប្រវែងសរុបរបស់វីដេអូ (duration)
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", original_video_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        duration = float(result.stdout)
        part_duration = math.ceil(duration / num_parts)

        # ចាប់ផ្តើមកាត់ជាផ្នែកៗ
        for i in range(num_parts):
            start_time = i * part_duration
            output_filename = f"part_{i+1}_{update.message.from_user.id}.mp4"
            
            # បង្កើត command សម្រាប់ FFmpeg
            command = [
                'ffmpeg',
                '-i', original_video_path,
                '-ss', str(start_time),
                '-t', str(part_duration),
                '-c', 'copy', # Copy a/v stream without re-encoding, much faster!
                output_filename
            ]
            
            subprocess.run(command, check=True)
            
            # ផ្ញើផ្នែកដែលកាត់រួចទៅអ្នកប្រើប្រាស់
            await update.message.reply_text(f"កំពុងផ្ញើផ្នែកទី {i+1}/{num_parts}...")
            await bot.send_video(chat_id=update.message.chat_id, video=open(output_filename, 'rb'), supports_streaming=True)
            
            # លុបไฟล์ដែលកាត់រួចចោល ដើម្បីសន្សំសំចៃទំហំផ្ទុក
            os.remove(output_filename)

        await update.message.reply_text("ការកាត់វីដេអូរួចរាល់ហើយ!")

    except Exception as e:
        await update.message.reply_text(f"មានបញ្ហាក្នុងការកាត់វីដេអូ: {e}")
    finally:
        # លុបไฟล์វីដេអូដើមចោល
        if os.path.exists(original_video_path):
            os.remove(original_video_path)
        
        # បញ្ចប់ Conversation
        return ConversationHandler.END

# Function សម្រាប់បោះបង់
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ប្រតិបត្តិការត្រូវបានបោះបង់។")
    return ConversationHandler.END

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.VIDEO, handle_video)],
        states={
            RECEIVING_SPLIT_CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_split_choice)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)

    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
