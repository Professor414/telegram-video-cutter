import os
from fpdf import FPDF
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

# Constants
FONT_PATH = "NotoSansKhmer-Regular.ttf"  # make sure this file is in your project root
FONT_NAME = "KhmerOS"

def get_handler():
    return CommandHandler("texttopdf", generate_pdf)

async def generate_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the user input text
    user_text = " ".join(context.args)
    if not user_text:
        await update.message.reply_text("⚠️ សូមបញ្ចូលអត្ថបទបន្ទាប់នឹង /texttopdf")
        return

    # Check if font file exists
    if not os.path.exists(FONT_PATH):
        await update.message.reply_text(f"❌ មិនមាន {FONT_PATH} សម្រាប់អក្សរខ្មែរ។")
        return

    # Generate PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font(FONT_NAME, '', FONT_PATH, uni=True)
    pdf.set_font(FONT_NAME, size=19)
    pdf.multi_cell(0, 10, txt=user_text)

    # Save with unique filename
    user_id = update.message.from_user.id
    filename = f"{user_id}_output.pdf"
    pdf.output(filename)

    # Send back the PDF
    await update.message.reply_document(document=open(filename, "rb"))

    # Cleanup
    os.remove(filename)
