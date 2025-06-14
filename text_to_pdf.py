from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from weasyprint import HTML
import os
import tempfile
import logging
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Error handler
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error("Exception while handling update:", exc_info=context.error)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("❌ មានបញ្ហាក្នុងប្រតិបត្តិការណ៍។ សូមសាកល្បងម្ដងទៀត។")

# Main PDF generation handler
async def text_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ សូមវាយ: /texttopdf អត្ថបទដែលអ្នកចង់បម្លែង")
        return

    user_text = " ".join(context.args)

    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @font-face {{
                font-family: 'Noto Sans Khmer';
                src: url('file:///app/NotoSansKhmer-Regular.ttf');
            }}
            body {{
                font-family: 'Noto Sans Khmer', sans-serif;
                font-size: 16pt;
                line-height: 1.8;
                margin: 2cm;
            }}
        </style>
    </head>
    <body>
        <p>{user_text}</p>
    </body>
    </html>
    """

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name
        try:
            HTML(string=html_content).write_pdf(tmp_path)
            with open(tmp_path, "rb") as f:
                await update.message.reply_document(document=f, filename="text.pdf")
        except Exception as e:
            logging.error("PDF generation failed", exc_info=True)
            await update.message.reply_text(f"❌ មានបញ្ហាក្នុងការបង្កើត PDF: {e}")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

# Run bot (if this script is executed directly)
if __name__ == "__main__":
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        print("❌ BOT_TOKEN not found in environment variables.")
        exit(1)

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("texttopdf", text_to_pdf))
    app.add_error_handler(error_handler)
    app.run_polling()
