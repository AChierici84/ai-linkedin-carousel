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
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PALETTE_DIR = os.path.join(PROJECT_ROOT, "palette")


THEME_LIBRARY = {
    "ai": {
        "keywords": {
            "ai", "llm", "rag", "prompt", "prompting", "embedding", "embeddings", "modello", "modelli",
            "retrieval", "assistant", "assistente", "chatbot", "multimodale", "transformer", "transformers",
            "attention", "self-attention", "inference", "generative", "generation", "token", "tokens",
            "fine-tuning", "agent", "agents", "copilot", "automation", "automazione",
        },
        "pattern": "spotlight",
        "palette_name": None,
    },
    "vision": {
        "keywords": {
            "vision", "computer", "immagine", "immagini", "image", "images", "patch", "patches", "vit",
            "cnn", "convolutional", "transformer", "encoder", "attention", "pixel", "pixels", "classification",
            "detection", "segmentazione", "segmentation", "feature", "features", "visuale", "visione",
        },
        "pattern": "spotlight",
        "palette_name": None,
    },
    "health": {
        "keywords": {
            "salute", "health", "healthcare", "medico", "medica", "medici", "medical", "diagnosi",
            "diagnostic", "ospedale", "ospedali", "clinico", "clinica", "cliniche", "patient", "paziente",
            "pazienti", "therapy", "terapia", "hospital", "screening", "disease", "malattia", "malattie",
        },
        "pattern": "spotlight",
        "palette_name": None,
    },
    "data": {
        "keywords": {
            "data", "dataset", "datasets", "analytics", "analysis", "analisi", "metric", "metrics",
            "insight", "insights", "benchmark", "benchmarks", "grafico", "grafici", "trend", "trends",
            "statistica", "statistiche", "measure", "misura", "misure", "report", "reporting",
        },
        "pattern": "waves",
        "palette_name": None,
    },
    "growth": {
        "keywords": {
            "crescita", "growth", "scala", "scalare", "impatto", "vantaggi", "risultati", "migliora",
            "performance", "strategia", "strategie", "scale", "scaling", "kpi", "efficienza", "efficiency",
            "conversion", "conversions", "revenue", "traction", "adoption", "adoptione", "roadmap",
        },
        "pattern": "waves",
        "palette_name": None,
    },
    "business": {
        "keywords": {
            "cliente", "clienti", "utenti", "utente", "business", "mercato", "prodotto", "prodotti", "team",
            "azienda", "aziende", "processo", "processi", "workflow", "controllo", "sales", "vendite",
            "marketing", "brand", "customer", "customers", "service", "servizio", "servizi", "operations",
        },
        "pattern": "panels",
        "palette_name": None,
    },
    "finance": {
        "keywords": {
            "finance", "finanza", "finanziario", "finanziaria", "costo", "costi", "margine", "margini",
            "investimento", "investimenti", "budget", "roi", "pricing", "price", "prices", "risk", "rischio",
            "rischi", "portfolio", "cashflow", "profit", "profits",
        },
        "pattern": "panels",
        "palette_name": None,
    },
    "security": {
        "keywords": {
            "security", "sicurezza", "privacy", "secure", "compliance", "cybersecurity", "threat", "threats",
            "attacco", "attacchi", "difesa", "difese", "protection", "protezione", "identity", "access",
            "authentication", "autenticazione", "authorization", "autorizzazione", "governance",
        },
        "pattern": "spotlight",
        "palette_name": None,
    },
    "education": {
        "keywords": {
            "education", "educazione", "training", "formazione", "learning", "learn", "studio", "student",
            "students", "ricerca", "research", "paper", "papers", "corso", "corsi", "lezione", "lezioni",
            "insegnamento", "didattica", "academy", "universita", "university",
        },
        "pattern": "waves",
        "palette_name": None,
    },
    "manual": {
        "keywords": {
            "manuale", "istruzioni", "guida", "pdf", "documento", "documenti", "pagina", "pagine", "qr",
            "codice", "tutorial", "how-to", "setup", "installazione", "install", "configurazione", "configuration",
            "onboarding", "passaggi", "steps",
        },
        "pattern": "panels",
        "palette_name": None,
    },
    "general": {
        "keywords": set(),
        "pattern": "spotlight",
        "palette_name": None,
    },
}


THEME_COLOR_TARGETS = {
    "ai": {"background": "#000000", "bold": "#226089", "title": "#4592AE", "text": "#E3C4A8"},
    "vision": {"background": "#3D6DB9", "bold": "#01D1FF", "title": "#00FFF1", "text": "#FAFBF6"},
    "health": {"background": "#1E6261", "bold": "#2D767F", "title": "#B4F2F1", "text": "#ECFFFB"},
    "data": {"background": "#446592", "bold": "#4A89AC", "title": "#ACE5F6", "text": "#E3FCF9"},
    "growth": {"background": "#2C4059", "bold": "#EA5455", "title": "#EF7B3E", "text": "#FFD451"},
    "business": {"background": "#075F63", "bold": "#49BEB6", "title": "#FF5959", "text": "#FAD05A"},
    "finance": {"background": "#6B3779", "bold": "#6C5FA7", "title": "#B24968", "text": "#FA8573"},
    "security": {"background": "#34222E", "bold": "#E2424A", "title": "#F9B8B8", "text": "#FEE9D6"},
    "education": {"background": "#A66CC1", "bold": "#A7ACEC", "title": "#ACE7EF", "text": "#CEFFF0"},
    "manual": {"background": "#114B5F", "bold": "#1A946F", "title": "#88D398", "text": "#F3E8D2"},
    "general": {"background": "#060608", "bold": "#2370A1", "title": "#A495C6", "text": "#FAD3CE"},
}


THEME_PALETTE_OVERRIDES = {
    "ai": "AdobeColor-Offender 2020.jpeg",
    "vision": "AdobeColor-Apparel 45.jpeg",
    "health": "AdobeColor-Moda (5).jpeg",
    "data": "AdobeColor-Miffew _ Lookbook.jpeg",
    "growth": "AdobeColor-GOSSAMER IN BUD _ L’Officiel Vietnam.jpeg",
    "business": "AdobeColor-Polina.jpeg",
    "finance": "AdobeColor-White bead - Beauty editorial.jpeg",
    "security": "AdobeColor-Campaign.jpeg",
    "education": "AdobeColor-Moda (3).jpeg",
    "manual": "AdobeColor-Moda (11).jpeg",
    "general": "AdobeColor-Moda (2).jpeg",
}


def _hex_to_rgb_safe(color_hex):
    clean = (color_hex or "").lstrip("#")
    if len(clean) != 6:
        return (0, 0, 0)
    return tuple(int(clean[index:index + 2], 16) for index in (0, 2, 4))


def _palette_similarity_score(target_roles, candidate_roles):
    weights = {
        "background": 3.0,
        "text": 2.5,
        "bold": 2.0,
        "title": 1.8,
    }
    score = 0.0
    for role, weight in weights.items():
        target_rgb = _hex_to_rgb_safe(target_roles.get(role))
        candidate_rgb = _hex_to_rgb_safe(candidate_roles.get(role))
        distance = sum((a - b) ** 2 for a, b in zip(target_rgb, candidate_rgb)) ** 0.5
        score += weight * distance
    return score


def list_palette_files():
    if not os.path.isdir(PALETTE_DIR):
        return []

    valid_ext = {".jpg", ".jpeg", ".png", ".webp"}
    files = []
    for name in os.listdir(PALETTE_DIR):
        path = os.path.join(PALETTE_DIR, name)
        if os.path.isfile(path) and os.path.splitext(name.lower())[1] in valid_ext:
            files.append(name)
    return sorted(files, key=lambda item: item.lower())


def _relative_luminance(rgb):
    def _channel_to_linear(channel):
        value = channel / 255.0
        return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4

    red, green, blue = (_channel_to_linear(channel) for channel in rgb)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def _rgb_to_hex(rgb):
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"


def _resolve_palette_path(palette_name_or_path):
    if not palette_name_or_path:
        return None
    if os.path.isfile(palette_name_or_path):
        return palette_name_or_path

    candidate = os.path.join(PALETTE_DIR, palette_name_or_path)
    if os.path.isfile(candidate):
        return candidate
    return None


def _extract_dominant_palette_colors(palette_name_or_path, max_colors=8):
    palette_path = _resolve_palette_path(palette_name_or_path)
    if not palette_path:
        return []

    with Image.open(palette_path) as image:
        rgb = image.convert("RGB")
        rgb.thumbnail((320, 320))
        quantized = rgb.quantize(colors=max_colors, method=Image.Quantize.MEDIANCUT)
        palette = quantized.getpalette()
        color_counts = quantized.getcolors() or []

    extracted = []
    for count, color_index in color_counts:
        base = color_index * 3
        extracted.append((count, tuple(palette[base:base + 3])))

    extracted.sort(key=lambda item: item[0], reverse=True)
    unique_rgb = []
    for _, rgb in extracted:
        if rgb not in unique_rgb:
            unique_rgb.append(rgb)
    return unique_rgb


def get_palette_roles(palette_name_or_path):
    dominant_colors = _extract_dominant_palette_colors(palette_name_or_path)
    if len(dominant_colors) < 4:
        return {
            "background": "#060608",
            "bold": "#2370A1",
            "title": "#A495C6",
            "text": "#FAD3CE",
            "ordered": ["#060608", "#2370A1", "#A495C6", "#FAD3CE"],
        }

    ordered_by_darkness = sorted(dominant_colors, key=_relative_luminance)
    darkest = ordered_by_darkness[0]
    second_darkest = ordered_by_darkness[1]
    third_darkest = ordered_by_darkness[2]
    lightest = ordered_by_darkness[-1]

    ordered_hex = [_rgb_to_hex(rgb) for rgb in ordered_by_darkness]
    return {
        "background": _rgb_to_hex(darkest),
        "bold": _rgb_to_hex(second_darkest),
        "title": _rgb_to_hex(third_darkest),
        "text": _rgb_to_hex(lightest),
        "ordered": ordered_hex,
    }


def get_theme_from_palette(palette_name_or_path):
    roles = get_palette_roles(palette_name_or_path)
    ordered_hex = roles["ordered"]
    if len(ordered_hex) < 3:
        ordered_hex = [roles["background"], roles["bold"], roles["title"]]

    return {
        "keywords": set(),
        "palette": tuple(_hex_to_rgb(color_hex) for color_hex in ordered_hex[:3]),
        "pattern": "spotlight",
        "title_color": roles["title"],
        "text_color": roles["text"],
        "bold_color": roles["bold"],
    }


def _resolve_automatic_theme_palettes():
    palette_files = list_palette_files()
    if not palette_files:
        return

    palette_roles_map = {name: get_palette_roles(name) for name in palette_files}
    available = set(palette_files)

    # Apply explicit overrides first for stable, brand-consistent output.
    for theme_name, palette_name in THEME_PALETTE_OVERRIDES.items():
        if theme_name not in THEME_LIBRARY:
            continue
        if palette_name in palette_roles_map:
            THEME_LIBRARY[theme_name]["palette_name"] = palette_name
            if palette_name in available:
                available.remove(palette_name)

    for theme_name in THEME_LIBRARY.keys():
        if THEME_LIBRARY[theme_name].get("palette_name") in palette_roles_map:
            continue
        target_roles = THEME_COLOR_TARGETS.get(theme_name, THEME_COLOR_TARGETS["general"])
        pool = available if available else set(palette_files)
        best_name = min(pool, key=lambda candidate: _palette_similarity_score(target_roles, palette_roles_map[candidate]))
        THEME_LIBRARY[theme_name]["palette_name"] = best_name
        if best_name in available:
            available.remove(best_name)


def _resolve_theme_definition(theme_name):
    theme_info = THEME_LIBRARY.get(theme_name, THEME_LIBRARY["general"])
    palette_name = theme_info.get("palette_name")
    if palette_name:
        resolved = get_theme_from_palette(palette_name)
        resolved["keywords"] = theme_info.get("keywords", set())
        resolved["pattern"] = theme_info.get("pattern", "spotlight")
        resolved["palette_name"] = palette_name
        return resolved

    fallback = get_theme_from_palette("")
    fallback["keywords"] = theme_info.get("keywords", set())
    fallback["pattern"] = theme_info.get("pattern", "spotlight")
    fallback["palette_name"] = None
    return fallback


_resolve_automatic_theme_palettes()

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


def _generate_auto_background(content_text, theme_name, theme_override=None):
    theme = theme_override if theme_override else _resolve_theme_definition(theme_name)
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


def _first_non_empty_line_from_slides(processed_contents):
    for slide in processed_contents:
        for raw_line in slide.splitlines():
            line = raw_line.strip()
            if line:
                line = re.sub(r"^#{1,6}\s+", "", line)
                line = re.sub(r"^[-*]\s+", "", line)
                return line
    return ""


def _split_cover_title_two_lines(title, max_chars=44):
    text = re.sub(r"\s+", " ", (title or "")).strip()
    if not text or len(text) <= max_chars or " " not in text:
        return text

    midpoint = len(text) // 2
    split_idx = min((idx for idx, ch in enumerate(text) if ch == " "), key=lambda idx: abs(idx - midpoint), default=-1)
    if split_idx <= 0 or split_idx >= len(text) - 1:
        return text

    left = text[:split_idx].strip()
    right = text[split_idx + 1 :].strip()
    if not left or not right:
        return text
    return f"{left}<br/>{right}"


def _draw_cover_slide(pdf, cover_image_path, page_width, page_height, cover_title):
    _draw_background(pdf, cover_image_path, page_width, page_height)
    background_rgb = _get_background_reference_rgb(cover_image_path)
    title_hex = _pick_readable_hex("#FFFFFF", background_rgb, min_ratio=4.5)
    title_color = HexColor(title_hex)

    text_width = page_width * 0.72
    inset_x = (page_width - text_width) / 2
    title_style = ParagraphStyle(
        "cover_title",
        fontName="Helvetica-Bold",
        fontSize=56,
        leading=64,
        alignment=1,
        textColor=title_color,
    )

    split_title = _split_cover_title_two_lines(cover_title)
    content = _markdown_inline_to_html((split_title or "").strip(), None)
    if not content:
        content = "Copertina"
    paragraph = Paragraph(content, title_style)
    _w, h = paragraph.wrap(text_width, page_height * 0.8)
    y = page_height - 140
    paragraph.drawOn(pdf, inset_x, y - h)


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
    body_size = int(24 * scale)
    return {
        "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=h1_size, leading=int(h1_size * 1.15), textColor=title_color),
        "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=h2_size, leading=int(h2_size * 1.16), textColor=title_color),
        "h3": ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=h3_size, leading=int(h3_size * 1.18), textColor=title_color),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=body_size, leading=int(body_size * 1.4), textColor=text_color),
        "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=body_size, leading=int(body_size * 1.4), textColor=text_color),
    }


def _measure_slide_height(slide, styles, colors, text_width, page_height, gap_body, gap_title, gap_blank):
    total = 0
    for raw_line in slide.splitlines():
        line = raw_line.strip()
        if not line:
            total += gap_blank
        elif line.startswith("### "):
            p = Paragraph(_markdown_inline_to_html(line[4:].strip(), colors["bold_color"]), styles["h3"])
            _, h = p.wrap(text_width, page_height)
            total += h + gap_title
        elif line.startswith("## "):
            p = Paragraph(_markdown_inline_to_html(line[3:].strip(), colors["bold_color"]), styles["h2"])
            _, h = p.wrap(text_width, page_height)
            total += h + gap_title
        elif line.startswith("# "):
            p = Paragraph(_markdown_inline_to_html(line[2:].strip(), colors["bold_color"]), styles["h1"])
            _, h = p.wrap(text_width, page_height)
            total += h + gap_title
        else:
            is_bullet = line.startswith("- ") or line.startswith("* ")
            content = line[2:].strip() if is_bullet else line
            html = _markdown_inline_to_html(content, colors["bold_color"])
            if is_bullet:
                html = f"\u2022 {html}"
            p = Paragraph(html, styles["bullet"] if is_bullet else styles["body"])
            _, h = p.wrap(text_width, page_height)
            total += h + gap_body
    return total


def _find_adaptive_scale(slide, colors, title_color, text_color, text_width, page_height, usable_height):
    """Binary-search the largest font scale that makes the slide content fit usable_height."""
    scale_min = 0.55
    scale_max = 2.2
    target = usable_height * 0.92          # fill 92% of usable area
    for _ in range(18):                    # 18 iterations → precision < 0.001
        scale = (scale_min + scale_max) / 2
        styles = _build_styles(title_color, text_color, scale)
        gap_body  = max(4, int(10 * scale))
        gap_title = max(4, int(12 * scale))
        gap_blank = max(4, int(14 * scale))
        h = _measure_slide_height(slide, styles, colors, text_width, page_height, gap_body, gap_title, gap_blank)
        if h > target:
            scale_max = scale
        else:
            scale_min = scale
    return scale_min


def _get_theme_colors(background_image_path, theme_name=None, theme_override=None):
    is_dark_background = _is_dark_background(background_image_path)
    background_rgb = _get_background_reference_rgb(background_image_path)
    theme = theme_override if theme_override else (_resolve_theme_definition(theme_name) if theme_name else {})
    title_color_hex = theme.get("title_color")
    text_color_hex = theme.get("text_color")
    bold_color_hex = theme.get("bold_color")

    # If a palette already provides explicit role colors, keep them as-is.
    # This avoids automatic fallback to white/black and respects selected palette intent.
    has_explicit_palette_roles = bool(title_color_hex and text_color_hex and bold_color_hex)
    if has_explicit_palette_roles:
        return {
            "title_color": HexColor(title_color_hex),
            "text_color": HexColor(text_color_hex),
            "bold_color": bold_color_hex,
        }

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


def _generate_pdf(
    processed_contents,
    output_pdf_path,
    background_path_provider,
    theme_name_provider=None,
    theme_override_provider=None,
    cover_image_path=None,
):
    output_dir = os.path.join(PROJECT_ROOT, "output")
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    page_width, page_height = CX
    left_margin = 42
    right_margin = 42
    content_inset = 0
    content_top_inset = 0
    top_margin = 54
    bottom_margin = 54
    text_left = left_margin + content_inset
    text_width = page_width - text_left - right_margin

    pdf = canvas.Canvas(output_pdf_path, pagesize=CX)

    usable_height = page_height - top_margin - bottom_margin

    if cover_image_path:
        cover_title = _first_non_empty_line_from_slides(processed_contents)
        _draw_cover_slide(pdf, cover_image_path, page_width, page_height, cover_title)
        if processed_contents:
            pdf.showPage()

    for slide_index, slide in enumerate(processed_contents):
        background_image_path = background_path_provider(slide_index, slide)
        theme_name = theme_name_provider(slide_index, slide) if theme_name_provider else None
        theme_override = theme_override_provider(slide_index, slide) if theme_override_provider else None
        colors = _get_theme_colors(background_image_path, theme_name, theme_override)

        # Find the largest scale that fits the slide in the usable area
        scale = _find_adaptive_scale(
            slide, colors, colors["title_color"], colors["text_color"],
            text_width, page_height, usable_height,
        )
        styles = _build_styles(colors["title_color"], colors["text_color"], scale)
        gap_body  = max(4, int(10 * scale))
        gap_title = max(4, int(12 * scale))
        gap_blank = max(4, int(14 * scale))

        # Start from top of usable area
        y_start = page_height - top_margin

        # Draw
        _draw_background(pdf, background_image_path, page_width, page_height)
        y = y_start
        for raw_line in slide.splitlines():
            line = raw_line.strip()

            if not line:
                y -= gap_blank
            elif line.startswith("### "):
                paragraph = Paragraph(_markdown_inline_to_html(line[4:].strip(), colors["bold_color"]), styles["h3"])
                y = _draw_paragraph(
                    pdf, paragraph, text_left, y, text_width, bottom_margin,
                    page_height, top_margin, background_image_path, page_width,
                )
                y -= gap_title
            elif line.startswith("## "):
                paragraph = Paragraph(_markdown_inline_to_html(line[3:].strip(), colors["bold_color"]), styles["h2"])
                y = _draw_paragraph(
                    pdf, paragraph, text_left, y, text_width, bottom_margin,
                    page_height, top_margin, background_image_path, page_width,
                )
                y -= gap_title
            elif line.startswith("# "):
                paragraph = Paragraph(_markdown_inline_to_html(line[2:].strip(), colors["bold_color"]), styles["h1"])
                y = _draw_paragraph(
                    pdf, paragraph, text_left, y, text_width, bottom_margin,
                    page_height, top_margin, background_image_path, page_width,
                )
                y -= gap_title
            else:
                is_bullet = line.startswith("- ") or line.startswith("* ")
                content = line[2:].strip() if is_bullet else line
                html = _markdown_inline_to_html(content, colors["bold_color"])
                if is_bullet:
                    html = f"\u2022 {html}"
                paragraph = Paragraph(html, styles["bullet"] if is_bullet else styles["body"])
                y = _draw_paragraph(
                    pdf, paragraph, text_left, y, text_width, bottom_margin,
                    page_height, top_margin, background_image_path, page_width,
                )
                y -= gap_body

        if slide_index < len(processed_contents) - 1:
            pdf.showPage()

    pdf.save()
    return output_pdf_path


def _generate_pdf_with_auto_backgrounds(processed_contents, input_file_path, cover_image_path=None):
    output_dir = os.path.join(PROJECT_ROOT, "output")
    input_name = os.path.splitext(os.path.basename(input_file_path))[0]
    combined_content = "\n".join(processed_contents)
    selected_themes = _extract_theme_candidates(combined_content, count=3)

    output_paths = []
    for theme_name in selected_themes:
        theme_info = _resolve_theme_definition(theme_name)
        theme_label = theme_info.get("palette_name") or theme_name
        output_pdf_path = os.path.join(output_dir, f"{input_name}_auto_{_slugify(theme_label)}.pdf")
        auto_background_image, resolved_theme_name = _generate_auto_background(combined_content, theme_name)
        output_paths.append(
            _generate_pdf(
                processed_contents,
                output_pdf_path,
                lambda _slide_index, _slide, image=auto_background_image: image,
                lambda _slide_index, _slide, name=resolved_theme_name: name,
                cover_image_path=cover_image_path,
            )
        )

    return output_paths


def _slugify(value):
    safe = re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_")
    return safe or "palette"


def _generate_pdf_with_selected_palette(processed_contents, input_file_path, palette_name_or_path, cover_image_path=None):
    output_dir = os.path.join(PROJECT_ROOT, "output")
    input_name = os.path.splitext(os.path.basename(input_file_path))[0]
    palette_path = _resolve_palette_path(palette_name_or_path)
    palette_label = os.path.splitext(os.path.basename(palette_path))[0] if palette_path else "custom"
    output_pdf_path = os.path.join(output_dir, f"{input_name}_palette_{_slugify(palette_label)}.pdf")

    combined_content = "\n".join(processed_contents)
    custom_theme = get_theme_from_palette(palette_name_or_path)
    auto_background_image, _ = _generate_auto_background(combined_content, "general", custom_theme)

    generated = _generate_pdf(
        processed_contents,
        output_pdf_path,
        lambda _slide_index, _slide, image=auto_background_image: image,
        lambda _slide_index, _slide: None,
        lambda _slide_index, _slide, theme=custom_theme: theme,
        cover_image_path=cover_image_path,
    )
    return [generated]


def generatePdf(processed_contents, input_file_path, selected_palette=None, cover_image_path=None):
    _register_optional_fonts()
    if selected_palette:
        return _generate_pdf_with_selected_palette(processed_contents, input_file_path, selected_palette, cover_image_path)
    return _generate_pdf_with_auto_backgrounds(processed_contents, input_file_path, cover_image_path)

def process_md_file(file_path, selected_palette=None, cover_image_path=None):
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
    
    return generatePdf(processed_contents, file_path, selected_palette, cover_image_path)


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