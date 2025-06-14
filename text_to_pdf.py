from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from fpdf import FPDF

# Command: /texttopdf Some long text
async def text_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ សូមបញ្ចូលអត្ថបទបន្ទាប់ពី /texttopdf")
        return

    text = " ".join(context.args)
    filename = f"{update.message.from_user.id}_output.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    pdf.output(filename)

    await update.message.reply_document(document=open(filename, "rb"))
    os.remove(filename)

def get_handler():
    return CommandHandler("texttopdf", text_to_pdf)
