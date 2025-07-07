
# Documento di Requisiti del Prodotto: Chatbot per la Revisione del Tempo

## 1. Introduzione

### 1.1 Scopo
Questo documento delinea i requisiti per lo sviluppo di un chatbot intelligente basato su LangChain, progettato per aiutare gli utenti a comprendere e analizzare il proprio tempo speso, basandosi sui dati degli eventi del calendario. L'obiettivo principale è fornire un'interfaccia conversazionale per l'analisi dei dati, consentendo agli utenti di ottenere approfondimenti sul loro utilizzo del tempo.

### 1.2 Obiettivi del Progetto
* Sviluppare un **AI Agent** robusto e reattivo utilizzando LangChain.
* Integrare un **repository di eventi del calendario** esistente come fonte di dati primaria.
* Fornire **analisi personalizzate** sull'allocazione del tempo tramite interazioni in linguaggio naturale.
* Migliorare l'**esperienza utente** con streaming e gestione della memoria conversazionale.
* Garantire l'**osservabilità** per un debug e un'ottimizzazione efficienti.

### 1.3 Pubblico di Destinazione
Questo chatbot è destinato a individui che desiderano ottenere una migliore comprensione di come spendono il loro tempo, professionisti che vogliono analizzare la loro produttività o le abitudini alimentari, e chiunque abbia un calendario digitale come fonte principale per tracciare le attività.

## 2. Panoramica del Prodotto

Il "Chatbot per la Revisione del Tempo" sarà un **AI Agent** conversazionale costruito con LangChain, capace di interagire con i dati del calendario dell'utente. Utilizzerà un approccio basato su **Agenti React** e **Strumenti personalizzati** per recuperare, analizzare e presentare informazioni sul tempo speso. Il chatbot supporterà la memoria conversazionale e offrirà un'esperienza utente fluida tramite lo streaming.

### 2.1 Architettura Generale
Il cuore del sistema sarà un **Agente LangChain** che orchesterà l'interazione tra l'utente, i dati del calendario e i modelli di linguaggio di grandi dimensioni (LLM). L'agente utilizzerà una serie di **Strumenti (Tools)** personalizzati per eseguire operazioni specifiche sui dati del calendario. La memoria conversazionale garantirà che il chatbot possa mantenere il contesto attraverso più interazioni.

## 3. Funzionalità Dettagliate

### 3.1 Funzionalità Core (Revisione del Tempo Generale)

* **Interfaccia Conversazionale:** Gli utenti potranno porre domande in linguaggio naturale sull'utilizzo del loro tempo (es. "Quanto tempo ho passato in riunioni la settimana scorsa?", "Quali attività mi hanno richiesto più tempo il mese scorso?").
* **Recupero Dati Calendario:** L'agente sarà in grado di recuperare eventi del calendario per intervalli di tempo specificati dall'utente (es. "ieri", "ultima settimana", "mese scorso", "dal... al...").
* **Categorizzazione Eventi:** Utilizzerà la logica di categorizzazione esistente dal repository del calendario o implementerà una categorizzazione dinamica basata sul contenuto dell'evento.
* **Analisi del Tempo Speso:** Eseguirà analisi sul tempo speso per categoria, identificando le attività più dispendiose in termini di tempo e fornendo riepiloghi.
* **Generazione di Report:** Formatterà i risultati dell'analisi in report leggibili e concisi, adatti alla presentazione all'utente.
* **Memoria Conversazionale:** Ricorderà le interazioni precedenti per supportare domande di follow-up e mantenere il contesto della conversazione.
* **Streaming:** Fornirà output in streaming per un'esperienza utente reattiva, inclusi i token generati dall'LLM e gli stati intermedi dell'agente.

### 3.2 Funzionalità Opzionali (Idee Alternative)

#### 3.2.1 Chatbot per la Revisione dell'Alimentazione (Food-focused)
* **Identificazione Eventi Alimentari:** Capacità di identificare e filtrare specificamente gli eventi legati al cibo o ai pasti dai dati del calendario (es. "pranzo", "cena", "spesa alimentare", "ristorante").
* **Analisi delle Abitudini Alimentari:** Analizzerà la frequenza dei pasti, i luoghi (casa vs. fuori), e se i dettagli lo consentono, la tipologia di cibo.
* **Output Strutturato per Alimenti:** Restituirà un riepilogo strutturato delle abitudini alimentari, potenzialmente con suggerimenti o osservazioni.

#### 3.2.2 Chatbot per la Revisione degli Obiettivi Lavorativi Annuali
* **Gestione Obiettivi:** Consente all'utente di definire o caricare i propri obiettivi annuali lavorativi.
* **Allineamento Eventi-Obiettivi:** Categorizza gli eventi del calendario in base alla loro rilevanza per ciascun obiettivo, potenzialmente utilizzando tecniche di incorporamento (embeddings) per il confronto semantico.
* **Analisi del Tempo per Obiettivo:** Calcola il tempo speso per ciascun obiettivo, evidenziando discrepanze o attività non allineate.
* **Report Obiettivi:** Fornisce report dettagliati sull'allocazione del tempo per ogni obiettivo, evidenziando progressi, sovraccarico o sotto-utilizzo.

## 4. Requisiti Tecnici

### 4.1 Componenti LangChain
* **Agente:** Implementazione di un **Agente React (Reasoning and Action)**.
* **Strumenti (Tools) Personalizzati:**
    * **`CalendarEventRetrievalTool`**: Per recuperare e categorizzare eventi del calendario. Dovrà essere **asincrono (`@tool.coroutine`)** per una migliore reattività.
    * **`DataAnalysisTool`**: Per eseguire analisi sui dati degli eventi categorizzati.
    * **`ReportingTool`**: Per formattare i risultati dell'analisi. Potrebbe utilizzare `with_structured_output` per garantire un formato prevedibile (es. JSON).
    * *(Per le funzionalità opzionali)*: `DietAnalysisTool`, `ObjectiveManagementTool`, `ObjectiveAlignmentTool`, `WorkTimeAnalysisTool`.
* **Memoria Conversazionale:** Utilizzo di `runnable with message history` con `messages placeholder`. Si valuterà l'uso di `ConversationBufferMemory` o `ConversationSummaryBufferMemory`.
* **Ingegneria dei Prompt:**
    * **System Prompt:** Chiaro e specifico sul ruolo del chatbot.
    * **User Prompt:** Strutturato per catturare la domanda e i vincoli.
    * **Agent Scratchpad:** Essenziale per il `Chain-of-Thought`.
* **LangChain Expression Language (LCEL):** Utilizzo dell'operatore pipe (`|`) per costruire catene e agenti modulari. Potenziale uso di `RunnableParallel` e `RunnablePassthrough`.
* **Streaming:** Implementazione tramite un `AsyncCallbackHandler` personalizzato (es. simile a `QCallbackHandler`) per trasmettere token e stati intermedi al frontend.

### 4.2 Backend e API
* **Framework API:** **FastAPI** per la creazione dell'API backend.
* **Operazioni Asincrone:** Forte enfasi sull'uso di `asyncio.gather` e altre pratiche asincrone per mantenere il chatbot reattivo.

### 4.3 Osservabilità
* **Integrazione LangSmith:** Utilizzo di LangSmith per visualizzare ogni passaggio dell'agente, inclusi LLM calls, tool inputs/outputs e token usage, facilitando il debug e l'ottimizzazione.

### 4.4 Fonte Dati
* **Repository Calendario Esistente:** Il chatbot si interfaccerà con il repository esistente per il download e la categorizzazione degli eventi del calendario.

## 5. Esperienza Utente (UX)

* **Interfaccia Chiara:** L'interfaccia utente (non inclusa in questo PRD ma da considerare per lo sviluppo frontend) dovrà essere intuitiva e facile da usare per interagire con il chatbot.
* **Feedback in Tempo Reale:** Lo streaming garantirà che l'utente riceva feedback immediato durante l'elaborazione delle richieste.
* **Risposte Chiare e Concisa:** Le risposte del chatbot dovranno essere ben formattate, facili da leggere e andare direttamente al punto, evitando verbosità inutili.

## 6. Considerazioni Future

* **Integrazione Diretta API Calendario:** Esplorare l'integrazione diretta con API di calendario (es. Google Calendar, Outlook) per eliminare la dipendenza da un repository locale pre-scaricato.
* **Visualizzazioni Dati:** Aggiungere la capacità di generare visualizzazioni grafiche dei dati (es. grafici a torta per la distribuzione del tempo).
* **Notifiche Proattive:** Sviluppare funzionalità per inviare notifiche proattive basate su anomalie o tendenze rilevate.
* **Personalizzazione Avanzata:** Consentire agli utenti di definire le proprie categorie di eventi o regole di analisi personalizzate.
