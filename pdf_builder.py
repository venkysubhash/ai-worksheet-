# ==========================================================
# CAIGS ULTRA AI – CHILD WORKSHEET PDF BUILDER (PREMIUM)
# COLORFUL • EMOJI HEAVY • PRINT OPTIMIZED • 12+ PAGES
# ==========================================================

import os
import random
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
    HRFlowable,
    Image
)
from reportlab.platypus import Table
from reportlab.lib import colors
# from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader, PdfWriter
import os
from reportlab.platypus import KeepTogether
TEMP_PDF = "temp_image_pages.pdf"

if os.path.exists(TEMP_PDF):
    try:
        os.remove(TEMP_PDF)
    except:
        pass
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from emoji_engine import (
    parse_text_emoji_only,
    parse_text_heavy_emoji,
    parse_header_with_emoji
)

# ==========================================================
# FONT REGISTRATION
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

pdfmetrics.registerFont(
    TTFont("BodyFont", os.path.join(BASE_DIR, "DejaVuSans.ttf"))
)

pdfmetrics.registerFont(
    TTFont("HeadingFont", os.path.join(BASE_DIR, "DejaVuSans-Bold.ttf"))
)

# ==========================================================
# COLOR PALETTE
# ==========================================================

PRIMARY = colors.HexColor("#1565C0")
SECTION_BG = colors.HexColor("#E3F2FD")
ALT_ROW = colors.HexColor("#FFF8E1")
LIGHT_BOX = colors.HexColor("#F5F5F5")
TEXT_COLOR = colors.HexColor("#212121")

# ==========================================================
# PAGE NUMBER
# ==========================================================

def add_page_number(canvas, doc):
    page_num = canvas.getPageNumber()
    canvas.setFont("BodyFont", 9)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(7.8 * inch, 0.5 * inch,
                           f"Worksheet | Page {page_num}")

# ==========================================================
# EMOJI INLINE RENDER (LARGE)
# ==========================================================

def render_emoji_text(text, style, emoji_mode="heavy"):

    if emoji_mode == "emoji_only":
        parts = parse_text_emoji_only(text)
    else:
        parts = parse_text_heavy_emoji(text)

    html = ""

    for kind, value in parts:
        if kind == "TEXT":
            # Check if the text contains raw emoji characters
            # and try to find image for them
            if contains_emoji(value):
                # Try to find emoji image for each emoji character in text
                processed = process_raw_emojis(value)
                html += processed
            else:
                html += value
        elif kind == "IMAGE" and os.path.exists(value):
            html += (
                f'<img src="{value}" '
                f'width="26" height="26" '
                f'valign="middle"/> '
            )

    return Paragraph(html, style)


def contains_emoji(text):
    """Check if text contains emoji characters"""
    if not text:
        return False
    for char in text:
        if ord(char) >= 0x2600 or 0x1F300 <= ord(char) <= 0x1F9FF:
            return True
    return False


def process_raw_emojis(text):
    """Process raw emoji characters and try to convert to images"""
    if not text:
        return text
    
    from emoji_engine import get_emoji_image_path
    
    result = ""
    for char in text:
        # Check if it's an emoji (various Unicode ranges)
        if (0x2600 <= ord(char) <= 0x26FF or  # Miscellaneous Symbols
            0x1F300 <= ord(char) <= 0x1F9FF or  # Emoticons, Misc Symbols, Transport, Weather, etc.
            0x2700 <= ord(char) <= 0x27BF):     # Dingbats
            image_path = get_emoji_image_path(char)
            if image_path and os.path.exists(image_path):
                result += f'<img src="{image_path}" width="26" height="26" valign="middle"/> '
            else:
                result += char  # Fall back to emoji character
        else:
            result += char
    return result

# ==========================================================
# SECTION HEADER
# ==========================================================

def build_section_header(title):

    style = ParagraphStyle(
        name="SectionHeader",
        fontName="HeadingFont",
        fontSize=22,
        leading=26, 
        textColor=PRIMARY,
        spaceAfter=12
    )

    header = render_emoji_text(title, style)

    box = Table([[header]], colWidths=[6.5 * inch])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), SECTION_BG),
        ("BOX", (0,0), (-1,-1), 1, colors.grey),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))

    return box

# ==========================================================
# BLANK WRITING BOX
# ==========================================================

def build_blank_box(height=3):

    box = Table(
        [[""]],
        colWidths=[6.5 * inch],
        rowHeights=[height * inch]
    )

    box.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 1, colors.grey),
        ("BACKGROUND", (0,0), (-1,-1), LIGHT_BOX),
    ]))

    return box

# ==========================================================
# MAIN STUDENT WORKSHEET
# ==========================================================

def build_student_pdf(path, data):

    doc = SimpleDocTemplate(
    path,
    pagesize=A4,
    rightMargin=40,
    leftMargin=40,
    topMargin=0,     # remove top gap
    bottomMargin=50
)

    elements = []



    body_style = ParagraphStyle(
    name="Body",
    fontName="BodyFont",
    fontSize=15,      # increased from 13
    leading=24,       # increased spacing
    textColor=TEXT_COLOR,
    spaceAfter=10
)
    logo = data.get("header_logo")
    header_text = data.get("header_text")

    from reportlab.platypus import Table, TableStyle
    from reportlab.lib.units import inch
    from PIL import Image as PILImage

    # ======================================================
    # HEADER IMAGE (SAFE)
    # ======================================================

    if logo and os.path.exists(logo):

        pil_img = PILImage.open(logo)
        aspect = pil_img.height / pil_img.width

        header_img = Image(
            logo,
            width=doc.width,
            height=doc.width * aspect
        )

        header_table = Table([[header_img]], colWidths=[doc.width])

        header_table.setStyle(TableStyle([
            ("LEFTPADDING", (0,0), (-1,-1), 0),
            ("RIGHTPADDING", (0,0), (-1,-1), 0),
            ("TOPPADDING", (0,0), (-1,-1), 0),
            ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ]))

        elements.append(header_table)

    # ======================================================
    # HEADER TEXT (OPTIONAL)
    # ======================================================

    if header_text:
        header_style = ParagraphStyle(
            name="HeaderText",
            fontName="HeadingFont",
            fontSize=16,
            alignment=1,
            spaceAfter=20
        )

        elements.append(Paragraph(header_text, header_style))
        # ======================================================
    # COVER PAGE
    # ======================================================

    

    title_style = ParagraphStyle(
        name="CoverTitle",
        fontName="HeadingFont",
        fontSize=34,     # increased from 30
        leading=38,      # added for better spacing
        alignment=1,
        textColor=PRIMARY,
        spaceAfter=30
    )

    elements.append(render_emoji_text(
        data["chapter"] + " 📘",
        title_style,
        emoji_mode="heavy"
    ))

    elements.append(Spacer(1, 20))

    # ======================================================
    # SUMMARY PAGE
    # ======================================================

    # ======================================================
# SUMMARY PAGE (SAFE RENDER)
# ======================================================

    summary = data.get("summary_section", {})

    # Show only if summary exists
    if summary.get("summary_lines"):

        elements.append(build_section_header("📖 Summary"))
        elements.append(Spacer(1, 12))

        # Chapter Title
        elements.append(
            render_emoji_text(
                summary.get("chapter_title", ""),
                body_style
            )
        )
        elements.append(Spacer(1, 10))

        # Summary Content
        for line in summary.get("summary_lines", []):
            if line.strip():
                elements.append(render_emoji_text(line, body_style))
                elements.append(Spacer(1, 5))

        elements.append(Spacer(1, 15))


    # ---------------- NEW WORDS ----------------

    new_words = summary.get("new_words", [])

    if new_words:
        elements.append(build_section_header("📚 New Words"))
        elements.append(Spacer(1, 8))

        new_words_text = ", ".join(new_words)
        elements.append(
            render_emoji_text(new_words_text, body_style, "heavy")
        )

        elements.append(Spacer(1, 15))
    # ---------------- DIFFICULT WORDS ----------------

    difficult_words = summary.get("difficult_words", [])

    if difficult_words:
        elements.append(build_section_header("⚡ Difficult Words"))
        elements.append(Spacer(1, 8))

        for word, meaning in difficult_words:
            elements.append(
                render_emoji_text(f"{word} – {meaning}", body_style)
            )
            elements.append(Spacer(1, 5))

    # ======================================================
    # TRUE / FALSE (2 PAGES)
    # ======================================================
# ======================================================
# TRUE / FALSE
# ======================================================

    elements.append(build_section_header("❓ True or False"))
    elements.append(Spacer(1, 15))

    tf_data = data.get("true_false", [])

    for i, item in enumerate(tf_data, 1):

        if not isinstance(item, tuple) or len(item) != 2:
            continue

        question, answer = item

        question_text = f"{i}. {question}"
        elements.append(render_emoji_text(question_text, body_style))

        checkbox = Paragraph("☐ TRUE        ☐ FALSE", body_style)
        elements.append(checkbox)
        elements.append(Spacer(1, 12))

    elements.append(PageBreak())

    # ======================================================
    # FILL IN THE BLANKS
    # ======================================================

    elements.append(build_section_header("✏ Fill in the Blanks"))
    elements.append(Spacer(1, 15))

    for i, (q, _) in enumerate(data["fill_blanks"], 1):
        question_text = f"{i}. {q}"
        elements.append(render_emoji_text(question_text, body_style))
        elements.append(Spacer(1, 10))

    elements.append(PageBreak())

    # ======================================================
    # MCQ SECTION (2 COLUMN OPTIONS)
    # ======================================================

    elements.append(build_section_header("📝 Multiple Choice Questions"))
    elements.append(Spacer(1, 15))

    for i, item in enumerate(data.get("mcqs", []), 1):

        if not isinstance(item, tuple) or len(item) < 2:
            continue

        q = item[0]
        options = item[1]

        if not isinstance(options, list):
            continue

        # Ensure exactly 4 options
        while len(options) < 4:
            options.append("Option")

        options = options[:4]

        elements.append(render_emoji_text(f"{i}. {q}", body_style))
        elements.append(Spacer(1, 6))

        A = f"A. {options[0]}"
        B = f"B. {options[1]}"
        C = f"C. {options[2]}"
        D = f"D. {options[3]}"

        row1 = [
            render_emoji_text(A, body_style),
            render_emoji_text(B, body_style)
        ]
        row2 = [
            render_emoji_text(C, body_style),
            render_emoji_text(D, body_style)
        ]

        option_table = Table(
            [row1, row2],
            colWidths=[3.2 * inch, 3.2 * inch]
        )

        option_table.setStyle(TableStyle([
            ("LEFTPADDING", (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ]))

        elements.append(option_table)
        elements.append(Spacer(1, 18))

    elements.append(PageBreak())


 # ======================================================
# 🎯 MATCH THE FOLLOWING (ALWAYS RENDER IF DATA EXISTS)
# ======================================================

    pairs = data.get("match_general", [])

    # convert to tuple if needed
    pairs = [
        tuple(p) for p in pairs
        if isinstance(p, (list, tuple)) and len(p) == 2
    ]

    # 🔴 ONLY REQUIREMENT: at least 1 pair
    if pairs:

        import random
        pairs = pairs[:10]  # limit to 10

        left = [p[0] for p in pairs]
        right = [p[1] for p in pairs]

        random.shuffle(right)

        elements.append(build_section_header("🎯 Match the Following"))
        elements.append(Spacer(1, 10))

        left_data = [
            [render_emoji_text(f"{i+1}. {item}", body_style)]
            for i, item in enumerate(left)
        ]

        right_data = [
            [render_emoji_text(f"{chr(65+i)}. {item}", body_style)]
            for i, item in enumerate(right)
        ]

        table = Table(
            [[Table(left_data), Table(right_data)]],
            colWidths=[3.2 * inch, 3.2 * inch]
        )

        elements.append(table)
        elements.append(Spacer(1, 20))
# ======================================================
# 🧠 IQ CHALLENGE ZONE (AI GENERATED – ADVANCED)
# ======================================================

    iq_data = data.get("iq_section", [])

    # strict: require valid AI data
    iq_data = [
        q for q in iq_data
        if isinstance(q, dict) and q.get("question")
    ]

    # limit to 6–8 high-quality questions
    iq_data = iq_data[:8]

    if iq_data:

        elements.append(build_section_header("🧠 IQ Challenge Zone"))
        elements.append(Spacer(1, 10))

        levels = ["🟢 Easy", "🟡 Medium", "🔴 Hard", "🔥 Expert"]

        for i, item in enumerate(iq_data, 1):

            level = levels[i % len(levels)]

            text = f"{i}. {level} – {item.get('type','Thinking')}: {item.get('question','')}"
            elements.append(render_emoji_text(text, body_style))
            elements.append(Spacer(1, 8))

            # answer box (forces thinking)
            elements.append(build_blank_box(1.5))
            elements.append(Spacer(1, 12))

    # ======================================================
    # ILLUSTRATION + HOMEWORK
    # ======================================================

    elements.append(build_section_header("🎨 Draw and Write"))
    elements.append(Spacer(1, 15))

    elements.append(render_emoji_text(
        data["illustration"]["drawing"],
        body_style
    ))

    elements.append(Spacer(1, 15))
    elements.append(build_blank_box(4))

    elements.append(Spacer(1, 20))

    elements.append(render_emoji_text(
        data["illustration"]["writing"],
        body_style
    ))

    elements.append(Spacer(1, 15))
    elements.append(build_blank_box(2))
    elements.append(PageBreak())

# ======================================================
# 🎮 CHALLENGE ARENA – FULL GAMIFIED PAGE
# ======================================================

    elements.append(build_section_header("🎮 Challenge Arena"))
    elements.append(Spacer(1, 15))

    arena = data.get("challenge_arena", {})

    # ---------------- TREASURE HUNT ----------------
    elements.append(render_emoji_text("🗺️ Treasure Hunt", body_style))
    elements.append(Spacer(1, 10))

    treasure = arena.get("treasure_hunt", [])
    if treasure:
        for i, clue in enumerate(treasure, 1):
            elements.append(render_emoji_text(f"{i}. {clue}", body_style))
            elements.append(Spacer(1, 6))
    else:
        elements.append(render_emoji_text("No tasks available", body_style))

    elements.append(Spacer(1, 15))

    # ---------------- BOSS BATTLE ----------------
    elements.append(render_emoji_text("⚔️ Boss Battle", body_style))
    elements.append(Spacer(1, 8))

    boss = arena.get("boss_battle", "")
    elements.append(render_emoji_text(boss if boss else "No challenge available", body_style))

    elements.append(Spacer(1, 10))
    elements.append(build_blank_box(2))

    elements.append(Spacer(1, 15))

    # ---------------- EMOJI CIPHER ----------------
    elements.append(render_emoji_text("🔐 Emoji Cipher", body_style))
    elements.append(Spacer(1, 10))

    cipher = arena.get("emoji_cipher", [])
    if cipher:
        for emoji, word in cipher:
            elements.append(render_emoji_text(f"{emoji} → ________", body_style))
            elements.append(Spacer(1, 6))
    else:
        elements.append(render_emoji_text("No cipher available", body_style))

    elements.append(Spacer(1, 10))
    elements.append(build_blank_box(1.5))

    elements.append(Spacer(1, 15))

    # ---------------- WORD BUILDER ----------------
    elements.append(render_emoji_text("🔤 Word Builder", body_style))
    elements.append(Spacer(1, 10))

    words = arena.get("word_builder", [])
    if words:
        for part, full in words:
            elements.append(render_emoji_text(f"{part} → ________", body_style))
            elements.append(Spacer(1, 6))
    else:
        elements.append(render_emoji_text("No words available", body_style))

    elements.append(Spacer(1, 15))

    # ---------------- RAPID FIRE ----------------
    elements.append(render_emoji_text("🔥 Rapid Fire Round", body_style))
    elements.append(Spacer(1, 10))

    rapid = arena.get("rapid_fire", [])
    if rapid:
        for q in rapid:
            elements.append(render_emoji_text(f"• {q}", body_style))
            elements.append(Spacer(1, 4))
    else:
        elements.append(render_emoji_text("No questions available", body_style))

    elements.append(Spacer(1, 15))

    # ---------------- ROLE PLAY ----------------
    elements.append(render_emoji_text("🎭 Role Play Challenge", body_style))
    elements.append(Spacer(1, 8))

    role = arena.get("role_play", "")
    elements.append(render_emoji_text(role if role else "No role play available", body_style))

    elements.append(Spacer(1, 10))
    elements.append(build_blank_box(2))
    # 7️⃣ XP System Display
    elements.append(render_emoji_text("XP Progress Tracker", body_style))
    elements.append(Spacer(1, 6))
    elements.append(render_emoji_text("Beginner (0-30) | Explorer (31-60) | Master (61+)", body_style))

    elements.append(Spacer(1, 15))

    # 8️⃣ Achievement Badges
    elements.append(render_emoji_text("Achievement Badges", body_style))
    elements.append(Spacer(1, 6))
    elements.append(render_emoji_text("Perfect Score | Critical Thinker | Speed Master | Accuracy Champion", body_style))
# ======================================================
# EXTRACTED IMAGES FROM ORIGINAL PDF
# ================
    # ======================================================
    # BUILD DOCUMENT
    # ======================================================

    doc.build(
        elements,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )
    append_image_pages(path, data.get("extracted_images", []))



def append_image_pages(main_pdf_path, images):

    if not images:
        return

    temp_pdf = "temp_image_pages.pdf"

    # remove old temp file if locked
    if os.path.exists(temp_pdf):
        try:
            os.remove(temp_pdf)
        except:
            pass

    c = canvas.Canvas(temp_pdf, pagesize=A4)
    page_width, page_height = A4

    half_width = page_width / 2
    half_height = page_height / 2

    for i in range(0, len(images), 4):

        group = images[i:i+4]

        positions = [
            (0, half_height),            # Top-left
            (half_width, half_height),   # Top-right
            (0, 0),                      # Bottom-left
            (half_width, 0)              # Bottom-right
        ]

        for img_path, (x, y) in zip(group, positions):

            if os.path.exists(img_path):
                c.drawImage(
                    img_path,
                    x,
                    y,
                    width=half_width,
                    height=half_height,
                    preserveAspectRatio=True,
                    anchor='c'
                )

        c.showPage()

    c.save()

    # Merge with original PDF
    writer = PdfWriter()

    with open(main_pdf_path, "rb") as main_file:
        main_reader = PdfReader(main_file)

        for page in main_reader.pages:
            writer.add_page(page)

    with open(temp_pdf, "rb") as image_file:
        image_reader = PdfReader(image_file)

        for page in image_reader.pages:
            writer.add_page(page)

    with open(main_pdf_path, "wb") as f:
        writer.write(f)

    # safely delete temp file
    try:
        os.remove(temp_pdf)
    except:
        pass
# ==========================================================
# TEACHER ANSWER KEY (CLEAN)
# ==========================================================

def build_teacher_pdf(path, data):

    doc = SimpleDocTemplate(path, pagesize=A4)
    elements = []

    style = ParagraphStyle(
        name="Teacher",
        fontName="BodyFont",
        fontSize=12,
        leading=18
    )

    elements.append(Paragraph("Teacher Answer Key", style))
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("True/False", style))
    for i, (_, ans) in enumerate(data["true_false"], 1):
        elements.append(Paragraph(f"{i}. {ans}", style))

    elements.append(PageBreak())

    elements.append(Paragraph("Fill in the Blanks", style))
    for i, (_, ans) in enumerate(data["fill_blanks"], 1):
        elements.append(Paragraph(f"{i}. {ans}", style))

    elements.append(PageBreak())

    elements.append(Paragraph("MCQ Answers", style))
    for i, (_, _, ans) in enumerate(data["mcqs"], 1):
        elements.append(Paragraph(f"{i}. {ans}", style))

    doc.build(elements)