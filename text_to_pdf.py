import os
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

# Import គ្រឿងផ្សំសំខាន់ៗពី Platypus ដែលអាចរៀបរៀងអក្សរខ្មែរបាន
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

# --- ការកំណត់ពុម្ពអក្សរ (ចំណុចកែសម្រួលសំខាន់ទី១) ---
# យើងប្តូរไปប្រើពុម្ពអក្សរ Khmer OS Siemreap ដែលជាស្តង់ដារ และអាចដំណើរការបានល្អ
FONT_FILENAME = "NotoSansKhmer-Regular.ttf" 
FONT_NAME = "NotoSansKhmer" # ឈ្មោះសម្រាប់ប្រើក្នុងកូដ

# ស្វែងរកទីតាំងពិតប្រាកដរបស់ไฟล์កូដ (ចំណុចកែសម្រួលសំខាន់ទី២)
# វិធីនេះធានាថា Bot រកไฟล์ font ឃើញเสมอ ទោះបីជាអ្នករត់វាមកពីទីណាក៏ដោយ
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(SCRIPT_DIR, FONT_FILENAME)


def get_handler():
    """ ត្រឡប់ handler សម្រាប់បញ្ជា Telegram bot """
    return CommandHandler("texttopdf", text_to_pdf)


async def text_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ បង្កើតឯកសារ PDF ពីអត្ថបទដែលអ្នកប្រើប្រាស់បានផ្ញើ """
    if not context.args:
        await update.message.reply_text("⚠️ សូមប្រើ: `/texttopdf អត្ថបទដែលអ្នកចង់សរសេរ…`")
        return

    user_text = " ".join(context.args)

    # ពិនិត្យមើលថាតើไฟล์ពុម្ពអក្សរមានឬអត់ (ចំណុចកែសម្រួលសំខាន់ទី៣)
    if not os.path.exists(FONT_PATH):
        # សារ Error ដែលបានปรับปรุงใหม่ នឹងបង្ហាញទីតាំងที่มันរកไม่ឃើញ
        error_message = (
            f"❌ រកមិនឃើញไฟล์ពុម្ពអក្សរ `{FONT_FILENAME}` ទេ។\n\n"
            f"Bot កំពុងព្យាយាមស្វែងរកវានៅទីតាំងនេះ:\n`{FONT_PATH}`\n\n"
            "សូមប្រាកដថាអ្នកបានទាញយក និងដាក់ไฟล์ font នៅក្នុងថតតែមួយជាមួយកូដរបស់អ្នក។"
        )
        await update.message.reply_text(error_message)
        return

    # --- ការបង្កើត PDF ដោយប្រើ Paragraph (ส่วนนี้ถูกต้องแล้ว) ---
    output_file = f"{update.message.from_user.id}_output.pdf"
    
    # 1. ចុះឈ្មោះពុម្ពអក្សរខ្មែរ
    pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))

    # 2. បង្កើតឯកសារ PDF
    doc = SimpleDocTemplate(output_file, pagesize=A4,
                            rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)

    # 3. បង្កើត Style សម្រាប់អត្ថបទខ្មែរ
    khmer_style = ParagraphStyle(
        'KhmerStyle',
        fontName=FONT_NAME,  # ប្រើពុម្ពអក្សរដែលយើងបានចុះឈ្មោះ
        fontSize=12,         # ទំហំអក្សរ (អាចปรับเปลี่ยนតាមใจ)
        leading=22,          # គម្លាតរវាងបន្ទាត់
    )

    # 4. បំប្លែង \n (បន្ទាត់ថ្មី) ទៅជា <br/> ដែល Paragraph អាចយល់បាន
    formatted_text = user_text.replace('\n', '<br/>')

    # 5. បង្កើត Paragraph object (นี่คือหัวใจของการแก้ปัญหา)
    story = [Paragraph(formatted_text, khmer_style)]

    # 6. បង្កើតឯកសារ PDF
    try:
        doc.build(story)
    except Exception as e:
        print(f"Error building PDF: {e}")
        await update.message.reply_text(f"❌ មានបញ្ហាក្នុងការបង្កើត PDF: {e}")
        return

    # 7. ផ្ញើឯកសារ PDF ទៅឲ្យអ្នកប្រើប្រាស់
    try:
        with open(output_file, "rb") as f:
            await update.message.reply_document(document=f, filename="អត្ថបទខ្មែរ.pdf")
    finally:
        # 8. លុបไฟล์បណ្ដោះអាសន្នចោលក្រោយពេលផ្ញើរួច
        if os.path.exists(output_file):
            os.remove(output_file)
