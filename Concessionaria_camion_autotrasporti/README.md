## Setup dell’Ambiente di Sviluppo

Questo progetto utilizza un **ambiente virtuale** (`venv`).

L’ambiente virtuale serve a isolare le librerie necessarie al progetto (come Flask e i driver del database) dal resto del sistema, evitando conflitti tra dipendenze e problemi con altri progetti Python.

> **Nota:** La cartella `venv` non viene tracciata da Git. Ogni sviluppatore deve creare il proprio ambiente virtuale localmente seguendo i passaggi riportati di seguito.

### 1. Creare l’ambiente virtuale

Dopo aver clonato il repository, aprire il terminale nella cartella principale del progetto ed eseguire:

```bash
python -m venv venv
```

> **Nota:** Se il comando non funziona, provare ad aprire il terminale come amministratore ed eseguirlo nuovamente dalla cartella del progetto.

### 2. Attivare l’ambiente virtuale

Su Windows:

```bash
.\venv\Scripts\activate
```

Dopo l’attivazione del `venv`, nel terminale comparirà il prefisso `(venv)`.

### 3. Installare le dipendenze

Installare Flask tramite `pip`:

```bash
pip install Flask
```

### 4. Avviare l’applicazione

Per eseguire il progetto:

```bash
python app.py
```

---

## Relazione LaTeX

Link alla relazione su Overleaf:

https://www.overleaf.com/2982212473tfxjtbdkfbbw#9be521:contentReference
