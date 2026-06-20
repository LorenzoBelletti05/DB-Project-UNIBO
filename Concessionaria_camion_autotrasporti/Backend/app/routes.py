from functools import wraps
from flask import Blueprint, render_template, request, redirect, session, flash
from .db import supabase 

main = Blueprint('main', __name__)

# --- DECORATORE PER PROTEZIONE ROTTE ---
def ruolo_richiesto(ruolo_necessario):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'ruolo' not in session or session['ruolo'] != ruolo_necessario:
                flash("Non hai i permessi necessari per accedere a quest'area.", "danger")
                return redirect('/login')
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- ROTTA LOGIN ---
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            response = supabase.table('PERSONA').select('*').eq('Mail', email).execute()
            utenti = response.data

            if not utenti:
                flash("Account inesistente. Registrati.", "warning")
                return redirect('/login')
                
            utente = utenti[0]
            if utente['Password'] == password:
                session['user_id'] = utente['ID_Persona']
                session['ruolo'] = utente['Ruolo'] 
                session['nome'] = utente['Nome']

                if utente['Ruolo'] == 4:
                    return redirect('/dashboard_admin')
                elif utente['Ruolo'] == 1:
                    return redirect('/area_cliente')
                else:
                    return redirect('/')
            else:
                flash("Password errata.", "danger")
                return redirect('/login')

        except Exception as e:
            print(f"ERRORE LOGIN: {str(e)}")
            flash("Errore di connessione.", "danger")
            return redirect('/login')

    return render_template('login/login.html')

# --- ROTTA REGISTRAZIONE ---
@main.route('/registrazione', methods=['POST'])
def registrazione():
    try:
        mail = request.form.get('mail')
        controllo = supabase.table('PERSONA').select('*').eq('Mail', mail).execute()
        if len(controllo.data) > 0:
            flash("Email già registrata.", "info")
            return redirect('/login')
            
        residenza = f"{request.form.get('via')} {request.form.get('civico')}, {request.form.get('cap')} {request.form.get('citta')} ({request.form.get('provincia')})"
        
        nuovo_utente = {
            "Nome": request.form.get('nome'),
            "Cognome": request.form.get('cognome'),
            "CF": request.form.get('cf'),
            "Numero_Passaporto": request.form.get('passaporto'),
            "Residenza": residenza[:50],
            "Telefono": request.form.get('telefono'),
            "Mail": mail,
            "Password": request.form.get('password'),
            "Ruolo": 1  
        }
        
        supabase.table('PERSONA').insert(nuovo_utente).execute()
        flash("Registrazione completata! Ora puoi accedere.", "success")
        return redirect('/login')
        
    except Exception as e:
        print(f"ERRORE REGISTRAZIONE: {str(e)}")
        flash("Errore nel salvataggio dati.", "danger")
        return redirect('/login')

# --- ROTTE PROTETTE ---
@main.route('/')
def home():
    if 'user_id' not in session: 
        return redirect('/login')
        
    if session['ruolo'] == 4: 
        return redirect('/dashboard_admin')     
    elif session['ruolo'] == 3:                 
        return redirect('/salesperson')         
    elif session['ruolo'] == 1: 
        return redirect('/area_cliente')        
        
    return f"Benvenuto {session.get('nome', '')}! Il tuo ruolo ({session['ruolo']}) non ha ancora una home dedicata."

@main.route('/dashboard_admin')
@ruolo_richiesto(4) 
def dashboard_admin():
    try:
        # --- 1. KPI: Veicoli in Catalogo ---
        # Contiamo tutti i veicoli che NON sono in stato Archiviato ('A')
        res_veicoli = supabase.table('VEICOLO').select('NumeroTelaio').neq('Stato_Disponibilita', 'A').execute()
        veicoli_catalogo = len(res_veicoli.data)
        
        # --- 2. KPI: Interventi Aperti (Officina) ---
        # Contiamo i compiti che non sono ancora completati. (Modifica 'Stato' e 'Completato' se usi nomi diversi)
        res_interventi = supabase.table('COMPITO').select('ID_Compito').neq('Stato', 'Completato').execute()
        interventi_aperti = len(res_interventi.data)
        
        # --- 3. KPI: Valutazioni in Sospeso ---
        # Contiamo le valutazioni usato che aspettano l'approvazione finale (Es. Approvazione_PV è null)
        res_valutazioni = supabase.table('VALUTAZIONE_USATO').select('ID_Usato').is_('Approvazione_PV', 'null').execute()
        valutazioni_sospeso = len(res_valutazioni.data)

        # --- GRAFICI (Statistiche di Vendita) ---
        # Interroghiamo le Viste SQL (Assicurati di averle create in Supabase!)
        res_modelli = supabase.table('vista_modelli_venduti').select('*').execute()
        labels_modelli = [riga['Modello'] for riga in res_modelli.data]
        valori_modelli = [riga['totale_vendite'] for riga in res_modelli.data]

        res_venditori = supabase.table('vista_performance_venditori').select('*').execute()
        labels_venditori = [riga['venditore'] for riga in res_venditori.data]
        valori_venditori = [riga['totale_vendite'] for riga in res_venditori.data]

    except Exception as e:
        print(f"ERRORE DASHBOARD ADMIN: {str(e)}")
        # In caso di errore (es. tabelle vuote o viste mancanti), mettiamo tutto a zero
        veicoli_catalogo, interventi_aperti, valutazioni_sospeso = 0, 0, 0
        labels_modelli, valori_modelli, labels_venditori, valori_venditori = [], [], [], []

    return render_template('admin/dashboard.html', 
                           veicoli_catalogo=veicoli_catalogo,
                           interventi_aperti=interventi_aperti,
                           valutazioni_sospeso=valutazioni_sospeso,
                           labels_modelli=labels_modelli, 
                           valori_modelli=valori_modelli,
                           labels_venditori=labels_venditori,
                           valori_venditori=valori_venditori)

@main.route('/area_cliente')
@ruolo_richiesto(1) 
def area_cliente():
    return render_template('dashboard/dashboard.html')

@main.route('/admin/utenti')
@ruolo_richiesto(4)
def gestione_utenti():
    response = supabase.table('PERSONA').select('*').execute()
    return render_template('admin/admin_user.html', utenti=response.data)

@main.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@main.route('/admin/add_crew', methods=['GET', 'POST'])
@ruolo_richiesto(4)  
def add_crew():
    if request.method == 'POST':
        ruolo_scelto = int(request.form.get('ruolo')) 
        mail = request.form.get('mail')
        
        try:
            controllo = supabase.table('PERSONA').select('*').eq('Mail', mail).execute()
            if len(controllo.data) > 0:
                flash("Errore: Email già presente nel sistema.", "danger")
                return redirect('/admin/add_crew')
            
            nuovo_dipendente = {
                "Nome": request.form.get('nome'),
                "Cognome": request.form.get('cognome'),
                "CF": request.form.get('cf'),
                "Residenza": request.form.get('residenza')[:50],
                "Telefono": request.form.get('telefono'),
                "Mail": mail,
                "Password": request.form.get('password'),
                "Ruolo": ruolo_scelto 
            }
            
            supabase.table('PERSONA').insert(nuovo_dipendente).execute()
            flash(f"Dipendente {nuovo_dipendente['Nome']} aggiunto con successo!", "success")
            return redirect('/dashboard_admin')
            
        except Exception as e:
            print(f"ERRORE ASSUNZIONE: {str(e)}")
            flash("Errore durante l'inserimento nel database.", "danger")
            return redirect('/admin/add_crew')

    return render_template('admin/add_crew.html')

@main.route('/admin/catalog', methods=['GET', 'POST'])
@ruolo_richiesto(4) 
def gestione_catalogo():
    if request.method == 'POST':
        
        if 'aggiungi_marca' in request.form: 
            nome_marca = request.form.get('nome_marca')
            try:
                supabase.table('MARCA').insert({"Nome": nome_marca, "Attiva": "Y"}).execute()
                flash(f"Marca {nome_marca} aggiunta!", "success")
            except Exception as e:
                print(f"ERRORE MARCA: {e}")
                flash("Errore durante l'inserimento della marca.", "danger")
            return redirect('/admin/catalog')

        if 'aggiungi_veicolo' in request.form:
            try:
                nuovo_veicolo = {
                    "Targa": request.form.get('targa').upper(),
                    "Modello": request.form.get('modello'),
                    "Anno_Produzione": int(request.form.get('anno')),
                    "Data_Arrivo_Concessionaria": request.form.get('data_arrivo'),
                    "Classe_Inquinamento": request.form.get('classe_inquinamento'),
                    "Prezzo_Base": float(request.form.get('prezzo')),
                    "Stato_Disponibilita": request.form.get('stato'),
                    "ID_Marca": int(request.form.get('id_marca')),
                    "Kilometraggio": int(request.form.get('chilometraggio')),
                    "Potenza_CV": int(request.form.get('potenza_cv')),
                    "Peso": float(request.form.get('peso')),
                    "Data_Immatricolazione": request.form.get('data_immatricolazione'),
                    "Descrizione": request.form.get('descrizione'),
                    "Configurazione_Assi": request.form.get('configurazione_assi'),
                    "Numero_Assi": int(request.form.get('numero_assi')),
                    "NumeroTelaio": request.form.get('numero_telaio').upper(),
                    "Tipologia_Motrice": request.form.get('tipologia_motrice')
                }
                supabase.table('VEICOLO').insert(nuovo_veicolo).execute()
                flash(f"Veicolo {nuovo_veicolo['Modello']} inserito nel catalogo!", "success")
            except Exception as e:
                print(f"ERRORE VEICOLO: {e}")
                flash("Errore durante il salvataggio del veicolo.", "danger")
            return redirect('/admin/catalog')

    try:
        lista_marche = supabase.table('MARCA').select('*').execute().data
        tutti_veicoli = supabase.table('VEICOLO').select('*').execute().data
        
        # Dividiamo i veicoli tramite Python
        lista_veicoli = [v for v in tutti_veicoli if v['Stato_Disponibilita'] != 'A']
        veicoli_archiviati = [v for v in tutti_veicoli if v['Stato_Disponibilita'] == 'A']
        
    except:
        lista_marche, lista_veicoli, veicoli_archiviati = [], [], []

    return render_template('admin/catalog.html', 
                           marche=lista_marche, 
                           veicoli=lista_veicoli,
                           veicoli_archiviati=veicoli_archiviati)

@main.route('/catalog', methods=['GET'])
def public_catalog():
    try:
        res_veicoli = supabase.table('VEICOLO').select('*').execute()
        vehicles = res_veicoli.data

        res_marche = supabase.table('MARCA').select('*').eq('Attiva', 'Y').execute()
        brands = res_marche.data
        
        mappa_marche = {marca['ID_Marca']: marca['Nome'] for marca in brands}

    except Exception as e:
        print(f"ERRORE CATALOGO PUBBLICO: {e}")
        vehicles, brands, mappa_marche = [], [], {}

    return render_template('public_catalog.html', vehicles=vehicles, brands=brands, mappa_marche=mappa_marche)

@main.route('/salesperson', methods=['GET'])
@ruolo_richiesto(3)  
def salesperson_dashboard():
    try:
        res_veicoli = supabase.table('VEICOLO').select('*').execute()
        veicoli_disponibili = len(res_veicoli.data)
        quotes, test_drives = [], []

    except Exception as e:
        print(f"ERRORE DASHBOARD VENDITORE: {e}")
        veicoli_disponibili, quotes, test_drives = 0, [], []

    return render_template('salesperson_dashboard.html', 
                           quotes=quotes, 
                           test_drives=test_drives, 
                           stock_count=veicoli_disponibili)

@main.route('/transaction_wizard', methods=['GET'])
@ruolo_richiesto(3) 
def transaction_wizard():
    if request.method == 'POST':
        flash("Transazione/Preventivo generato con successo!", "success")
        return redirect('/salesperson')

    try:
        clienti = supabase.table('PERSONA').select('*').eq('Ruolo', 1).execute().data
        veicoli = supabase.table('VEICOLO').select('*').execute().data
        res_marche = supabase.table('MARCA').select('*').execute()
        mappa_marche = {marca['ID_Marca']: marca['Nome'] for marca in res_marche.data}
    except Exception as e:
        print(f"ERRORE WIZARD: {e}")
        clienti, veicoli, mappa_marche = [], [], {}

    return render_template('sales/transaction_wizard.html', 
                           clienti=clienti, 
                           veicoli=veicoli, 
                           mappa_marche=mappa_marche)

@main.route('/test_drive_calendar', methods=['GET'])
def test_drive_calendar():
    return render_template('test_drive_calendar.html')

# --- ROTTA CORRETTA: CAMBIATO <int:id_veicolo> in <string:telaio> ---
@main.route('/admin/toggle_veicolo/<string:telaio>', methods=['POST'])
@ruolo_richiesto(4) 
def toggle_veicolo(telaio):
    try:
        res = supabase.table('VEICOLO').select('Stato_Disponibilita').eq('NumeroTelaio', telaio).single().execute()
        attuale = res.data['Stato_Disponibilita']
        
        # Se era disponibile o usato, lo archivio ('A'). Se era archiviato, lo faccio tornare Usato ('U')
        nuovo_stato = 'A' if attuale != 'A' else 'U'
        
        supabase.table('VEICOLO').update({'Stato_Disponibilita': nuovo_stato}).eq('NumeroTelaio', telaio).execute()
        
        flash(f"Veicolo con Telaio {telaio} spostato con successo!", "success")
    except Exception as e:
        print(f"ERRORE ARCHIVIAZIONE: {e}")
        flash("Errore durante lo spostamento del veicolo.", "danger")
        
    return redirect('/admin/catalog')

@main.route('/admin/toggle_marca/<int:id_marca>', methods=['POST'])
@ruolo_richiesto(4) 
def toggle_marca(id_marca):
    try:
        res_marca = supabase.table('MARCA').select('Attiva').eq('ID_Marca', id_marca).single().execute()
        stato_attuale_marca = res_marca.data['Attiva']
        
        nuovo_stato_marca = 'N' if stato_attuale_marca == 'Y' else 'Y'
        # Se disattivo la marca, i veicoli diventano 'A'. Se la riattivo, tornano 'N' (Nuovi)
        nuovo_stato_veicoli = 'A' if nuovo_stato_marca == 'N' else 'N'
        
        supabase.table('MARCA').update({'Attiva': nuovo_stato_marca}).eq('ID_Marca', id_marca).execute()
        supabase.table('VEICOLO').update({'Stato_Disponibilita': nuovo_stato_veicoli}).eq('ID_Marca', id_marca).execute()
        
        azione = "disattivata" if nuovo_stato_marca == 'N' else "riattivata"
        flash(f"Marca {azione} con successo. Tutti i relativi veicoli sono stati aggiornati.", "success")
        
    except Exception as e:
        print(f"ERRORE TOGGLE MARCA: {e}")
        flash("Errore durante l'aggiornamento della marca.", "danger")
        
    return redirect('/admin/catalog')