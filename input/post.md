# Manuale Tecnico 

## Da un pdf a un assistente interattivo.

Hai mai comprato un elettrodomestico e ti sei trovato a sfogliare un manuale enorme: 
* cercando la tua lingua, 
* leggendo un documento su due colonne con caratteri minuscoli, 
* cercando di capire come farlo funzionare? 🤯

Oppure, peggio ancora, inquadri un **QR code** che ti fa scaricare un PDF sullo smartphone… 
e poi scorri disperato alla ricerca delle istruzioni giuste?

------------------------------

Forse ciò di cui abbiamo davvero bisogno è una **RAG**.

**RAG** => **Retrieval-Augmented Generation**

In pratica, si tratta di:
* convertire il manuale in embeddings (vettori numerici nello spazio semantico) 
* indicizzarlo, 

=> così da poter cercare rapidamente frammenti utili per rispondere a una domanda specifica.

💡 Esempio: “Come installo la base di ricarica del clean robot AXYZD?”

--------------------------------

**Perché non chiedere a un LLM generico?**

Non puoi essere sicuro che la risposta si riferisca al tuo **modello specifico**.
Potresti ricevere **informazioni obsolete o relative a marche concorrenti**.

--------------------------------

Le **RAG** limitano il campo d’azione dell’LLM,
sfruttandone la capacità conversazionale 
solo sui contenuti ufficiali.

--------------------------------

Il processo è semplice, ma potente:

1. L’LLM riceve frammenti specifici del manuale, corredati di foto e didascalie.
2. Risponde alla domanda dell’utente basandosi solo su questi contenuti.
3. Se non ha abbastanza informazioni, ammette di non sapere, evitando risposte vaghe o dannose.

-----------------------------------

⚡ **Vantaggi concreti delle RAG multimodali:**

- Riduzione drastica delle allucinazioni
- Controllo completo sul contenuto fornito
- Aggiornamento facile: basta rigenerare gli embeddings quando il manuale cambia. 
- Possibilità di includere immagini come supporto esplicativo

------------------------------------

In pratica, il cliente ha un manuale interattivo affidabile, 
capace di guidarlo passo passo, anche in contesti delicati.

----------------------------------------

I motori di ricerca fanno qualcosa di simile “on demand”, 
cercando contenuti online e componendo la risposta 
come un riassunto di quanto trovato, 
ma senza garanzie sulle fonti.

-----------------------------------------

Con una **RAG**, **il controllo è totale**, 
**le risposte sono affidabili** e 
l’esperienza utente migliora drasticamente.