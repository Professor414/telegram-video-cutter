import os
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from fpdf import FPDF

# Font path from root directory
FONT_PATH = os.path.join(os.path.dirname(__file__), "KhmerFont.ttf")

def get_handler():
    return CommandHandler("texttopdf", text_to_pdf)

async def text_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if user included any arguments
    if not context.args:
        await update.message.reply_text("⚠️ សូមបញ្ចូលអត្ថបទមក /texttopdf របៀបសរសេរ ៖\n\n`/texttopdf សួស្តី​ពិភពលោក`")
        return

    # Join text parts
    user_text = " ".join(context.args)

    # Check if the font file exists
    if not os.path.exists(FONT_PATH):
        await update.message.reply_text("❌ បរាជ័យ: TTF Font file not found: KhmerFont.ttf")
        return

    # Create the PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Khmer", "", FONT_PATH, uni=True)
    pdf.set_font("Khmer", size=14)
    pdf.multi_cell(0, 10, txt=user_text)

    # Generate unique file name
    output_file = f"{update.message.from_user.id}_output.pdf"
    pdf.output(output_file)

    # Send the PDF back to user
    with open(output_file, "rb") as f:
        await update.message.reply_document(document=f)

    # Clean up file
    os.remove(output_file)
