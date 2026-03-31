import os
import re
from hashlib import md5
from html import escape

from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw, ImageStat

inch = 72.0
cm = inch / 2.54
mm = cm * 0.1
CX=(381*mm,476*mm)


THEME_LIBRARY = {
    # palette from image: #000000 / #226089 / #4592AE / #E3C4A8
    "ai": {
        "keywords": {
            "ai", "llm", "rag", "prompt", "prompting", "embedding", "embeddings", "modello", "modelli",
            "retrieval", "assistant", "assistente", "chatbot", "multimodale", "transformer", "transformers",
            "attention", "self-attention", "inference", "generative", "generation", "token", "tokens",
            "fine-tuning", "agent", "agents", "copilot", "automation", "automazione",
        },
        "palette": ((0, 0, 0), (34, 96, 137), (69, 146, 174)),
        "pattern": "spotlight",
        "title_color": "#4592AE",
        "text_color": "#E3C4A8",
        "bold_color": "#00FFF1",
    },
    # palette from image: #3D6DB9 / #01D1FF / #00FFF1 / #FAFBF6
    "vision": {
        "keywords": {
            "vision", "computer", "immagine", "immagini", "image", "images", "patch", "patches", "vit",
            "cnn", "convolutional", "transformer", "encoder", "attention", "pixel", "pixels", "classification",
            "detection", "segmentazione", "segmentation", "feature", "features", "visuale", "visione",
        },
        "palette": ((61, 109, 185), (1, 209, 255), (0, 255, 241)),
        "pattern": "spotlight",
        "title_color": "#00FFF1",
        "text_color": "#FAFBF6",
        "bold_color": "#01D1FF",
    },
    # palette from image: #1E6261 / #2D767F / #B4F2F1 / #ECFFFB
    "health": {
        "keywords": {
            "salute", "health", "healthcare", "medico", "medica", "medici", "medical", "diagnosi",
            "diagnostic", "ospedale", "ospedali", "clinico", "clinica", "cliniche", "patient", "paziente",
            "pazienti", "therapy", "terapia", "hospital", "screening", "disease", "malattia", "malattie",
        },
        "palette": ((30, 98, 97), (45, 118, 127), (180, 242, 241)),
        "pattern": "spotlight",
        "title_color": "#B4F2F1",
        "text_color": "#ECFFFB",
        "bold_color": "#2D767F",
    },
    # palette from image: #446592 / #4A89AC / #ACE5F6 / #E3FCF9
    "data": {
        "keywords": {
            "data", "dataset", "datasets", "analytics", "analysis", "analisi", "metric", "metrics",
            "insight", "insights", "benchmark", "benchmarks", "grafico", "grafici", "trend", "trends",
            "statistica", "statistiche", "measure", "misura", "misure", "report", "reporting",
        },
        "palette": ((68, 101, 146), (74, 137, 172), (172, 229, 246)),
        "pattern": "waves",
        "title_color": "#ACE5F6",
        "text_color": "#E3FCF9",
        "bold_color": "#F8F8F8",
    },
    # palette from image: #FFD451 / #EF7B3E / #EA5455 / #2C4059
    "growth": {
        "keywords": {
            "crescita", "growth", "scala", "scalare", "impatto", "vantaggi", "risultati", "migliora",
            "performance", "strategia", "strategie", "scale", "scaling", "kpi", "efficienza", "efficiency",
            "conversion", "conversions", "revenue", "traction", "adoption", "adoptione", "roadmap",
        },
        "palette": ((44, 64, 89), (234, 84, 85), (239, 123, 62)),
        "pattern": "waves",
        "title_color": "#FFD451",
        "text_color": "#FAFBF6",
        "bold_color": "#EF7B3E",
    },
    # palette from image: #FF5959 / #FAD05A / #49BEB6 / #075F63
    "business": {
        "keywords": {
            "cliente", "clienti", "utenti", "utente", "business", "mercato", "prodotto", "prodotti", "team",
            "azienda", "aziende", "processo", "processi", "workflow", "controllo", "sales", "vendite",
            "marketing", "brand", "customer", "customers", "service", "servizio", "servizi", "operations",
        },
        "palette": ((7, 95, 99), (73, 190, 182), (255, 89, 89)),
        "pattern": "panels",
        "title_color": "#FAD05A",
        "text_color": "#FAFBF6",
        "bold_color": "#FF5959",
    },
    # palette from image: #6C5FA7 / #6B3779 / #B24968 / #FA8573
    "finance": {
        "keywords": {
            "finance", "finanza", "finanziario", "finanziaria", "costo", "costi", "margine", "margini",
            "investimento", "investimenti", "budget", "roi", "pricing", "price", "prices", "risk", "rischio",
            "rischi", "portfolio", "cashflow", "profit", "profits",
        },
        "palette": ((107, 55, 121), (108, 95, 167), (178, 73, 104)),
        "pattern": "panels",
        "title_color": "#FA8573",
        "text_color": "#FAFBF6",
        "bold_color": "#FFD451",
    },
    # palette from image: #34222E / #E2424A / #F9B8B8 / #FEE9D6
    "security": {
        "keywords": {
            "security", "sicurezza", "privacy", "secure", "compliance", "cybersecurity", "threat", "threats",
            "attacco", "attacchi", "difesa", "difese", "protection", "protezione", "identity", "access",
            "authentication", "autenticazione", "authorization", "autorizzazione", "governance",
        },
        "palette": ((52, 34, 46), (226, 66, 74), (249, 184, 184)),
        "pattern": "spotlight",
        "title_color": "#F9B8B8",
        "text_color": "#FEE9D6",
        "bold_color": "#FAD05A",
    },
    # palette from image: #A66CC1 / #A7ACEC / #ACE7EF / #CEFFF0
    "education": {
        "keywords": {
            "education", "educazione", "training", "formazione", "learning", "learn", "studio", "student",
            "students", "ricerca", "research", "paper", "papers", "corso", "corsi", "lezione", "lezioni",
            "insegnamento", "didattica", "academy", "universita", "university",
        },
        "palette": ((166, 108, 193), (167, 172, 236), (172, 231, 239)),
        "pattern": "waves",
        "title_color": "#CEFFF0",
        "text_color": "#FAFBF6",
        "bold_color": "#ACE7EF",
    },
    # palette from image: #F3E8D2 / #88D398 / #1A946F / #114B5F
    "manual": {
        "keywords": {
            "manuale", "istruzioni", "guida", "pdf", "documento", "documenti", "pagina", "pagine", "qr",
            "codice", "tutorial", "how-to", "setup", "installazione", "install", "configurazione", "configuration",
            "onboarding", "passaggi", "steps",
        },
        "palette": ((17, 75, 95), (26, 148, 111), (136, 211, 152)),
        "pattern": "panels",
        "title_color": "#88D398",
        "text_color": "#F3E8D2",
        "bold_color": "#CEFFF0",
    },
    # palette from image: #060608 / #2370A1 / #A495C6 / #FAD3CE
    "general": {
        "keywords": set(),
        "palette": ((6, 6, 8), (35, 112, 161), (164, 149, 198)),
        "pattern": "spotlight",
        "title_color": "#A495C6",
        "text_color": "#FAD3CE",
        "bold_color": "#2370A1",
    },
}

FONT_REGISTRY = {
    "SegoeUISymbol": os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "seguisym.ttf"),
    "SegoeUIEmoji": os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "seguiemj.ttf"),
}

ICON_FONT_MAP = {
    "→": "SegoeUISymbol",
    "➡": "SegoeUISymbol",
    "✔": "SegoeUISymbol",
    "⚖": "SegoeUISymbol",
    "❌": "SegoeUISymbol",
    "💡": "SegoeUIEmoji",
    "🏥": "SegoeUIEmoji",
    "👉": "SegoeUIEmoji",
    "✅": "SegoeUIEmoji",
    "🚀": "SegoeUIEmoji",
}


def _register_optional_fonts():
    for font_name, font_path in FONT_REGISTRY.items():
        if font_name in pdfmetrics.getRegisteredFontNames():
            continue
        if os.path.isfile(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
            except Exception:
                pass  # font unreadable — icons using it will be stripped


def _apply_icon_font_spans(text):
    registered = set(pdfmetrics.getRegisteredFontNames())
    for icon, font_name in ICON_FONT_MAP.items():
        if icon not in text:
            continue
        if font_name not in registered:
            # Font not available — strip to avoid rendering blank glyphs
            text = text.replace(icon, "")
            continue
        
        cp = ord(icon)
        if cp > 0xFFFF:
            # SMP emoji (surrogate pair) — leave as raw unicode without font tag
            # ReportLab handles SMP better when not wrapped in <font>
            pass
        else:
            # BMP emoji — wrap with font tag using XML entity
            entity = f"&#x{cp:04X};"
            text = text.replace(icon, f'<font name="{font_name}">{entity}</font>')
    
    return text


def _markdown_inline_to_html(text, bold_color=None):
    escaped = escape(text.replace("\ufe0f", ""))
    # Links: [text](url)  — brackets/parens survive html.escape()
    html = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', escaped)
    # Underline: __text__  (must run before single-underscore italic)
    html = re.sub(r"(?<!\w)__(.+?)__(?!\w)", r"<u>\1</u>", html)
    # Bold: **text**
    if bold_color:
        html = re.sub(r"\*\*(.+?)\*\*", rf'<b><font color="{bold_color}">\1</font></b>', html)
    else:
        html = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", html)
    # Italic: *text* and _text_
    html = re.sub(r"(?<!\*)\*(?!\*)([^*]+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", html)
    html = re.sub(r"(?<!\w)_(?!_)(.+?)(?<!_)_(?!\w)", r"<i>\1</i>", html)
    return _apply_icon_font_spans(html)


def _mix_colors(color_a, color_b, ratio):
    return tuple(int(channel_a + (channel_b - channel_a) * ratio) for channel_a, channel_b in zip(color_a, color_b))


def _hex_to_rgb(color_hex):
    clean = color_hex.lstrip("#")
    if len(clean) != 6:
        raise ValueError(f"Invalid HEX color: {color_hex}")
    return tuple(int(clean[index:index + 2], 16) for index in (0, 2, 4))


def _rgb_to_hex(rgb):
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"


def _relative_luminance(rgb):
    def _channel_to_linear(channel):
        value = channel / 255.0
        return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4

    red, green, blue = (_channel_to_linear(channel) for channel in rgb)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def _contrast_ratio(rgb_a, rgb_b):
    luminance_a = _relative_luminance(rgb_a)
    luminance_b = _relative_luminance(rgb_b)
    lighter = max(luminance_a, luminance_b)
    darker = min(luminance_a, luminance_b)
    return (lighter + 0.05) / (darker + 0.05)


def _get_background_reference_rgb(background_image_path):
    if isinstance(background_image_path, Image.Image):
        rgb_image = background_image_path.convert("RGB")
        stat = ImageStat.Stat(rgb_image)
        return tuple(int(channel) for channel in stat.mean)

    with Image.open(background_image_path) as image:
        rgb_image = image.convert("RGB")
        stat = ImageStat.Stat(rgb_image)
        return tuple(int(channel) for channel in stat.mean)


def _pick_readable_hex(preferred_hex, background_rgb, min_ratio):
    preferred_rgb = _hex_to_rgb(preferred_hex)
    if _contrast_ratio(preferred_rgb, background_rgb) >= min_ratio:
        return preferred_hex

    light_candidate = "#FFFFFF"
    dark_candidate = "#111111"
    light_ratio = _contrast_ratio(_hex_to_rgb(light_candidate), background_rgb)
    dark_ratio = _contrast_ratio(_hex_to_rgb(dark_candidate), background_rgb)
    return light_candidate if light_ratio >= dark_ratio else dark_candidate


def _ensure_text_vs_bold_separation(text_hex, bold_hex, background_rgb):
    text_rgb = _hex_to_rgb(text_hex)
    bold_rgb = _hex_to_rgb(bold_hex)
    if _contrast_ratio(text_rgb, bold_rgb) >= 1.2:
        return text_hex, bold_hex

    candidates = ["#C7D2FE", "#BFDBFE", "#CBD5E1", "#D1D5DB", "#1F2937", "#374151"]
    best_text = text_hex
    best_score = -1.0
    for candidate in candidates:
        candidate_rgb = _hex_to_rgb(candidate)
        contrast_to_bg = _contrast_ratio(candidate_rgb, background_rgb)
        contrast_to_bold = _contrast_ratio(candidate_rgb, bold_rgb)
        if contrast_to_bg >= 4.5 and contrast_to_bold >= 1.2:
            score = contrast_to_bg + contrast_to_bold
            if score > best_score:
                best_score = score
                best_text = candidate

    if best_score >= 0:
        return best_text, bold_hex

    # Last resort: push bold to white or black (whichever is more readable), then set text to the other.
    white = "#FFFFFF"
    black = "#111111"
    white_ratio = _contrast_ratio(_hex_to_rgb(white), background_rgb)
    black_ratio = _contrast_ratio(_hex_to_rgb(black), background_rgb)
    best_bold = white if white_ratio >= black_ratio else black
    best_text = black if best_bold == white else white
    return best_text, best_bold


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


def _extract_theme_candidates(content_text, count=3):
    tokens = re.findall(r"[a-zA-ZÀ-ÿ0-9]+", content_text.lower())
    scored = []
    for theme_name, theme in THEME_LIBRARY.items():
        if theme_name == "general":
            continue
        keywords = theme.get("keywords", set())
        score = sum(1 for token in tokens if token in keywords)
        scored.append((theme_name, score))

    scored.sort(key=lambda item: (-item[1], item[0]))
    selected = [theme_name for theme_name, score in scored if score > 0][:count]

    if len(selected) < count:
        fallback_pool = [theme_name for theme_name, _score in scored if theme_name not in selected]
        seed_bytes = md5(content_text.encode("utf-8")).digest()
        offset = seed_bytes[0] % len(fallback_pool) if fallback_pool else 0
        rotated_pool = fallback_pool[offset:] + fallback_pool[:offset]
        selected.extend(rotated_pool[: count - len(selected)])

    return selected[:count] if selected else ["general"]


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
        _draw_spotlight_pattern(draw, width, height, accent, seed_bytes)
    elif pattern_name == "panels":
        _draw_panel_pattern(draw, width, height, accent, seed_bytes)
    elif pattern_name == "waves":
        _draw_wave_pattern(draw, width, height, accent, seed_bytes)
    else:
        _draw_spotlight_pattern(draw, width, height, accent, seed_bytes)


def _generate_auto_background(content_text, theme_name):
    theme = THEME_LIBRARY.get(theme_name, THEME_LIBRARY["general"])
    base_color, mid_color, _accent_color = theme["palette"]
    width = int(CX[0] * 2)
    height = int(CX[1] * 2)
    image = Image.new("RGBA", (width, height), base_color + (255,))
    draw = ImageDraw.Draw(image, "RGBA")

    for y in range(height):
        ratio = y / max(1, height - 1)
        row_color = _mix_colors(base_color, mid_color, ratio)
        draw.line((0, y, width, y), fill=row_color + (255,))

    return image.convert("RGB"), theme_name


def _draw_background(pdf, background_image_path, page_width, page_height):
    if isinstance(background_image_path, Image.Image):
        pdf.drawImage(
            ImageReader(background_image_path),
            0,
            0,
            width=page_width,
            height=page_height,
            preserveAspectRatio=False,
            mask="auto",
        )
    elif os.path.isfile(background_image_path):
        pdf.drawImage(
            background_image_path,
            0,
            0,
            width=page_width,
            height=page_height,
            preserveAspectRatio=False,
            mask="auto",
        )


def _is_dark_background(background_image_path):
    if isinstance(background_image_path, Image.Image):
        rgb_image = background_image_path.convert("RGB")
        stat = ImageStat.Stat(rgb_image)
        red, green, blue = stat.mean
        brightness = 0.299 * red + 0.587 * green + 0.114 * blue
        return brightness < 145

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


def _build_styles(title_color, text_color, scale=1.0):
    h1_size = int(42 * scale)
    h2_size = int(34 * scale)
    h3_size = int(28 * scale)
    body_size = int(20 * scale)
    return {
        "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=h1_size, leading=int(h1_size * 1.15), textColor=title_color),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=h2_size, leading=int(h2_size * 1.16), textColor=title_color),
        "h3": ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=h3_size, leading=int(h3_size * 1.18), textColor=title_color),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=body_size, leading=int(body_size * 1.4), textColor=text_color),
        "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=body_size, leading=int(body_size * 1.4), textColor=text_color),
    }


def _get_slide_layout_profile(slide_text):
    cleaned = re.sub(r"[\*_#>-]", "", slide_text)
    characters = len(cleaned)
    lines = [line.strip() for line in slide_text.splitlines() if line.strip()]
    non_empty_lines = len(lines)

    if characters < 170 or non_empty_lines <= 4:
        return {"scale": 1.24, "line_gap": 14, "blank_gap": 24, "title_gap": 18}
    if characters < 300:
        return {"scale": 1.14, "line_gap": 12, "blank_gap": 20, "title_gap": 16}
    if characters > 780 or non_empty_lines > 15:
        return {"scale": 0.96, "line_gap": 8, "blank_gap": 12, "title_gap": 12}
    return {"scale": 1.04, "line_gap": 10, "blank_gap": 16, "title_gap": 14}


def _get_theme_colors(background_image_path, theme_name=None):
    is_dark_background = _is_dark_background(background_image_path)
    background_rgb = _get_background_reference_rgb(background_image_path)
    theme = THEME_LIBRARY.get(theme_name, {}) if theme_name else {}
    title_color_hex = theme.get("title_color")
    text_color_hex = theme.get("text_color")
    bold_color_hex = theme.get("bold_color")

    if title_color_hex is None:
        title_color_hex = "#7DD3FC" if is_dark_background else "#1D4ED8"
    if text_color_hex is None:
        text_color_hex = "#FFFFFF" if is_dark_background else "#111111"
    if bold_color_hex is None:
        bold_color_hex = "#FFFFFF" if is_dark_background else "#1E3A8A"

    title_color_hex = _pick_readable_hex(title_color_hex, background_rgb, min_ratio=3.0)
    text_color_hex = _pick_readable_hex(text_color_hex, background_rgb, min_ratio=4.5)
    bold_color_hex = _pick_readable_hex(bold_color_hex, background_rgb, min_ratio=4.5)
    text_color_hex, bold_color_hex = _ensure_text_vs_bold_separation(text_color_hex, bold_color_hex, background_rgb)

    title_color = HexColor(title_color_hex)
    text_color = HexColor(text_color_hex)
    return {
        "title_color": title_color,
        "text_color": text_color,
        "bold_color": bold_color_hex,
    }


def _get_styles_for_background(background_image_path, scale=1.0, theme_name=None):
    colors = _get_theme_colors(background_image_path, theme_name)
    return _build_styles(colors["title_color"], colors["text_color"], scale)


def _generate_pdf(processed_contents, output_pdf_path, background_path_provider, theme_name_provider=None):
    project_root = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(project_root, "output")
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    page_width, page_height = CX
    left_margin = 42
    right_margin = 42
    content_inset = 18
    content_top_inset = 18
    top_margin = 54
    bottom_margin = 54
    text_left = left_margin + content_inset
    text_width = page_width - text_left - right_margin

    pdf = canvas.Canvas(output_pdf_path, pagesize=CX)

    for slide_index, slide in enumerate(processed_contents):
        background_image_path = background_path_provider(slide_index, slide)
        layout_profile = _get_slide_layout_profile(slide)
        theme_name = theme_name_provider(slide_index, slide) if theme_name_provider else None
        styles = _get_styles_for_background(background_image_path, layout_profile["scale"], theme_name)
        colors = _get_theme_colors(background_image_path, theme_name)
        _draw_background(pdf, background_image_path, page_width, page_height)
        y = page_height - top_margin - content_top_inset
        for raw_line in slide.splitlines():
            line = raw_line.strip()

            if not line:
                y -= layout_profile["blank_gap"]
            elif line.startswith("### "):
                paragraph = Paragraph(_markdown_inline_to_html(line[4:].strip(), colors["bold_color"]), styles["h3"])
                y = _draw_paragraph(
                    pdf,
                    paragraph,
                    text_left,
                    y,
                    text_width,
                    bottom_margin,
                    page_height,
                    top_margin + content_top_inset,
                    background_image_path,
                    page_width,
                )
                y -= layout_profile["title_gap"]
            elif line.startswith("## "):
                paragraph = Paragraph(_markdown_inline_to_html(line[3:].strip(), colors["bold_color"]), styles["h2"])
                y = _draw_paragraph(
                    pdf,
                    paragraph,
                    text_left,
                    y,
                    text_width,
                    bottom_margin,
                    page_height,
                    top_margin + content_top_inset,
                    background_image_path,
                    page_width,
                )
                y -= layout_profile["title_gap"]
            elif line.startswith("# "):
                paragraph = Paragraph(_markdown_inline_to_html(line[2:].strip(), colors["bold_color"]), styles["h1"])
                y = _draw_paragraph(
                    pdf,
                    paragraph,
                    text_left,
                    y,
                    text_width,
                    bottom_margin,
                    page_height,
                    top_margin + content_top_inset,
                    background_image_path,
                    page_width,
                )
                y -= layout_profile["title_gap"]
            else:
                is_bullet = line.startswith("- ") or line.startswith("* ")
                content = line[2:].strip() if is_bullet else line
                html = _markdown_inline_to_html(content, colors["bold_color"])
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
                    top_margin + content_top_inset,
                    background_image_path,
                    page_width,
                )
                y -= layout_profile["line_gap"]

        if slide_index < len(processed_contents) - 1:
            pdf.showPage()

    pdf.save()
    return output_pdf_path


def _generate_pdf_with_auto_backgrounds(processed_contents, input_file_path):
    project_root = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(project_root, "output")
    input_name = os.path.splitext(os.path.basename(input_file_path))[0]
    combined_content = "\n".join(processed_contents)
    selected_themes = _extract_theme_candidates(combined_content, count=3)

    output_paths = []
    for theme_name in selected_themes:
        output_pdf_path = os.path.join(output_dir, f"{input_name}_auto_{theme_name}.pdf")
        auto_background_image, resolved_theme_name = _generate_auto_background(combined_content, theme_name)
        output_paths.append(
            _generate_pdf(
                processed_contents,
                output_pdf_path,
                lambda _slide_index, _slide, image=auto_background_image: image,
                lambda _slide_index, _slide, name=resolved_theme_name: name,
            )
        )

    return output_paths


def generatePdf(processed_contents, input_file_path):
    _register_optional_fonts()
    return _generate_pdf_with_auto_backgrounds(processed_contents, input_file_path)

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