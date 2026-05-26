from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def dashboard():
    # ==========================================
    # 1. KPI (Key Performance Indicators)
    # ==========================================
    # SUGGERIMENTO SQL PER IL BACKEND:
    # Auto: SELECT COUNT(*) FROM VEICOLO WHERE Stato_Disponibilita = 'D' (o 'Disponibile');
    # Vendite: SELECT COUNT(*) FROM VENDITA WHERE EXTRACT(MONTH FROM Data_Vendita) = EXTRACT(MONTH FROM CURRENT_DATE);
    # Clienti: SELECT COUNT(*) FROM CLIENTE;
    # Officina: SELECT COUNT(*) FROM INTERVENTO WHERE Data_Inizio = CURRENT_DATE;
    
    kpi_data = {
        'auto_disponibili': 115,
        'vendite_mese': 42,
        'clienti_registrati': 890,
        'interventi_oggi': 18
    }

    # ==========================================
    # 2. DATI GRAFICI
    # ==========================================
    # SUGGERIMENTO SQL PER IL BACKEND (Vendite per Modello):
    # SELECT Modello, COUNT(*) as Totale FROM VEICOLO v JOIN VENDITA vd ON v.ID_Contratto = vd.ID_Contratto GROUP BY Modello;
    grafico_modelli = {
        'labels': ['Panda', 'Giulietta', 'Giulia', '500', 'Stelvio'],
        'data': [90, 75, 55, 45, 30]
    }

    # ==========================================
    # 3. TABELLE DATI RECENTI
    # ==========================================
    
    # SUGGERIMENTO SQL:
    # SELECT p.ID_Preventivo, per.Nome, per.Cognome, v.Modello, p.Stato_PreventivoChiuso 
    # FROM PREVENTIVO p JOIN PERSONA per ON p.Pos_ID_Persona = per.ID_Persona 
    # JOIN VEICOLO v ON p.NumeroTelaio = v.NumeroTelaio ORDER BY p.ID_Preventivo DESC LIMIT 5;
    preventivi_recenti = [
        {'id': 'P001', 'cliente': 'Mario Rossi', 'auto': 'Panda', 'data': '15/05/2026', 'stato': 'Aperto'},
        {'id': 'P002', 'cliente': 'Luca Bianchi', 'auto': 'Giulia', 'data': '14/05/2026', 'stato': 'Chiuso'},
        {'id': 'P003', 'cliente': 'Giulia Verdi', 'auto': 'Giulietta', 'data': '14/05/2026', 'stato': 'Aperto'},
    ]

    # SUGGERIMENTO SQL:
    # SELECT c.ID_Contratto, c.Tipo_Contratto, per.Nome, per.Cognome, c.Data_Scadenza
    # FROM CONTRATTO c JOIN CLIENTE cli ON c.ID_Persona = cli.ID_Persona 
    # JOIN PERSONA per ON cli.ID_Persona = per.ID_Persona 
    # WHERE c.Data_Scadenza BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30' DAY;
    contratti_scadenza = [
        {'id': 'C899', 'tipo': 'Noleggio', 'cliente': 'Azienda SPA', 'scadenza': '20/05/2026'},
        {'id': 'C901', 'tipo': 'Leasing', 'cliente': 'Marco Neri', 'scadenza': '22/05/2026'},
    ]

    # SUGGERIMENTO SQL:
    # SELECT i.ID_Intervento, i.Targa, i.Tipologia_Intervento, p.Nome, p.Cognome, i.Note
    # FROM INTERVENTO i JOIN PRENOTAZIONE pr ON i.ID_Intervento = pr.ID_Intervento
    # JOIN PERSONA p ON pr.ID_Persona = p.ID_Persona WHERE i.Data_Inizio = CURRENT_DATE;
    officina_oggi = [
        {'id': 'INT-10', 'auto': 'AB123CD', 'tipo': 'Tagliando', 'cliente': 'Luigi Gialli', 'stato': 'In lavorazione'},
        {'id': 'INT-11', 'auto': 'EF456GH', 'tipo': 'Riparazione', 'cliente': 'Anna Bruni', 'stato': 'In attesa'},
    ]

    # Passo tutto al template HTML
    return render_template(
        'dashboard.html', 
        kpi=kpi_data, 
        preventivi=preventivi_recenti, 
        contratti=contratti_scadenza, 
        officina=officina_oggi,
        grafico_modelli=grafico_modelli
    )

# ==========================================
# ROTTE PER LE ALTRE PAGINE (Scheletro)
# ==========================================
# Aggiungi queste rotte sotto a quelle che hai già creato in app.py

@app.route('/inventario')
def inventario():
    # SUGGERIMENTO SQL:
    # SELECT NumeroTelaio, Modello, Targa, Prezzo_Base, Stato_Disponibilita, Kilometraggio FROM VEICOLO;
    auto_db = [
        {'telaio': 'ZAR1234567890ABCD', 'modello': 'Giulia', 'targa': 'AB123CD', 'prezzo': 35000, 'stato': 'Disponibile', 'km': 0},
        {'telaio': 'ZFA0987654321WXYZ', 'modello': 'Panda', 'targa': 'EF456GH', 'prezzo': 12000, 'stato': 'In Vendita', 'km': 15000},
        {'telaio': 'ZAR5556667778LMNO', 'modello': 'Stelvio', 'targa': 'IL789MN', 'prezzo': 45000, 'stato': 'Noleggiata', 'km': 5000}
    ]
    return render_template('inventario.html', veicoli=auto_db)

@app.route('/officina')
def officina():
    # SUGGERIMENTO SQL:
    # SELECT i.ID_Intervento, i.Data_Inizio, i.Targa, i.Tipologia_Intervento, p.Nome, p.Cognome 
    # FROM INTERVENTO i JOIN PRENOTAZIONE pr ON i.ID_Intervento = pr.ID_Intervento
    # JOIN PERSONA p ON pr.ID_Persona = p.ID_Persona ORDER BY i.Data_Inizio DESC;
    interventi_db = [
        {'id': 101, 'data': '26/05/2026', 'targa': 'AB123CD', 'tipo': 'Tagliando', 'cliente': 'Mario Rossi', 'stato': 'In Corso'},
        {'id': 102, 'data': '27/05/2026', 'targa': 'EF456GH', 'tipo': 'Riparazione Motore', 'cliente': 'Luigi Bianchi', 'stato': 'Programmato'},
    ]
    return render_template('officina.html', interventi=interventi_db)

@app.route('/contratti')
def contratti():
    # SUGGERIMENTO SQL:
    # SELECT c.ID_Contratto, c.Tipo_Contratto, c.Data_Stipula, c.Importo_Totale, p.Nome, p.Cognome 
    # FROM CONTRATTO c JOIN CLIENTE cli ON c.ID_Persona = cli.ID_Persona 
    # JOIN PERSONA p ON cli.ID_Persona = p.ID_Persona;
    contratti_db = [
        {'id': 'C-1001', 'tipo': 'Finanziamento', 'data': '10/05/2026', 'importo': 25000.00, 'cliente': 'Giulia Verdi'},
        {'id': 'C-1002', 'tipo': 'Noleggio', 'data': '15/05/2026', 'importo': 800.00, 'cliente': 'Azienda Tech SPA'},
    ]
    return render_template('contratti.html', contratti=contratti_db)

@app.route('/clienti')
def clienti():
    # SUGGERIMENTO SQL:
    # SELECT p.ID_Persona, p.Nome, p.Cognome, p.Telefono, p.Mail, p.Residenza 
    # FROM PERSONA p JOIN CLIENTE c ON p.ID_Persona = c.ID_Persona;
    clienti_db = [
        {'id': 1, 'nome': 'Mario Rossi', 'telefono': '333-1234567', 'email': 'mario@email.it', 'citta': 'Milano'},
        {'id': 2, 'nome': 'Luigi Bianchi', 'telefono': '338-9876543', 'email': 'luigi@email.it', 'citta': 'Roma'},
    ]
    return render_template('clienti.html', clienti=clienti_db)

if __name__ == '__main__':
    app.run(debug=True)