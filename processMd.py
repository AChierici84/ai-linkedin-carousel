import os
import re
from glob import glob
from html import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas
from PIL import Image, ImageStat


def _markdown_inline_to_html(text):
    escaped = escape(text)
    # Convert markdown bold (**text**) to reportlab paragraph bold tags.
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)


def _draw_background(pdf, background_image_path, page_width, page_height):
    if os.path.isfile(background_image_path):
        pdf.drawImage(
            background_image_path,
            0,
            0,
            width=page_width,
            height=page_height,
            preserveAspectRatio=False,
            mask="auto",
        )


def _get_background_variants(project_root):
    pattern = os.path.join(project_root, "bkg*.*")
    background_paths = []
    for path in sorted(glob(pattern)):
        base_name = os.path.splitext(os.path.basename(path))[0]
        match = re.fullmatch(r"bkg(\d+)", base_name)
        if match:
            background_paths.append((match.group(1), path))

    return background_paths


def _is_dark_background(background_image_path):
    with Image.open(background_image_path) as image:
        rgb_image = image.convert("RGB")
        stat = ImageStat.Stat(rgb_image)
        red, green, blue = stat.mean
        brightness = 0.299 * red + 0.587 * green + 0.114 * blue
        return brightness < 145


def _draw_paragraph(
    pdf,
    paragraph,
    x,
    y,
    max_width,
    bottom_margin,
    page_height,
    top_margin,
    background_image_path,
    page_width,
):
    _, height = paragraph.wrap(max_width, page_height)
    if y - height < bottom_margin:
        pdf.showPage()
        _draw_background(pdf, background_image_path, page_width, page_height)
        y = page_height - top_margin
        _, height = paragraph.wrap(max_width, page_height)

    paragraph.drawOn(pdf, x, y - height)
    return y - height


def _build_styles(title_color, text_color):
    return {
        "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=42, leading=48, textColor=title_color),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=34, leading=40, textColor=title_color),
        "h3": ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=28, leading=34, textColor=title_color),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=20, leading=28, textColor=text_color),
        "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=20, leading=28, textColor=text_color),
    }


def _generate_pdf_for_background(processed_contents, input_file_path, background_suffix, background_image_path):
    project_root = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(project_root, "output")
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    input_name = os.path.splitext(os.path.basename(input_file_path))[0]
    output_pdf_path = os.path.join(output_dir, f"{input_name}_bkg{background_suffix}.pdf")

    page_width, page_height = A4
    left_margin = 42
    right_margin = 42
    top_margin = 54
    bottom_margin = 54
    text_width = page_width - left_margin - right_margin
    is_dark_background = _is_dark_background(background_image_path)
    title_color = HexColor("#7DD3FC") if is_dark_background else HexColor("#1D4ED8")
    text_color = HexColor("#FFFFFF") if is_dark_background else HexColor("#111111")
    styles = _build_styles(title_color, text_color)

    pdf = canvas.Canvas(output_pdf_path, pagesize=A4)

    for slide_index, slide in enumerate(processed_contents):
        _draw_background(pdf, background_image_path, page_width, page_height)
        y = page_height - top_margin
        for raw_line in slide.splitlines():
            line = raw_line.strip()

            if not line:
                y -= 16
            elif line.startswith("### "):
                paragraph = Paragraph(_markdown_inline_to_html(line[4:].strip()), styles["h3"])
                y = _draw_paragraph(
                    pdf,
                    paragraph,
                    left_margin,
                    y,
                    text_width,
                    bottom_margin,
                    page_height,
                    top_margin,
                    background_image_path,
                    page_width,
                )
                y -= 12
            elif line.startswith("## "):
                paragraph = Paragraph(_markdown_inline_to_html(line[3:].strip()), styles["h2"])
                y = _draw_paragraph(
                    pdf,
                    paragraph,
                    left_margin,
                    y,
                    text_width,
                    bottom_margin,
                    page_height,
                    top_margin,
                    background_image_path,
                    page_width,
                )
                y -= 14
            elif line.startswith("# "):
                paragraph = Paragraph(_markdown_inline_to_html(line[2:].strip()), styles["h1"])
                y = _draw_paragraph(
                    pdf,
                    paragraph,
                    left_margin,
                    y,
                    text_width,
                    bottom_margin,
                    page_height,
                    top_margin,
                    background_image_path,
                    page_width,
                )
                y -= 16
            else:
                is_bullet = line.startswith("- ") or line.startswith("* ")
                content = line[2:].strip() if is_bullet else line
                html = _markdown_inline_to_html(content)
                if is_bullet:
                    html = f"• {html}"

                paragraph = Paragraph(html, styles["bullet"] if is_bullet else styles["body"])
                y = _draw_paragraph(
                    pdf,
                    paragraph,
                    left_margin,
                    y,
                    text_width,
                    bottom_margin,
                    page_height,
                    top_margin,
                    background_image_path,
                    page_width,
                )
                y -= 10

        if slide_index < len(processed_contents) - 1:
            pdf.showPage()

    pdf.save()
    return output_pdf_path


def generatePdf(processed_contents, input_file_path):
    project_root = os.path.dirname(os.path.abspath(__file__))
    background_variants = _get_background_variants(project_root)
    if not background_variants:
        raise FileNotFoundError("No background images matching 'bkgN.*' were found in the project root.")

    output_pdf_paths = []
    for background_suffix, background_image_path in background_variants:
        output_pdf_paths.append(
            _generate_pdf_for_background(
                processed_contents,
                input_file_path,
                background_suffix,
                background_image_path,
            )
        )

    return output_pdf_paths

def process_md_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    processed_contents=[]

    processed_content = ''
    for line in content.splitlines():
        if line.startswith('----'):
            processed_contents.append(processed_content)
            processed_content = ''
        else:
            processed_content += line + '\n'
    
    if processed_content:
        processed_contents.append(processed_content)
    
    return generatePdf(processed_contents, file_path)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python processMd.py <markdown_file_path>")
        sys.exit(1)

    md_file_path = os.path.join("./input", sys.argv[1])
    if not os.path.isfile(md_file_path):
        print(f"Error: File '{md_file_path}' does not exist.")
        sys.exit(1)

    output_pdfs = process_md_file(md_file_path)
    for output_pdf in output_pdfs:
        print(f"PDF generated at: {output_pdf}")