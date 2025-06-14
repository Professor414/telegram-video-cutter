import os
from fpdf import FPDF
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

def get_handler():
    return CommandHandler("texttopdf", text_to_pdf)

async def text_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Join message parts (everything after the command)
    message_text = " ".join(context.args)

    if not message_text.strip():
        await update.message.reply_text("⚠️ សូមបញ្ចូលអត្ថបទបន្ទាប់ពី /texttopdf ដូចជា:\n/texttopdf ខ្ញុំស្រលាញ់កម្ពុជា")
        return

    try:
        # Create PDF
        pdf = FPDF()
        pdf.add_page()

        # Path to KhmerFont.ttf (must be in the same directory)
        font_path = os.path.join(os.path.dirname(__file__), "KhmerFont.ttf")

        if not os.path.isfile(font_path):
            await update.message.reply_text("❌ មិនមាន KhmerFont.ttf សម្រាប់បញ្ចូលទេ!")
            return

        # Register and set Khmer font
        pdf.add_font("KhmerFont", "", font_path, uni=True)
        pdf.set_font("KhmerFont", size=20)

        # Insert text with wrapping
        pdf.multi_cell(0, 10, message_text)

        # Output file
        filename = f"{update.message.from_user.id}_output.pdf"
        pdf.output(filename)

        # Send back PDF
        with open(filename, "rb") as f:
            await update.message.reply_document(f)

        os.remove(filename)

    except Exception as e:
        await update.message.reply_text(f"❌ បញ្ហា: {e}")
