# Un bibliotecario AI

Dopo anni di lavoro coi motori di ricerca storco un po' il naso quando vedo un sistema che non trova quello che voglio, ma capisco anche che non è sempre semplice creare un sistema ideale. Prendiamo il caso delle biblioteche, hanno migliaia di libri, in migliaia di versioni già indicizzare il contenuto coi metadati base non è banale. Nei libri recenti sono stati inserite alcune schede a corredo del libro, con immenso sforzo manuale di trascrizione del retro di copertina, immagino, ma nel 90% dei libri presenti è già tanto avere anno di pubblicazione, casa editrice, autore e dati principali. Solitamente si cerca un libro per titolo e/o autore, se sono esatti il sistema fa il suo dovere. Tuttavia, noi poveri utenti spesso non ricordiamo il titolo esatto o l'autore, ricordiamo di cosa parla una storia Es. "Un giallo ambientato in montagna con una ragazza scomparsa" 

Ovviamente il sistema attuale non può rispondere a questa definizione perché cerca parola per parola 
"UN + GIALLO + AMBIENTATO ..." . Un minimo di stopwords sarebbe forse stato fattibile, non parliamo dell'estrazione del genere "GIALLO" , ambientazione e argomento generale sono totalmente al di fuori della capacità del sistema. 

Ecco la sfida che mi sono posta. Estendere il sistema esistente per permettere ricerche complesse di questo tipo, in cosa può essere d'aiuto l'ai per questo?

GPT come molti modelli LLM è stato istruito partendo da migliaia di pagine web tra cui wikipedia e intere pagine di libri classici, questo vuol dire che conosce tutti i libri che sono stati usati per istruirlo? Assolutamente no.
Purtroppo per noi, lui usa questi libri per conoscere la lingua, non i libri in sé. Prende una frase nasconde alcune parole e prova ad indovinarle, questo è quello che è stato addestrato a fare,  quindi se voi chiedete i titoli di  "Un giallo ambientato in montagna con una ragazza scomparsa" vi darà anche centinaia di titoli, accattivanti, d'effetto,  ma non reali. Questo è un classico caso di allucinazione. Proprio perché lui non conosce i libri che ha usato per essere addestrato, conosce le frasi di una lingua. Le parole per lui sono vettori in uno spazio semantico, che stanno "vicine" ad altri vettori. L'LLM non ha una comprensione dell'entità libro. Ha letto le parole o a volte anche solo parte di esse, non ha capito un libro. 

Per fortuna però le Open AI sono andate oltre includendo agenti che sono in grado di cercare su web, su Wikipedia, in siti di recensioni e trovare titoli "VERI" (se glielo specificate) di 'gialli ambientati in montagna'.  Non è l'LLM ha saperlo, è il web e gli agenti che scansionano i siti e trovano questi titoli, compattano i titoli nel formato che vogliamo, e infine ci rimane da incrociarli coi libri davvero presenti in biblioteca e woilà ... il bibliotecario AI è finalmente diventato "intelligente" e "utile", con un po' di lavoro.

  
