import os
import re as _re
import sys
import math
from html import escape as _escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gradio as gr

from processMd import get_palette_roles, list_palette_files, process_md_file

_INPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "input")


# ── Python helpers ────────────────────────────────────────────────────────────

def _md_to_preview(text: str) -> str:
    """Preprocess markdown text for Gradio Markdown preview."""
    if not text:
        return ""
    # __text__ → <u>text</u>  (Gradio markdown passes inline HTML through)
    result = _re.sub(r"(?<!\w)__(.+?)__(?!\w)", r"<u>\1</u>", text)
    # ---- slide separator → visible <hr>
    result = _re.sub(r"^----\s*$", "---", result, flags=_re.MULTILINE)
    return result


def save_md(content: str, filename: str):
    filename = (filename or "post").strip()
    if not filename.endswith(".md"):
        filename += ".md"
    os.makedirs(_INPUT_DIR, exist_ok=True)
    filepath = os.path.join(_INPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as fh:
        fh.write(content or "")
    return filepath, f"✅ Salvato: {filepath}"


def generate_pdfs(content: str, filename: str, selected_palette: str):
    filepath, msg = save_md(content, filename)
    if "❌" in msg:
        return None, msg
    try:
        output_paths = process_md_file(filepath, selected_palette=selected_palette)
        theme_msg = f" con palette '{selected_palette}'" if selected_palette else ""
        return output_paths, f"✅ Generati {len(output_paths)} PDF{theme_msg}"
    except Exception as exc:
        return None, f"❌ Errore: {exc}"


def _render_palette_swatches(selected_palette: str) -> str:
    if not selected_palette:
        return "<div>Nessuna palette selezionata.</div>"

    roles = get_palette_roles(selected_palette)
    ordered = roles.get("ordered", [])
    if not ordered:
        return "<div>Impossibile leggere i colori della palette.</div>"

    blocks = []
    labels = {
        roles["background"]: "sfondo",
        roles["bold"]: "bold",
        roles["title"]: "titoli",
        roles["text"]: "testo",
    }
    for color in ordered:
        label = labels.get(color, "")
        label_html = f"<div style='font-size:11px; color:#333;'>{label}</div>" if label else ""
        blocks.append(
            "<div style='display:flex; flex-direction:column; align-items:center; gap:4px;'>"
            f"<div title='{color}' style='width:56px; height:56px; border-radius:10px; border:1px solid #DDD; background:{color};'></div>"
            f"<div style='font-size:11px; color:#444;'>{color}</div>"
            f"{label_html}"
            "</div>"
        )
    return "<div style='display:flex; gap:10px; flex-wrap:wrap; align-items:flex-start;'>" + "".join(blocks) + "</div>"


def _render_pdf_preview(content: str, selected_palette: str) -> str:
    roles = get_palette_roles(selected_palette) if selected_palette else None
    if not roles:
        return "<div>Seleziona una palette per vedere l'anteprima.</div>"

    first_slide = (content or "").split("----", 1)[0]

    def _adaptive_scale(slide_text: str) -> float:
        lines = slide_text.splitlines()
        if not any(line.strip() for line in lines):
            return 1.0

        def _estimate_height(scale: float) -> float:
            h1_size = 29 * scale
            h2_size = 25 * scale
            h3_size = 22 * scale
            body_size = 17 * scale
            line_h1 = h1_size * 1.2
            line_h2 = h2_size * 1.25
            line_h3 = h3_size * 1.25
            line_body = body_size * 1.45
            gap_blank = 8 * scale
            gap_block = 6 * scale

            # Conservative wrap model for preview card width.
            max_chars_body = max(16, int(46 / scale))
            max_chars_h1 = max(10, int(28 / scale))
            max_chars_h2 = max(12, int(32 / scale))
            max_chars_h3 = max(14, int(36 / scale))

            total = 0.0
            for raw in lines:
                line = raw.strip()
                if not line:
                    total += gap_blank
                    continue

                if line.startswith("# "):
                    text = line[2:].strip()
                    wraps = max(1, math.ceil(len(text) / max_chars_h1))
                    total += wraps * line_h1 + gap_block
                    continue
                if line.startswith("## "):
                    text = line[3:].strip()
                    wraps = max(1, math.ceil(len(text) / max_chars_h2))
                    total += wraps * line_h2 + gap_block
                    continue
                if line.startswith("### "):
                    text = line[4:].strip()
                    wraps = max(1, math.ceil(len(text) / max_chars_h3))
                    total += wraps * line_h3 + gap_block
                    continue

                is_bullet = line.startswith("- ") or line.startswith("* ")
                text = line[2:].strip() if is_bullet else line
                wraps = max(1, math.ceil(len(text) / max_chars_body))
                total += wraps * line_body + gap_block

            return total

        target_height = 610.0
        low = 0.56
        high = 1.12
        for _ in range(16):
            mid = (low + high) / 2
            if _estimate_height(mid) > target_height:
                high = mid
            else:
                low = mid
        return low

    scale = _adaptive_scale(first_slide)
    h1_size = max(18, int(29 * scale))
    h2_size = max(16, int(25 * scale))
    h3_size = max(15, int(22 * scale))
    body_size = max(13, int(17 * scale))
    blank_gap = max(4, int(8 * scale))

    def _inline_md_to_html(text: str) -> str:
        html = _escape(text)
        html = _re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2" style="color:inherit; text-decoration:underline;">\1</a>', html)
        html = _re.sub(r"(?<!\w)__(.+?)__(?!\w)", r"<u>\1</u>", html)
        html = _re.sub(r"\*\*(.+?)\*\*", rf'<strong style="color:{roles["bold"]};">\1</strong>', html)
        html = _re.sub(r"(?<!\*)\*(?!\*)([^*]+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", html)
        html = _re.sub(r"(?<!\w)_(?!_)(.+?)(?<!_)_(?!\w)", r"<em>\1</em>", html)
        return html

    rendered_lines = []
    for line in first_slide.splitlines():
        clean = line.strip()
        if not clean:
            rendered_lines.append(f"<div style='height:{blank_gap}px;'></div>")
            continue

        if clean.startswith("### "):
            content_html = _inline_md_to_html(clean[4:].strip())
            rendered_lines.append(
                f"<div style='font-family:Helvetica, Arial, sans-serif; font-size:{h3_size}px; font-weight:700; line-height:1.25; color:{roles['title']};'>{content_html}</div>"
            )
            continue

        if clean.startswith("## "):
            content_html = _inline_md_to_html(clean[3:].strip())
            rendered_lines.append(
                f"<div style='font-family:Helvetica, Arial, sans-serif; font-size:{h2_size}px; font-weight:700; line-height:1.25; color:{roles['title']};'>{content_html}</div>"
            )
            continue

        if clean.startswith("# "):
            content_html = _inline_md_to_html(clean[2:].strip())
            rendered_lines.append(
                f"<div style='font-family:Helvetica, Arial, sans-serif; font-size:{h1_size}px; font-weight:700; line-height:1.2; color:{roles['title']};'>{content_html}</div>"
            )
            continue

        is_bullet = clean.startswith("- ") or clean.startswith("* ")
        content_html = _inline_md_to_html(clean[2:].strip() if is_bullet else clean)
        if is_bullet:
            rendered_lines.append(
                f"<div style='font-family:Helvetica, Arial, sans-serif; font-size:{body_size}px; line-height:1.45; color:{roles['text']}; display:flex; gap:8px; align-items:flex-start;'>"
                f"<span style='line-height:1.3;'>•</span><span>{content_html}</span></div>"
            )
        else:
            rendered_lines.append(
                f"<div style='font-family:Helvetica, Arial, sans-serif; font-size:{body_size}px; line-height:1.45; color:{roles['text']};'>{content_html}</div>"
            )

    if not rendered_lines:
        rendered_lines = [
            f"<div style='font-family:Helvetica, Arial, sans-serif; font-size:{h1_size}px; font-weight:700; line-height:1.2; color:{roles['title']};'>Titolo slide</div>",
            f"<div style='font-family:Helvetica, Arial, sans-serif; font-size:{body_size}px; line-height:1.45; color:{roles['text']};'>Testo anteprima del PDF</div>",
            f"<div style='font-family:Helvetica, Arial, sans-serif; font-size:{max(14, int(body_size * 1.05))}px; font-weight:700; color:{roles['bold']};'>Testo in grassetto</div>",
        ]

    bg_color = roles["background"]
    gradient_end = roles["bold"]

    return f"""
<div style="border:1px solid #D8D8D8; border-radius:14px; padding:10px; background:#fff;">
  <div style="font-size:12px; color:#666; margin-bottom:8px;">Anteprima stile PDF</div>
    <div style="width:100%; max-width:760px; margin:0 auto; aspect-ratio:4/5; border-radius:12px; padding:18px; background:linear-gradient(180deg, {bg_color} 0%, {gradient_end} 100%); display:flex; flex-direction:column; gap:10px; justify-content:flex-start; overflow:hidden; box-sizing:border-box;">
    {''.join(rendered_lines)}
  </div>
</div>
"""


def refresh_theme_preview(content: str, selected_palette: str):
    return _render_palette_swatches(selected_palette), _render_pdf_preview(content, selected_palette)


# ── JavaScript for toolbar buttons ───────────────────────────────────────────
# Each function runs entirely client-side; the return value updates the editor.

def _wrap_js(prefix: str, suffix: str) -> str:
    """Return a JS arrow-function that wraps the selected textarea text."""
    p = prefix.replace("\\", "\\\\").replace("'", "\\'")
    s = suffix.replace("\\", "\\\\").replace("'", "\\'")
    pl = len(prefix)
    return f"""() => {{
    const ta = document.querySelector('#md-editor textarea');
    if (!ta) return [''];
    const start = ta.selectionStart, end = ta.selectionEnd;
    const selected = ta.value.substring(start, end) || 'testo';
    const newVal = ta.value.substring(0, start) + '{p}' + selected + '{s}' + ta.value.substring(end);
    ta.value = newVal;
    ta.dispatchEvent(new Event('input', {{bubbles: true}}));
    ta.selectionStart = start + {pl};
    ta.selectionEnd   = end   + {pl};
    ta.focus();
    return [newVal];
}}"""


_LINK_JS = """() => {
    const ta = document.querySelector('#md-editor textarea');
    if (!ta) return [''];
    const start = ta.selectionStart, end = ta.selectionEnd;
    const selected = ta.value.substring(start, end) || 'testo';
    const url = window.prompt('URL del link:', 'https://');
    if (!url) return [ta.value];
    const insert = '[' + selected + '](' + url + ')';
    const newVal = ta.value.substring(0, start) + insert + ta.value.substring(end);
    ta.value = newVal;
    ta.dispatchEvent(new Event('input', {bubbles: true}));
    const newPos = start + insert.length;
    ta.selectionStart = newPos;
    ta.selectionEnd   = newPos;
    ta.focus();
    return [newVal];
}"""

_SEPARATOR_JS = r"""() => {
    const ta = document.querySelector('#md-editor textarea');
    if (!ta) return [''];
    const pos = ta.selectionStart;
    const before = ta.value.substring(0, pos);
    const after  = ta.value.substring(pos);
    const sep = '\n\n----\n\n';
    const newVal = before + sep + after;
    ta.value = newVal;
    ta.dispatchEvent(new Event('input', {bubbles: true}));
    const newPos = pos + sep.length;
    ta.selectionStart = newPos;
    ta.selectionEnd   = newPos;
    ta.focus();
    return [newVal];
}"""


# ── CSS ───────────────────────────────────────────────────────────────────────

_CSS = """
/* Toolbar */
#toolbar { gap: 4px !important; align-items: center; flex-wrap: wrap; }
#toolbar button {
    min-width: 38px !important;
    max-width: 80px;
    padding: 4px 8px !important;
    font-size: 14px !important;
}
#bold-btn   { font-weight: 900 !important; }
#italic-btn { font-style: italic !important; }
#ul-btn     { text-decoration: underline !important; }

/* Monospace editor */
#md-editor textarea {
    font-family: 'Consolas', 'Courier New', monospace !important;
    font-size: 14px !important;
    line-height: 1.65 !important;
}

/* Preview pane */
#preview-pane { min-height: 500px; }

#theme-preview { min-height: 380px; }
"""

_PLACEHOLDER = """\
# Titolo della prima slide

Introduci il tuo argomento con una frase d'impatto.

- Punto chiave **uno**
- Punto chiave *due*
- Punto chiave __tre__ (sottolineato)

----

## Slide 2 — Dettagli

Approfondisci il tema con dati o esempi concreti.

Per saperne di più visita [il mio profilo](https://linkedin.com).
"""

# ── Gradio UI ─────────────────────────────────────────────────────────────────

with gr.Blocks(title="LinkedIn Carousel Editor") as demo:

    gr.Markdown("## ✏️ LinkedIn Carousel Editor")

    palette_options = list_palette_files()
    default_palette = palette_options[0] if palette_options else None

    # ── Filename row ──────────────────────────────────────────────────────────
    with gr.Row():
        filename_input = gr.Textbox(
            value="post",
            label="Nome file",
            info="Senza estensione — verrà salvato come .md in input/",
            scale=1,
            max_lines=1,
            min_width=220,
        )
        palette_dropdown = gr.Dropdown(
            choices=palette_options,
            value=default_palette,
            label="Tema (cartella palette)",
            info="I colori vengono letti dall'immagine selezionata.",
            scale=1,
            min_width=280,
        )

    palette_swatches = gr.HTML(
        label="Colori palette in riga",
        value=_render_palette_swatches(default_palette),
    )

    # ── Formatting toolbar ────────────────────────────────────────────────────
    with gr.Row(elem_id="toolbar"):
        bold_btn      = gr.Button("B",          size="sm", elem_id="bold-btn",   min_width=38)
        italic_btn    = gr.Button("I",          size="sm", elem_id="italic-btn", min_width=38)
        underline_btn = gr.Button("U",          size="sm", elem_id="ul-btn",     min_width=38)
        link_btn      = gr.Button("🔗 Link",    size="sm", min_width=80)
        separator_btn = gr.Button("⊟ Nuova slide", size="sm", min_width=110)

    # ── Editor + Preview ──────────────────────────────────────────────────────
    with gr.Row():
        with gr.Column(scale=1):
            editor = gr.Textbox(
                label="Editor (Markdown)",
                lines=28,
                elem_id="md-editor",
                placeholder=_PLACEHOLDER,
            )
        with gr.Column(scale=1):
            with gr.Tabs():
                with gr.Tab("Anteprima Markdown"):
                    preview = gr.Markdown(label="Anteprima", elem_id="preview-pane")
                with gr.Tab("Anteprima PDF"):
                    theme_preview = gr.HTML(
                        label="Anteprima PDF con palette",
                        value=_render_pdf_preview("", default_palette),
                        elem_id="theme-preview",
                    )

    # ── Action buttons ────────────────────────────────────────────────────────
    with gr.Row():
        save_btn = gr.Button("💾 Salva .md",   variant="secondary", scale=1)
        pdf_btn  = gr.Button("📄 Genera PDF",  variant="primary",   scale=2)

    status_box = gr.Textbox(label="Stato", interactive=False, max_lines=2)

    with gr.Row():
        md_download  = gr.File(label="File .md salvato",  interactive=False)
        pdf_download = gr.File(label="PDF generati",       interactive=False, file_count="multiple")

    # ── Bindings ──────────────────────────────────────────────────────────────

    # Live preview (Python — handles __underline__ conversion)
    editor.change(fn=_md_to_preview, inputs=editor, outputs=preview)
    editor.change(fn=refresh_theme_preview, inputs=[editor, palette_dropdown], outputs=[palette_swatches, theme_preview])
    palette_dropdown.change(fn=refresh_theme_preview, inputs=[editor, palette_dropdown], outputs=[palette_swatches, theme_preview])

    # Toolbar — pure JS, no Python round-trip
    bold_btn.click(     fn=None, js=_wrap_js("**", "**"), outputs=editor)
    italic_btn.click(   fn=None, js=_wrap_js("*",  "*"),  outputs=editor)
    underline_btn.click(fn=None, js=_wrap_js("__", "__"), outputs=editor)
    link_btn.click(     fn=None, js=_LINK_JS,             outputs=editor)
    separator_btn.click(fn=None, js=_SEPARATOR_JS,        outputs=editor)

    # Save / Generate
    save_btn.click(fn=save_md,       inputs=[editor, filename_input], outputs=[md_download,  status_box])
    pdf_btn.click( fn=generate_pdfs, inputs=[editor, filename_input, palette_dropdown], outputs=[pdf_download, status_box])


if __name__ == "__main__":
    demo.launch(inbrowser=True, css=_CSS, theme=gr.themes.Soft())
