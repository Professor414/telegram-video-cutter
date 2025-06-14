from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from fpdf import FPDF
import os

async def text_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("📝 សូមវាយ /texttopdf <អត្ថបទ>")
        return

    text = " ".join(context.args)
    user_id = update.message.from_user.id
    filename = f"{user_id}_output.pdf"

    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, text)
        pdf.output(filename)

        await update.message.reply_document(document=open(filename, 'rb'), filename="result.pdf")
    except Exception as e:
        await update.message.reply_text(f"❌ បំលែងបរាជ័យ: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

def get_handler():
    return CommandHandler("texttopdf", text_to_pdf)
