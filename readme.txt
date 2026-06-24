=========================================================
      AUTOTRASPORTI S.R.L. - GESTIONALE CONCESSIONARIA
=========================================================

Benvenuto nel sistema gestionale per la concessionaria "Autotrasporti S.r.l.". 
Questo documento ti guiderà passo dopo passo nell'installazione e nell'avvio del progetto sul tuo computer.

---------------------------------------------------------
 1. REQUISITI DI SISTEMA
---------------------------------------------------------
Per eseguire correttamente il programma, assicurati di avere installato sul tuo computer:
- Python 3.8 o versioni successive (scaricabile da python.org)
- pip (il gestore di pacchetti di Python, solitamente incluso con Python)

---------------------------------------------------------
 2. CONFIGURAZIONE DEL DATABASE (File .env)
---------------------------------------------------------
Il sistema si appoggia a un database cloud Supabase. Per questioni di sicurezza, le chiavi di accesso non sono incluse nel codice.

1. Crea un nuovo file vuoto nella cartella principale del progetto (la stessa cartella dove si trova il file run.py) e chiamalo esattamente:  .env
2. Apri il file .env con un blocco note e inserisci le seguenti due righe, sostituendo i valori con le tue credenziali Supabase reali:

SUPABASE_URL=inserisci_qui_il_tuo_url_di_supabase
SUPABASE_KEY=inserisci_qui_la_tua_anon_key_di_supabase

3. Salva e chiudi il file .env.

---------------------------------------------------------
 3. INSTALLAZIONE DELLE LIBRERIE
---------------------------------------------------------
Prima di avviare il programma, devi installare le librerie necessarie (Flask per il web server, Supabase per il DB, ecc.).

1. Apri il Terminale (Prompt dei comandi su Windows o Terminale su Mac/Linux).
2. Naviga fino alla cartella principale del progetto.
3. (Opzionale ma consigliato) Crea un ambiente virtuale per non "sporcare" il tuo PC:
   - Windows:  python -m venv venv  --> per attivarlo: venv\Scripts\activate
   - Mac/Linux: python3 -m venv venv --> per attivarlo: source venv/bin/activate
4. Installa i requisiti eseguendo il seguente comando:
   pip install -r requirements.txt

---------------------------------------------------------
 4. AVVIO DELL'APPLICAZIONE
---------------------------------------------------------
Una volta installati i requisiti e configurato il file .env, sei pronto per partire.

1. Nel terminale, sempre dalla cartella principale del progetto, digita:
   python run.py

   (Se usi Mac o Linux, potresti dover digitare: python3 run.py)

2. Se tutto è configurato correttamente, vedrai nel terminale un messaggio simile a questo:
   * Running on http://127.0.0.1:5000

3. Apri il tuo browser preferito (Chrome, Edge, Safari, ecc.) e vai all'indirizzo:
   http://127.0.0.1:5000

---------------------------------------------------------
 5. COME TESTARE IL SISTEMA (Ruoli e Accessi)
---------------------------------------------------------
Il gestionale prevede diverse interfacce a seconda di chi effettua il login. 
Puoi registrarti dalla pagina di Login come "Cliente" (Ruolo 1).

Per testare le aree aziendali, devi utilizzare account preesistenti nel database o modificarne manualmente il ruolo dal pannello di Supabase. I ruoli sono:
- Ruolo 1: Cliente (Prenota test drive, offre usato, acquista)
- Ruolo 2: Meccanico (Gestisce l'officina e le perizie)
- Ruolo 3: Venditore (Area Business, gestione contratti)
- Ruolo 4: Amministratore (Dashboard completa, statistiche e gestione dipendenti)
- Ruolo 5: Impiegato Ufficio (Gestione base catalogo)

Credenziali per l'accesso:
	mail			password
-cliente@mail.it		pass
-meccanico@mail.it		pass
-venditore@mail.it		pass
-admin@mail.it			pass
-impiegato@mail.it		pass