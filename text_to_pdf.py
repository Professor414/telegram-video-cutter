from fpdf import FPDF
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
import time
import os

def get_handler():
    async def text_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.message.from_user.id
        text = " ".join(context.args)

        if not text:
            await update.message.reply_text("⚠️ សូមបញ្ចូលអត្ថបទបន្ទាប់ពី /texttopdf")
            return

        # ✅ Create PDF instance
        pdf = FPDF()
        pdf.add_page()

        # ✅ Add Khmer font with Unicode support
        font_path = "KhmerOS.ttf"  # Make sure this file is present in the same directory
        if not os.path.exists(font_path):
            await update.message.reply_text("❌ មិនមាន KhmerOS.ttf សម្រាប់អក្សរខ្មែរ")
            return

        pdf.add_font("KhmerOS", "", font_path, uni=True)
        pdf.set_font("KhmerOS", "", 19)

        # ✅ Write Khmer text
        pdf.multi_cell(0, 10, txt=text)

        # ✅ Save file
        filename = f"{user_id}_{int(time.time())}_output.pdf"
        pdf.output(filename)

        # ✅ Send file to user
        await update.message.reply_document(document=open(filename, 'rb'))

        # ✅ Clean up
        os.remove(filename)

    return CommandHandler("texttopdf", text_to_pdf)
