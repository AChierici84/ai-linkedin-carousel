import os
import re
from hashlib import md5
from glob import glob
from html import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw, ImageStat


THEME_LIBRARY = {
    "ai": {
        "keywords": {"ai", "llm", "rag", "prompt", "prompting", "embedding", "embeddings", "modello", "modelli", "retrieval", "assistant", "assistente", "chatbot", "multimodale"},
        "palette": ((15, 23, 42), (14, 116, 144), (125, 211, 252)),
        "pattern": "network",
    },
    "growth": {
        "keywords": {"crescita", "growth", "scala", "scalare", "impatto", "vantaggi", "risultati", "migliora", "performance", "strategia"},
        "palette": ((22, 78, 99), (8, 145, 178), (103, 232, 249)),
        "pattern": "waves",
    },
    "business": {
        "keywords": {"cliente", "utenti", "business", "mercato", "prodotto", "team", "azienda", "processo", "workflow", "controllo"},
        "palette": ((69, 26, 3), (180, 83, 9), (253, 186, 116)),
        "pattern": "panels",
    },
    "manual": {
        "keywords": {"manuale", "istruzioni", "guida", "pdf", "documento", "documenti", "pagina", "pagine", "qr", "codice"},
        "palette": ((30, 41, 59), (71, 85, 105), (148, 163, 184)),
        "pattern": "panels",
    },
    "general": {
        "keywords": set(),
        "palette": ((49, 46, 129), (37, 99, 235), (147, 197, 253)),
        "pattern": "spotlight",
    },
}


def _markdown_inline_to_html(text):
    escaped = escape(text)
    # Convert markdown bold (**text**) to reportlab paragraph bold tags.
    html = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)
    html = re.sub(r"(?<!\*)\*(?!\*)([^*]+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", html)
    return re.sub(r"(?<!\w)_(?!_)(.+?)(?<!_)_(?!\w)", r"<i>\1</i>", html)


def _mix_colors(color_a, color_b, ratio):
    return tuple(int(channel_a + (channel_b - channel_a) * ratio) for channel_a, channel_b in zip(color_a, color_b))


def _extract_theme(slide_text):
    tokens = re.findall(r"[a-zA-ZÀ-ÿ0-9]+", slide_text.lower())
    scores = {}
    for theme_name, theme in THEME_LIBRARY.items():
        if not theme["keywords"]:
            continue
        scores[theme_name] = sum(1 for token in tokens if token in theme["keywords"])

    if scores and max(scores.values()) > 0:
        return max(scores, key=scores.get)

    digest = md5(slide_text.encode("utf-8")).digest()[0]
    named_themes = [theme_name for theme_name in THEME_LIBRARY if theme_name != "general"]
    return named_themes[digest % len(named_themes)] if named_themes else "general"


def _draw_network_pattern(draw, width, height, accent, seed_bytes):
    points = []
    for index in range(6):
        x = int((0.15 + 0.12 * index + (seed_bytes[index] / 255) * 0.12) * width)
        y = int((0.58 + (seed_bytes[index + 6] / 255) * 0.26) * height)
        points.append((x, y))

    for start, end in zip(points, points[1:]):
        draw.line((start[0], start[1], end[0], end[1]), fill=accent + (84,), width=5)

    for x, y in points:
        radius = 16 + seed_bytes[(x + y) % len(seed_bytes)] % 18
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=accent + (132,))


def _draw_panel_pattern(draw, width, height, accent, seed_bytes):
    panel_width = width // 5
    for index in range(4):
        left = int(index * panel_width + panel_width * 0.35)
        top = int(height * (0.54 + index * 0.04))
        right = left + int(panel_width * (0.8 + (seed_bytes[index] / 255) * 0.2))
        bottom = height - int(height * (0.04 + index * 0.03))
        draw.rounded_rectangle((left, top, right, bottom), radius=32, fill=accent + (42 + index * 12,))


def _draw_wave_pattern(draw, width, height, accent, seed_bytes):
    for index in range(4):
        top = int(height * (0.62 + index * 0.06))
        wave_height = 120 + seed_bytes[index] % 80
        draw.arc((-120, top, width + 120, top + wave_height), start=0, end=180, fill=accent + (90,), width=7)


def _draw_spotlight_pattern(draw, width, height, accent, seed_bytes):
    for index in range(3):
        radius = int(width * (0.16 + (seed_bytes[index] / 255) * 0.12))
        center_x = int(width * (0.2 + index * 0.3))
        center_y = int(height * (0.62 + (seed_bytes[index + 3] / 255) * 0.18))
        draw.ellipse(
            (center_x - radius, center_y - radius, center_x + radius, center_y + radius),
            fill=accent + (46 + index * 16,),
        )


def _draw_pattern(draw, width, height, pattern_name, accent, seed_bytes):
    if pattern_name == "network":
        _draw_network_pattern(draw, width, height, accent, seed_bytes)
    elif pattern_name == "panels":
        _draw_panel_pattern(draw, width, height, accent, seed_bytes)
    elif pattern_name == "waves":
        _draw_wave_pattern(draw, width, height, accent, seed_bytes)
    else:
        _draw_spotlight_pattern(draw, width, height, accent, seed_bytes)


def _generate_auto_background(content_text, output_path):
    theme_name = _extract_theme(content_text)
    theme = THEME_LIBRARY.get(theme_name, THEME_LIBRARY["general"])
    base_color, mid_color, accent_color = theme["palette"]
    width = int(A4[0] * 2)
    height = int(A4[1] * 2)
    image = Image.new("RGBA", (width, height), base_color + (255,))
    draw = ImageDraw.Draw(image, "RGBA")

    for y in range(height):
        ratio = y / max(1, height - 1)
        row_color = _mix_colors(base_color, mid_color, ratio)
        draw.line((0, y, width, y), fill=row_color + (255,))

    seed_bytes = md5(content_text.encode("utf-8")).digest()
    accent_variant = _mix_colors(accent_color, (255, 255, 255), 0.15)
    _draw_pattern(draw, width, height, theme["pattern"], accent_variant, seed_bytes)

    halo_radius = int(width * 0.24)
    halo_x = int(width * (0.72 + (seed_bytes[10] / 255) * 0.12))
    halo_y = int(height * (0.68 + (seed_bytes[11] / 255) * 0.12))
    draw.ellipse(
        (halo_x - halo_radius, halo_y - halo_radius, halo_x + halo_radius, halo_y + halo_radius),
        fill=accent_color + (36,),
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    image.convert("RGB").save(output_path, format="PNG")
    return output_path


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


def _get_styles_for_background(background_image_path):
    is_dark_background = _is_dark_background(background_image_path)
    title_color = HexColor("#7DD3FC") if is_dark_background else HexColor("#1D4ED8")
    text_color = HexColor("#FFFFFF") if is_dark_background else HexColor("#111111")
    return _build_styles(title_color, text_color)


def _generate_pdf(processed_contents, output_pdf_path, background_path_provider):
    project_root = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(project_root, "output")
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    page_width, page_height = A4
    left_margin = 42
    right_margin = 42
    content_inset = 18
    content_top_inset = 18
    top_margin = 54
    bottom_margin = 54
    text_left = left_margin + content_inset
    text_width = page_width - text_left - right_margin

    pdf = canvas.Canvas(output_pdf_path, pagesize=A4)

    for slide_index, slide in enumerate(processed_contents):
        background_image_path = background_path_provider(slide_index, slide)
        styles = _get_styles_for_background(background_image_path)
        _draw_background(pdf, background_image_path, page_width, page_height)
        y = page_height - top_margin - content_top_inset
        for raw_line in slide.splitlines():
            line = raw_line.strip()

            if not line:
                y -= 16
            elif line.startswith("### "):
                paragraph = Paragraph(_markdown_inline_to_html(line[4:].strip()), styles["h3"])
                y = _draw_paragraph(
                    pdf,
                    paragraph,
                    text_left,
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
                    text_left,
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
                    text_left,
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
                    text_left,
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


def _generate_pdf_for_background(processed_contents, input_file_path, background_suffix, background_image_path):
    project_root = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(project_root, "output")
    input_name = os.path.splitext(os.path.basename(input_file_path))[0]
    output_pdf_path = os.path.join(output_dir, f"{input_name}_bkg{background_suffix}.pdf")
    return _generate_pdf(processed_contents, output_pdf_path, lambda _slide_index, _slide: background_image_path)


def _generate_pdf_with_auto_backgrounds(processed_contents, input_file_path):
    project_root = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(project_root, "output")
    input_name = os.path.splitext(os.path.basename(input_file_path))[0]
    output_pdf_path = os.path.join(output_dir, f"{input_name}_auto.pdf")
    auto_background_path = os.path.join(output_dir, f"{input_name}_auto_background.png")
    combined_content = "\n".join(processed_contents)
    _generate_auto_background(combined_content, auto_background_path)
    return _generate_pdf(
        processed_contents,
        output_pdf_path,
        lambda _slide_index, _slide: auto_background_path,
    )


def generatePdf(processed_contents, input_file_path):
    project_root = os.path.dirname(os.path.abspath(__file__))
    background_variants = _get_background_variants(project_root)

    output_pdf_paths = [_generate_pdf_with_auto_backgrounds(processed_contents, input_file_path)]
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