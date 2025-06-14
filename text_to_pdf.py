import os
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

# Import  компоненты Platypus ที่จำเป็น
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

# --- ការកំណត់ពុម្ពអក្សរ (Font Configuration) ---
# សូមប្រាកដថាអ្នកបានទាញយក និងដាក់ไฟล์ font នេះក្នុងថតតែមួយជាមួយកូដ
FONT_FILENAME = "KhmerOS_muol.ttf" 
FONT_NAME = "KhmerOSMuol" # ឈ្មោះសម្រាប់ប្រើក្នុងកូដ

# ស្វែងរកទីតាំងពិតប្រាកដរបស់ไฟล์កូដ
# This makes sure the bot can find the font file
SCRIPT_DIR = os.path.dirname(__file__)
FONT_PATH = os.path.join(SCRIPT_DIR, FONT_FILENAME)


def get_handler():
    """ trả về trình xử lý lệnh cho bot Telegram """
    return CommandHandler("texttopdf", text_to_pdf)


async def text_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ สร้างไฟล์ PDF จากข้อความที่ผู้ใช้ส่งมา """
    if not context.args:
        await update.message.reply_text("⚠️ សូមប្រើ: `/texttopdf អត្ថបទដែលអ្នកចង់សរសេរ…`")
        return

    user_text = " ".join(context.args)

    # ពិនិត្យមើលថាតើไฟล์ពុម្ពអក្សរមានឬអត់
    if not os.path.exists(FONT_PATH):
        await update.message.reply_text(f"❌ រកមិនឃើញไฟล์ពុម្ពអក្សរ `{FONT_FILENAME}` ទេ។\nសូមទាញយក និងដាក់វានៅក្នុងថតតែមួយជាមួយកូដ។")
        return

    # --- ការបង្កើត PDF ដោយប្រើ Platypus ---
    output_file = f"{update.message.from_user.id}_output.pdf"
    
    # 1. ចុះឈ្មោះពុម្ពអក្សរខ្មែរ
    pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))

    # 2. បង្កើតเอกสาร PDF
    doc = SimpleDocTemplate(output_file, pagesize=A4,
                            rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)

    # 3. បង្កើត Style សម្រាប់អត្ថបទខ្មែរ
    khmer_style = ParagraphStyle(
        'KhmerStyle',
        fontName=FONT_NAME,
        fontSize=14,
        leading=24,  # កម្ពស់រវាងបន្ទាត់ (Line spacing)
    )

    # 4. បំប្លែង \n (បន្ទាត់ថ្មី) ទៅជា <br/> ដែល Paragraph អាចយល់ได้
    formatted_text = user_text.replace('\n', '<br/>')

    # 5. បង្កើត Paragraph object ហើយដាក់ក្នុង story
    story = []
    p = Paragraph(formatted_text, khmer_style)
    story.append(p)

    # 6. สร้างไฟล์ PDF
    try:
        doc.build(story)
    except Exception as e:
        print(f"Error building PDF: {e}")
        await update.message.reply_text(f"❌ មានបញ្ហាក្នុងការបង្កើត PDF: {e}")
        return

    # 7. ส่งไฟล์ PDF ទៅให้ผู้ใช้
    try:
        with open(output_file, "rb") as f:
            await update.message.reply_document(document=f, filename="អត្ថបទ.pdf")
    finally:
        # 8. ลบไฟล์ชั่วคราวหลังส่งเสร็จ
        if os.path.exists(output_file):
            os.remove(output_file)
