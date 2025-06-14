import os
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT

# Path to Khmer font in root folder
FONT_NAME = "KhmerFont"
FONT_FILE = os.path.join(os.path.dirname(__file__), "KhmerFont.ttf")

def get_handler():
    return CommandHandler("texttopdf", text_to_pdf)

async def text_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "⚠️ សូមបញ្ចូលអត្ថបទជាមួយ /texttopdf ដូចជា៖\n`/texttopdf សួស្តី ពិភពលោក`", parse_mode="Markdown")
        return

    user_text = " ".join(context.args)

    if not os.path.exists(FONT_FILE):
        await update.message.reply_text("❌ មិនឃើញ KhmerFont.ttf នៅក្នុង directory!")
        return

    # Register font
    pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_FILE))

    # PDF output file
    output_path = f"{update.message.from_user.id}_output.pdf"

    # Create PDF with paragraph
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()

    khmer_style = ParagraphStyle(
        name='Khmer',
        fontName=FONT_NAME,
        fontSize=19,
        leading=20,
        alignment=TA_LEFT,
    )

    paragraph = Paragraph(user_text, khmer_style)
    doc.build([paragraph])

    # Send file to user
    with open(output_path, "rb") as pdf_file:
        await update.message.reply_document(document=pdf_file)

    os.remove(output_path)
