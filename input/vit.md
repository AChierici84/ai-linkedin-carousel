## Hook

I **Vision Transformer** stanno cambiando la Computer Vision

Per anni le CNN sono state lo standard.
Ora qualcosa sta cambiando.

----------------------------------------

## Il punto di partenza

Le CNN (Convolutional Neural Networks)
analizzano le immagini localmente.

➡️ Guardano piccoli pezzi alla volta
➡️ Costruiscono il significato strato dopo strato

-----------------------------------------

## Il cambio di paradigma

I **Vision Transformer (ViT)** fanno qualcosa di diverso:

👉 Trattano l’immagine come una sequenza
(proprio come fosse testo)

-----------------------------------------

## Come funziona

1. L’immagine → divisa in **patch** (es. 16x16)
2. Ogni **patch** → trasformata in **vettore**
3. Aggiunta informazione posizionale

------------------------------------------

## Il cuore del modello

La sequenza passa nei **Transformer Encoder**

✔️ Self-attention
✔️ MLP
✔️ Residual + LayerNorm

-------------------------------------------

## Il vero vantaggio

💡 Ogni patch “vede” subito tutta l’immagine.

➡️ Comprensione globale immediata
➡️ Relazioni a lungo raggio
➡️ Meno dipendenza da kernel fissi

-------------------------------------------

## Caso concreto

🏥 Immagina una lastra medica:

👉 Individuare una massa
👉 Capire il contesto globale subito

Qui la differenza è reale.

-----------------------------------------

## I compromessi

⚖️ Non è tutto perfetto:

❌ Modelli molto grandi
❌ Servono tanti dati
❌ Costosi da addestrare da zero

-------------------------------------------

## Best practice

✅ Funzionano meglio così:

👉 Pre-trained
👉 Fine-tuning sul task specifico

--------------------------------------------

## Conclusione

🚀 I ViT non sostituiscono le CNN.

Ma sono una svolta quando serve:
✔️ Precisione
✔️ Contesto globale

E in alcuni casi… 
possono fare la differenza tra **errore** e 
una **diagnosi**.