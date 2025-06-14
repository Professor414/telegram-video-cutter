import os
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

FONT_PATH = os.path.join(os.path.dirname(__file__), "KhmerFont.ttf")

def get_handler():
    return CommandHandler("texttopdf", text_to_pdf)

async def text_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ សូមបញ្ចូលអត្ថបទជាមួយ /texttopdf ដូចជា:\n\n`/texttopdf បងសម្បត្តិជាប្រុសស្មោះ`")
        return

    user_text = " ".join(context.args)

    if not os.path.exists(FONT_PATH):
        await update.message.reply_text("❌ KhmerFont.ttf មិនមាននៅក្នុង directory!")
        return

    output_file = f"{update.message.from_user.id}_output.pdf"

    # Register Khmer font
    pdfmetrics.registerFont(TTFont("KhmerFont", FONT_PATH))

    # Create PDF using canvas
    c = canvas.Canvas(output_file)
    c.setFont("KhmerFont", 20)
    c.drawString(72, 800, user_text)
    c.save()

    # Send the PDF
    with open(output_file, "rb") as f:
        await update.message.reply_document(document=f)

    os.remove(output_file)
