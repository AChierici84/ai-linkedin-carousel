import os
import re as _re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gradio as gr

from processMd import process_md_file

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


def generate_pdfs(content: str, filename: str):
    filepath, msg = save_md(content, filename)
    if "❌" in msg:
        return None, msg
    try:
        output_paths = process_md_file(filepath)
        return output_paths, f"✅ Generati {len(output_paths)} PDF"
    except Exception as exc:
        return None, f"❌ Errore: {exc}"


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
            preview = gr.Markdown(label="Anteprima", elem_id="preview-pane")

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

    # Toolbar — pure JS, no Python round-trip
    bold_btn.click(     fn=None, js=_wrap_js("**", "**"), outputs=editor)
    italic_btn.click(   fn=None, js=_wrap_js("*",  "*"),  outputs=editor)
    underline_btn.click(fn=None, js=_wrap_js("__", "__"), outputs=editor)
    link_btn.click(     fn=None, js=_LINK_JS,             outputs=editor)
    separator_btn.click(fn=None, js=_SEPARATOR_JS,        outputs=editor)

    # Save / Generate
    save_btn.click(fn=save_md,       inputs=[editor, filename_input], outputs=[md_download,  status_box])
    pdf_btn.click( fn=generate_pdfs, inputs=[editor, filename_input], outputs=[pdf_download, status_box])


if __name__ == "__main__":
    demo.launch(inbrowser=True, css=_CSS, theme=gr.themes.Soft())
