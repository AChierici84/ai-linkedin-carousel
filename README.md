# AI LinkedIn Carousel

Tool Python per generare un carousel PDF partendo da un file Markdown.

Ogni sezione del Markdown viene trasformata in una pagina del PDF. Per ogni immagine di sfondo presente nella root del progetto con nome `bkgN` viene generata una variante separata del PDF, salvata nella cartella `output`.

## Funzionalita

- Converte un file Markdown in un carousel PDF multipagina.
- Interpreta titoli Markdown `#`, `##`, `###`.
- Interpreta il grassetto inline con `**testo**`.
- Interpreta liste con `* elemento` oppure `- elemento`.
- Usa automaticamente ogni sfondo `bkg1.png`, `bkg2.png`, `bkg3.png`, ecc.
- Genera un PDF separato per ogni sfondo con suffisso `_bkgN`.
- Se lo sfondo e scuro usa testo chiaro.
- I titoli usano blu su sfondi chiari e azzurro su sfondi scuri.

## Struttura del progetto

```text
.
|-- input/
|   `-- post.md
|-- output/
|-- bkg1.png
|-- bkg2.png
|-- bkg3.png
`-- processMd.py
```

## Requisiti

- Python 3.10+
- `reportlab`
- `Pillow`

Installazione dipendenze:

```bash
pip install reportlab pillow
```

## Formato del Markdown

Il file Markdown deve stare dentro la cartella `input/`.

Le slide vengono separate con una riga che inizia con:

```text
----
```

Esempio:

```md
# Titolo slide 1

Questo e un testo con **grassetto**.

* Primo punto
* Secondo punto

----

## Titolo slide 2

Altro contenuto.
```

## Esecuzione

Da root progetto:

```bash
python processMd.py post.md
```

Il comando cerca automaticamente il file in `input/post.md`.

## Output

Se nella root sono presenti ad esempio:

- `bkg1.png`
- `bkg2.png`
- `bkg3.png`

e il file di input e `post.md`, i file generati saranno:

- `output/post_bkg1.pdf`
- `output/post_bkg2.pdf`
- `output/post_bkg3.pdf`

## Regole di stile applicate

- Titoli grandi per migliorare la leggibilita nel formato carousel.
- Corpo del testo e bullet con dimensione aumentata.
- Sfondo applicato a tutta la pagina.
- Colore del testo adattato automaticamente alla luminosita media dello sfondo.

## Limiti attuali

- Non interpreta tutto il Markdown standard.
- Supporta in modo esplicito titoli, grassetto inline e bullet list semplici.
- Gli sfondi devono essere nella root del progetto e chiamarsi `bkgN`.

## File principale

La logica principale si trova in [processMd.py](processMd.py).