from functools import wraps
from flask import Blueprint, render_template, request, redirect, session, flash
from .db import supabase 

main = Blueprint('main', __name__)

# --- DECORATORE PER PROTEZIONE ROTTE ---
def ruolo_richiesto(ruolo_necessario):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Controlla se l'utente è loggato e se il ruolo corrisponde
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
            # QUERY: Ricerca utente usando 'Mail' (maiuscola come nel DB)
            response = supabase.table('PERSONA').select('*').eq('Mail', email).execute()
            utenti = response.data

            if not utenti:
                flash("Account inesistente. Registrati.", "warning")
                return redirect('/login')
                
            utente = utenti[0]
            # Controllo password (usando 'Password' come da DB)
            if utente['Password'] == password:
                session['user_id'] = utente['ID_Persona']
                session['ruolo'] = utente['Ruolo'] 
                session['nome'] = utente['Nome']

                # SMISTAMENTO
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
        # Controllo esistenza
        controllo = supabase.table('PERSONA').select('*').eq('Mail', mail).execute()
        if len(controllo.data) > 0:
            flash("Email già registrata.", "info")
            return redirect('/login')
            
        # Formattazione Residenza (Unione campi per colonna unica varchar(50))
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
            "Ruolo": 1  # 1 = Cliente
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
    if 'user_id' not in session: return redirect('/login')
    # Smistamento centrale
    if session['ruolo'] == 4: return redirect('/dashboard_admin')
    if session['ruolo'] == 1: return redirect('/area_cliente')
    return "Benvenuto!"

@main.route('/dashboard_admin')
@ruolo_richiesto(4) 
def dashboard_admin():
    try:
        # 1. Recupero dati per il Grafico dei Modelli (Query 5.1.16)
        res_modelli = supabase.table('vista_modelli_venduti').select('*').execute()
        dati_modelli = res_modelli.data

        # 2. Recupero dati per il Grafico dei Venditori (Query 5.1.17)
        res_venditori = supabase.table('vista_performance_venditori').select('*').execute()
        dati_venditori = res_venditori.data

        # 3. Creiamo le liste da passare all'HTML
        labels_modelli = [riga['Modello'] for riga in dati_modelli]
        valori_modelli = [riga['totale_vendite'] for riga in dati_modelli]

        labels_venditori = [riga['venditore'] for riga in dati_venditori]
        valori_venditori = [riga['totale_vendite'] for riga in dati_venditori]

    except Exception as e:
        # SE C'È UN ERRORE (es. viste SQL non ancora create),
        # CREIAMO LISTE VUOTE PER NON FAR CRASHARE L'HTML!
        print(f"ERRORE GRAFICI: {str(e)}")
        labels_modelli = []
        valori_modelli = []
        labels_venditori = []
        valori_venditori = []

    # 4. INVIAMO TUTTO ALLA PAGINA HTML (Questa è la riga che mancava o era sbagliata!)
    return render_template('admin/dashboard.html', 
                           labels_modelli=labels_modelli, 
                           valori_modelli=valori_modelli,
                           labels_venditori=labels_venditori,
                           valori_venditori=valori_venditori)

@main.route('/area_cliente')
@ruolo_richiesto(1) 
def area_cliente():
    # Modifica qui in base a dove si trova effettivamente il tuo file
    return render_template('dashboard/dashboard.html')

@main.route('/admin/utenti')
@ruolo_richiesto(4)
def gestione_utenti():
    response = supabase.table('PERSONA').select('*').execute()
    return render_template('admin_utenti.html', utenti=response.data)

@main.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@main.route('/admin/add_crew', methods=['GET', 'POST'])
@ruolo_richiesto(4)  # Solo il Proprietario/Admin può assumere!
def add_crew():
    if request.method == 'POST':
        # 1. Raccogliamo i dati dal form
        ruolo_scelto = int(request.form.get('ruolo')) # Sarà 2, 3 o 5
        mail = request.form.get('mail')
        
        try:
            # 2. Controllo se la mail esiste già
            controllo = supabase.table('PERSONA').select('*').eq('Mail', mail).execute()
            if len(controllo.data) > 0:
                flash("Errore: Email già presente nel sistema.", "danger")
                return redirect('/admin/add_crew')
            
            # 3. Prepariamo i dati per la tabella PERSONA
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
            
            # 4. Inserimento nel Database
            # (Nota: Più avanti aggiungeremo anche l'inserimento automatico nella 
            # tabella LAVORATORE e relative specializzazioni come da tuo ER)
            supabase.table('PERSONA').insert(nuovo_dipendente).execute()
            
            flash(f"Dipendente {nuovo_dipendente['Nome']} aggiunto con successo!", "success")
            return redirect('/dashboard_admin')
            
        except Exception as e:
            print(f"ERRORE ASSUNZIONE: {str(e)}")
            flash("Errore durante l'inserimento nel database.", "danger")
            return redirect('/admin/add_crew')

    # Se è una richiesta GET, mostriamo semplicemente il modulo
    return render_template('admin/add_crew.html')

@main.route('/admin/catalog', methods=['GET', 'POST'])
@ruolo_richiesto(4) 
def gestione_catalogo():
    if request.method == 'POST':
        
        # --- 1. GESTIONE INSERIMENTO MARCA ---
        if 'aggiungi_marca' in request.form: 
            nome_marca = request.form.get('nome_marca')
            try:
                supabase.table('MARCA').insert({"Nome": nome_marca, "Attiva": "Y"}).execute()
                flash(f"Marca {nome_marca} aggiunta!", "success")
            except Exception as e:
                print(f"ERRORE MARCA: {e}")
                flash("Errore durante l'inserimento della marca.", "danger")
            return redirect('/admin/catalog')

        # --- 2. GESTIONE INSERIMENTO VEICOLO ---
        if 'aggiungi_veicolo' in request.form:
            try:
                nuovo_veicolo = {
                    "Targa": request.form.get('targa').upper(),
                    "Modello": request.form.get('modello'),
                    "Prezzo_Base": float(request.form.get('prezzo')),
                    "Stato_Disponibilita": request.form.get('stato'),
                    "ID_Marca": int(request.form.get('id_marca'))
                }
                supabase.table('VEICOLO').insert(nuovo_veicolo).execute()
                flash(f"Veicolo {nuovo_veicolo['Modello']} inserito nel catalogo!", "success")
            except Exception as e:
                print(f"ERRORE VEICOLO: {e}")
                flash("Errore durante il salvataggio del veicolo.", "danger")
            return redirect('/admin/catalog')

    # --- RECUPERO DATI PER LE TABELLE ---
    try:
        lista_marche = supabase.table('MARCA').select('*').execute().data
        lista_veicoli = supabase.table('VEICOLO').select('*').execute().data
    except:
        lista_marche, lista_veicoli = [], []

    return render_template('admin/catalog.html', marche=lista_marche, veicoli=lista_veicoli)
