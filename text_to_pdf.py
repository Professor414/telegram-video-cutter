import os
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

# Import ไลบรารีใหม่: WeasyPrint
from weasyprint import HTML

# --- ការកំណត់ពុម្ពអក្សរ (แนะนำให้ใช้ Noto Sans Khmer) ---
FONT_FILENAME = "NotoSansKhmer-Regular.ttf"
FONT_NAME_CSS = "NotoSansKhmer" # ឈ្មោះសម្រាប់ប្រើក្នុង CSS

# ស្វែងរកទីតាំងពិតប្រាកដរបស់ไฟล์កូដ
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(SCRIPT_DIR, FONT_FILENAME)


def get_handler():
    """ ត្រឡប់ handler សម្រាប់បញ្ជា Telegram bot """
    return CommandHandler("texttopdf", text_to_pdf)


async def text_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ បង្កើតឯកសារ PDF ពីអត្ថបទដែលអ្នកប្រើប្រាស់បានផ្ញើ ដោយប្រើ WeasyPrint """
    if not context.args:
        await update.message.reply_text("⚠️ សូមប្រើ: `/texttopdf អត្ថបទដែលអ្នកចង់សរសេរ…`")
        return

    user_text = " ".join(context.args)

    # ពិនិត្យមើលថាតើไฟล์ពុម្ពអក្សរមានឬអត់
    if not os.path.exists(FONT_PATH):
        await update.message.reply_text(f"❌ រកមិនឃើញไฟล์ពុម្ពអក្សរ `{FONT_FILENAME}` ទេ។")
        return

    # --- ការបង្កើត PDF ដោយប្រើ WeasyPrint ---
    output_file = f"{update.message.from_user.id}_output.pdf"
    
    # 1. បំប្លែង \n (បន្ទាត់ថ្មី) ទៅជា <br> សម្រាប់ HTML
    formatted_text_html = user_text.replace('\n', '<br>')

    # 2. បង្កើតเนื้อหา HTML และ CSS
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @font-face {{
                font-family: '{FONT_NAME_CSS}';
                src: url('file://{FONT_PATH}');
            }}
            body {{
                font-family: '{FONT_NAME_CSS}', sans-serif;
                font-size: 14pt;
                line-height: 1.8;
                margin: 1in;
            }}
        </style>
    </head>
    <body>
        {formatted_text_html}
    </body>
    </html>
    """

    # 3. បង្កើតឯកសារ PDF
    try:
        html = HTML(string=html_content)
        html.write_pdf(output_file)
    except Exception as e:
        await update.message.reply_text(f"❌ មានបញ្ហាក្នុងការបង្កើត PDF: {e}")
        return

    # 4. ផ្ញើឯកសារ PDF ទៅឲ្យអ្នកប្រើប្រាស់
    try:
        with open(output_file, "rb") as f:
            await update.message.reply_document(document=f, filename="អត្ថបទខ្មែរ.pdf")
    finally:
        if os.path.exists(output_file):
            os.remove(output_file)
