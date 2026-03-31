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

- **Selettore tema** dalla cartella `palette/`
- **Colori palette in riga** con ruoli visivi mostrati nella UI
- **Anteprima live** del Markdown in tab dedicato
- **Anteprima PDF** in tab dedicato con gradiente, font e colori coerenti con il PDF finale
- **Salva .md** → salva il file in `input/` e offre il download
- **Genera PDF** → salva il file e produce un PDF usando la palette selezionata

---

## Avvio rapido — CLI

```bash
python processMd.py post.md
```

Il comando cerca il file in `input/post.md` e genera i PDF in `output/`.
Da CLI il motore usa la selezione automatica dei temi; dalla UI puoi invece forzare una palette specifica.

---

## Funzionalità del motore PDF

- Converte Markdown in carousel PDF multipagina (formato A4)
- Titoli `#`, `##`, `###` con dimensione scalata automaticamente al contenuto della slide
- Grassetto `**testo**`, corsivo `*testo*` / `_testo_`, sottolineato `__testo__`
- Link `[testo](url)` cliccabili nel PDF
- Bullet list con `- elemento` o `* elemento`
- Sfondi generati in memoria con gradiente verticale basato sulla palette selezionata
- Mappatura ruoli colore da palette immagine: più scuro → sfondo, secondo meno scuro → grassetto, terzo meno scuro → titoli, più chiaro → testo
- **UI**: genera 1 PDF con la palette scelta manualmente
- **CLI / auto-mode**: genera 3 PDF usando temi keyword-based mappati a palette reali della cartella `palette/`
- Colori della palette rispettati nel PDF finale senza sostituzione automatica con bianco/nero quando il tema è esplicito

---

## Palette e temi automatici

- La cartella `palette/` contiene immagini palette (`.jpg`, `.jpeg`, `.png`, `.webp`)
- La UI ti permette di scegliere direttamente una palette dalla cartella
- Il motore estrae i colori dominanti dall'immagine palette e assegna i ruoli grafici in automatico
- I temi automatici (`ai`, `vision`, `health`, `data`, `growth`, `business`, `finance`, `security`, `education`, `manual`, `general`) sono mappati a file palette reali
- In modalità automatica i file generati hanno nome simile a `{file}_auto_<palette>.pdf`
- In modalità manuale il file generato ha nome simile a `{file}_palette_<palette>.pdf`

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
├── app.py           ← UI Gradio con editor, tema, anteprime e generazione PDF
├── processMd.py     ← motore PDF e gestione palette/temi
├── palette/         ← immagini palette selezionabili dalla UI
├── input/
│   └── post.md
└── output/
    ├── post_auto_<palette>.pdf
    └── post_palette_<palette>.pdf
```

---

## Uso da Python

Se vuoi forzare una palette specifica senza passare dalla UI:

```python
from processMd import process_md_file

process_md_file("input/post.md", selected_palette="AdobeColor-Offender 2020.jpeg")
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