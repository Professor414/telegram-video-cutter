import os
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
import textwrap

FONT_PATH = os.path.join(os.path.dirname(__file__), "KhmerFont.ttf")

def get_handler():
    return CommandHandler("texttopdf", text_to_pdf)

async def text_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ សូមប្រើ: `/texttopdf អត្ថបទ…`")
        return

    user_text = " ".join(context.args)
    if not os.path.exists(FONT_PATH):
        await update.message.reply_text("❌ មិនឃើញ KhmerFont.ttf")
        return

    pdfmetrics.registerFont(TTFont("KhmerFont", FONT_PATH))
    output_file = f"{update.message.from_user.id}_output.pdf"
    
    c = canvas.Canvas(output_file, pagesize=A4)
    c.setFont("KhmerFont", 16)

    width, height = A4
    x_margin = 60
    y = height - 80
    line_height = 28

    # ចែកអត្ថបទជាបន្ទាត់តូចៗ
    wrapped_lines = textwrap.wrap(user_text, width=60, break_long_words=False)

    for line in wrapped_lines:
        c.drawString(x_margin, y, line)
        y -= line_height
        if y < 50:
            c.showPage()
            c.setFont("KhmerFont", 16)
            y = height - 80

    c.save()

    with open(output_file, "rb") as f:
        await update.message.reply_document(f)
    os.remove(output_file)
