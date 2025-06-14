from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from weasyprint import HTML
import os
import tempfile

def get_handler():
    return CommandHandler("texttopdf", text_to_pdf)

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
            await update.message.reply_text(f"❌ មានបញ្ហាក្នុងការបង្កើត PDF: {e}")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
