from fpdf import FPDF
import os
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

def get_handler():
    return CommandHandler("texttopdf", text_to_pdf)

async def text_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("⚠️ សូមបញ្ចូលអត្ថបទជាមួយនឹង /texttopdf")
        return

    # PDF setup
    pdf = FPDF()
    pdf.add_page()

    font_path = "KhmerFont.ttf"
    if not os.path.exists(font_path):
        await update.message.reply_text("❌ មិនមាន KhmerFont.ttf សម្រាប់អក្សរខ្មែរ")
        return

    pdf.add_font("Khmer", "", font_path, uni=True)
    pdf.set_font("Khmer", size=20)

    pdf.multi_cell(0, 10, text)
    file_name = f"{update.message.from_user.id}_output.pdf"
    pdf.output(file_name)

    # Send PDF back
    await update.message.reply_document(document=open(file_name, "rb"))
    os.remove(file_name)
