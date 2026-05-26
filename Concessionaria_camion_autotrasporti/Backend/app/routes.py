# Backend/app/routes.py
from flask import render_template, jsonify
from app import app
from app.db import get_db_connection  # Già pronto per quando collegherete SQL!

@app.route('/')
def dashboard():
    # ==========================================
    # 1. KPI (Key Performance Indicators)
    # ==========================================
    # SUGGERIMENTO SQL PER IL BACKEND:
    # conn = get_db_connection()
    # cursor = conn.cursor()
    # cursor.execute("SELECT COUNT(*) FROM VEICOLO WHERE Stato_Disponibilita = 'D';")
    # ...
    kpi_data = {
        'auto_disponibili': 115,
        'vendite_mese': 42,
        'clienti_registrati': 890,
        'interventi_oggi': 18
    }

    # ==========================================
    # 2. DATI GRAFICI
    # ==========================================
    grafico_modelli = {
        'labels': ['Panda', 'Giulietta', 'Giulia', '500', 'Stelvio'],
        'data': [90, 75, 55, 45, 30]
    }

    # ==========================================
    # 3. TABELLE DATI RECENTI (Mock Data)
    # ==========================================
    preventivi_recenti = [
        {'id': 'P001', 'cliente': 'Mario Rossi', 'auto': 'Panda', 'data': '15/05/2026', 'stato': 'Aperto'},
        {'id': 'P002', 'cliente': 'Luca Bianchi', 'auto': 'Giulia', 'data': '14/05/2026', 'stato': 'Chiuso'},
        {'id': 'P003', 'cliente': 'Giulia Verdi', 'auto': 'Giulietta', 'data': '14/05/2026', 'stato': 'Aperto'},
    ]

    contratti_scadenza = [
        {'id': 'C899', 'tipo': 'Noleggio', 'cliente': 'Azienda SPA', 'scadenza': '20/05/2026'},
        {'id': 'C901', 'tipo': 'Leasing', 'cliente': 'Marco Neri', 'scadenza': '22/05/2026'},
    ]

    officina_oggi = [
        {'id': 'INT-10', 'auto': 'AB123CD', 'tipo': 'Tagliando', 'cliente': 'Luigi Gialli', 'stato': 'In lavorazione'},
        {'id': 'INT-11', 'auto': 'EF456GH', 'tipo': 'Riparazione', 'cliente': 'Anna Bruni', 'stato': 'In attesa'},
    ]

    return render_template(
        'dashboard.html', 
        kpi=kpi_data, 
        preventivi=preventivi_recenti, 
        contratti=contratti_scadenza, 
        officina=officina_oggi,
        grafico_modelli=grafico_modelli
    )

# ==========================================
# ROTTE PER LE ALTRE PAGINE
# ==========================================

@app.route('/inventario')
def inventario():
    auto_db = [
        {'telaio': 'ZAR1234567890ABCD', 'modello': 'Giulia', 'targa': 'AB123CD', 'prezzo': 35000, 'stato': 'Disponibile', 'km': 0},
        {'telaio': 'ZFA0987654321WXYZ', 'modello': 'Panda', 'targa': 'EF456GH', 'prezzo': 12000, 'stato': 'In Vendita', 'km': 15000}
    ]
    return render_template('inventario.html', veicoli=auto_db)

@app.route('/officina')
def officina():
    interventi_db = [
        {'id': 101, 'data': '26/05/2026', 'targa': 'AB123CD', 'tipo': 'Tagliando', 'cliente': 'Mario Rossi', 'stato': 'In Corso'}
    ]
    return render_template('officina.html', interventi=interventi_db)

@app.route('/contratti')
def contratti():
    contratti_db = [
        {'id': 'C-1001', 'tipo': 'Finanziamento', 'data': '10/05/2026', 'importo': 25000.00, 'cliente': 'Giulia Verdi'}
    ]
    return render_template('contratti.html', contratti=contratti_db)

@app.route('/clienti')
def clienti():
    clienti_db = [
        {'id': 1, 'nome': 'Mario Rossi', 'telefono': '333-1234567', 'email': 'mario@email.it', 'citta': 'Milano'}
    ]
    return render_template('clienti.html', clienti=clienti_db)