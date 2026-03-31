# AI LinkedIn Carousel

Tool Python per generare carousel PDF multi-tema partendo da un file Markdown.  
Disponibile sia come **interfaccia grafica** (Gradio) che come **CLI**.

---

## Avvio rapido — UI grafica

```bash
python app.py
```

Si apre automaticamente il browser su `http://localhost:7860`.

### Funzionalità dell'editor

| Pulsante | Effetto | Sintassi inserita |
|---|---|---|
| **B** | Grassetto | `**testo**` |
| *I* | Corsivo | `*testo*` |
| U | Sottolineato | `__testo__` |
| 🔗 Link | Link (prompt URL) | `[testo](url)` |
| ⊟ Nuova slide | Separatore slide | `----` |

- **Anteprima live** del Markdown nella colonna destra
- **Salva .md** → salva il file in `input/` e offre il download
- **Genera PDF** → salva il file e produce 3 PDF tematici in `output/`

---

## Avvio rapido — CLI

```bash
python processMd.py post.md
```

Il comando cerca il file in `input/post.md` e genera i PDF in `output/`.

---

## Funzionalità del motore PDF

- Converte Markdown in carousel PDF multipagina (formato A4)
- Titoli `#`, `##`, `###` con dimensione scalata automaticamente al contenuto della slide
- Grassetto `**testo**`, corsivo `*testo*` / `_testo_`, sottolineato `__testo__`
- Link `[testo](url)` cliccabili nel PDF
- Bullet list con `- elemento` o `* elemento`
- **3 PDF tematici** generati per ogni file: i 3 temi più rilevanti vengono selezionati in base alle parole chiave presenti nel testo
- Sfondi generati in memoria (nessun PNG intermedio salvato su disco)
- Colori testo con controllo automatico **WCAG** (contrasto minimo 4.5:1 per testo/bold, 3:1 per titoli)
- Separazione visiva garantita tra colore testo normale e colore grassetto (≥ 1.2:1)

---

## Temi disponibili

| Tema | Colori base |
|---|---|
| `ai` | Nero → blu acciaio → azzurro |
| `vision` | Blu medio → ciano → acqua |
| `health` | Verde petrolio scuro → verde acqua |
| `data` | Blu ardesia → azzurro → cielo |
| `growth` | Blu notte → rosso corallo → arancio → giallo |
| `business` | Verde scuro → teal → rosso corallo |
| `finance` | Viola scuro → lilla → rosa |
| `security` | Bordeaux scuro → rosso → rosa chiaro |
| `education` | Viola → lilla → azzurro ghiaccio |
| `manual` | Blu petrolio → verde salvia → verde menta |
| `general` | Quasi nero → blu → malva |

Il tema viene scelto automaticamente: per ogni file vengono prodotti 3 PDF con nome `{file}_auto_{tema}.pdf`.

---

## Formato del Markdown

Le slide vengono separate con `----`:

```md
# Titolo slide 1

Testo con **grassetto**, *corsivo*, __sottolineato__.

Visita [il mio sito](https://example.com).

- Primo punto
- Secondo punto

----

## Titolo slide 2

Altro contenuto.
```

---

## Struttura del progetto

```text
.
├── app.py           ← UI Gradio
├── processMd.py     ← motore PDF
├── palette.jpg      ← riferimento palette colori
├── input/
│   └── post.md
└── output/
    └── post_auto_<tema>.pdf
```

---

## Requisiti

- Python 3.10+
- `reportlab`
- `Pillow`
- `gradio`

```bash
pip install reportlab pillow gradio
```