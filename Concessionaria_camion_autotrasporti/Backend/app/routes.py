from functools import wraps
from flask import Blueprint, render_template, request, redirect, session, flash, jsonify
from .db import supabase 

main = Blueprint('main', __name__)

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
        res_modelli = supabase.table('vista_modelli_venduti').select('*').execute()
        dati_modelli = res_modelli.data

        res_venditori = supabase.table('vista_performance_venditori').select('*').execute()
        dati_venditori = res_venditori.data

        labels_modelli = [riga['Modello'] for riga in dati_modelli]
        valori_modelli = [riga['totale_vendite'] for riga in dati_modelli]

        labels_venditori = [riga['venditore'] for riga in dati_venditori]
        valori_venditori = [riga['totale_vendite'] for riga in dati_venditori]

    except Exception as e:
        print(f"ERRORE GRAFICI: {str(e)}")
        labels_modelli = []
        valori_modelli = []
        labels_venditori = []
        valori_venditori = []

    return render_template('admin/dashboard.html', 
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
                numero_telaio = request.form.get('numero_telaio', '').upper()[:17]
                stato_veicolo = request.form.get('stato', 'N')[:1].upper() 

                km_form = request.form.get('chilometraggio')
                km = int(km_form) if km_form and km_form.strip() else 0
                if stato_veicolo == 'N':
                    km = 0  

                num_assi_form = request.form.get('numero_assi')
                num_assi = int(num_assi_form) if num_assi_form and num_assi_form.strip() else 2
                
                conf_assi_form = request.form.get('configurazione_assi')
                conf_assi = conf_assi_form[:3] if conf_assi_form and conf_assi_form.strip() else '4x2'

                descrizione = request.form.get('descrizione')
                desc_pulita = descrizione[:100] if descrizione else "N/A"

                nuovo_veicolo = {
                    "NumeroTelaio": numero_telaio,
                    "Targa": request.form.get('targa', '')[:20].upper(),
                    "Modello": request.form.get('modello', 'Sconosciuto')[:15],
                    "Anno_Produzione": int(request.form.get('anno') or 2024),
                    "Data_Arrivo_Concessionaria": request.form.get('data_arrivo'),
                    "Classe_Inquinamento": request.form.get('classe_inquinamento', 'Euro 6')[:6],
                    "Configurazione_Assi": conf_assi,
                    "Numero_Assi": num_assi,
                    "Tipologia_Motrice": request.form.get('tipologia_motrice', 'Motrice')[:15],
                    "Peso": float(request.form.get('peso') or 0.0),
                    "Descrizione": desc_pulita,
                    "Prezzo_Base": float(request.form.get('prezzo') or 0.0),
                    "Data_Immatricolazione": request.form.get('data_immatricolazione') or None,
                    "Potenza_CV": int(request.form.get('potenza_cv') or 0),
                    "Stato_Disponibilita": stato_veicolo,
                    "ID_Marca": int(request.form.get('id_marca') or 1),
                    "Kilometraggio": km
                }
                
                supabase.table('VEICOLO').insert(nuovo_veicolo).execute()

                flash(f"Veicolo {nuovo_veicolo['Modello']} inserito correttamente nel catalogo!", "success")
            
            except Exception as e:
                print(f"ERRORE VEICOLO: {e}")
                flash("Errore durante il salvataggio del veicolo. Controlla i dati inseriti.", "danger")
            return redirect('/admin/catalog')

    try:
        lista_marche = supabase.table('MARCA').select('*').execute().data
        lista_veicoli = supabase.table('VEICOLO').select('*').execute().data
    except:
        lista_marche, lista_veicoli = [], []

    return render_template('admin/catalog.html', marche=lista_marche, veicoli=lista_veicoli)

@main.route('/catalog', methods=['GET'])
def public_catalog():
    try:
        condizione = request.args.get('condition')
        marca_nome = request.args.get('brand')
        modello = request.args.get('model')
        prezzo_max = request.args.get('max_price')

        query = supabase.table('VEICOLO').select('*')

        if condizione == 'New':
            query = query.eq('Stato_Disponibilita', 'N')
        elif condizione == 'Used':
            query = query.eq('Stato_Disponibilita', 'U')

        if modello:
            query = query.ilike('Modello', f'%{modello}%')

        if prezzo_max:
            query = query.lte('Prezzo_Base', float(prezzo_max))

        res_veicoli = query.execute()
        vehicles = res_veicoli.data

        res_marche = supabase.table('MARCA').select('*').eq('Attiva', 'Y').execute()
        brands = res_marche.data
        mappa_marche = {marca['ID_Marca']: marca['Nome'] for marca in brands}

        if marca_nome:
            id_marca_cercata = next((id_m for id_m, nome in mappa_marche.items() if nome == marca_nome), None)
            if id_marca_cercata:
                vehicles = [v for v in vehicles if v['ID_Marca'] == id_marca_cercata]
            else:
                vehicles = [] 

    except Exception as e:
        print(f"ERRORE CATALOGO PUBBLICO: {e}")
        vehicles = []
        brands = []
        mappa_marche = {}

    return render_template('public_catalog.html', vehicles=vehicles, brands=brands, mappa_marche=mappa_marche)

@main.route('/api/optional/<numero_telaio>', methods=['GET'])
def get_optionals(numero_telaio):
    try:
        res_comp = supabase.table('Comprende_VO').select('ID_Optional').eq('NumeroTelaio', numero_telaio).execute()
        id_optionals = [riga['ID_Optional'] for riga in res_comp.data]

        if not id_optionals:
            return jsonify([])
        
        res_opt = supabase.table('OPTIONAL').select('*').in_('ID_Optional', id_optionals).execute()
        
        lista_optional = []
        for opt in res_opt.data:
            lista_optional.append({
                "id": opt.get("ID_Optional", opt.get("id", 0)),
                "nome": opt.get("Nome", opt.get("nome", "Optional")),
                "prezzo": opt.get("Prezzo", opt.get("prezzo", 0))
            })
            
        return jsonify(lista_optional)
    except Exception as e:
        print(f"ERRORE API OPTIONAL: {e}")
        return jsonify([])

@main.route('/salesperson', methods=['GET'])
@ruolo_richiesto(3) 
def salesperson_dashboard():
    try:
        res_veicoli = supabase.table('VEICOLO').select('*').execute()
        veicoli_disponibili = len(res_veicoli.data)
        
        quotes = [] 
        test_drives = []

    except Exception as e:
        print(f"ERRORE DASHBOARD VENDITORE: {e}")
        veicoli_disponibili = 0
        quotes = []
        test_drives = []

    return render_template('salesperson_dashboard.html', 
                           quotes=quotes, 
                           test_drives=test_drives, 
                           stock_count=veicoli_disponibili)

@main.route('/transaction_wizard', methods=['GET', 'POST'])
@ruolo_richiesto(3) 
def transaction_wizard():
    if request.method == 'POST':
        flash("Transazione/Preventivo generato con successo!", "success")
        return redirect('/salesperson')

    try:
        res_clienti = supabase.table('PERSONA').select('*').eq('Ruolo', 1).execute()
        clienti = res_clienti.data

        res_veicoli = supabase.table('VEICOLO').select('*').execute()
        veicoli = res_veicoli.data

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