import os
from fpdf import FPDF
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

# Path to the Khmer font
FONT_PATH = os.path.join(os.path.dirname(__file__), "KhmerOS.ttf")

def get_handler():
    return CommandHandler("texttopdf", text_to_pdf)

async def text_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = " ".join(context.args)

    if not text:
        await update.message.reply_text("⚠️ សូមបញ្ចូលអត្ថបទបន្ថែមក្រោយ /texttopdf")
        return

    if not os.path.exists(FONT_PATH):
        await update.message.reply_text("❌ មិនមាន KhmerOS.ttf សម្រាប់អក្សរខ្មែរ")
        return

    try:
        pdf = FPDF()
        pdf.add_page()

        # Register and use Khmer font
        pdf.add_font("KhmerOS", '', FONT_PATH, uni=True)
        pdf.set_font("KhmerOS", size=16)

        pdf.multi_cell(0, 10, text)

        output_path = f"{user_id}_output.pdf"
        pdf.output(output_path)

        await update.message.reply_document(document=open(output_path, "rb"))
        os.remove(output_path)

    except Exception as e:
        await update.message.reply_text(f"❌ បញ្ហា: {e}")
