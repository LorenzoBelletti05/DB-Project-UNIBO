from functools import wraps
from flask import Blueprint, render_template, request, redirect, session, flash, jsonify
from .db import supabase 
from datetime import date, datetime

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

                # SMISTAMENTO AUTOMATICO DOPO IL LOGIN (COMPLETO)
                if utente['Ruolo'] == 4:
                    return redirect('/dashboard_admin')
                elif utente['Ruolo'] == 3:
                    return redirect('/salespearson')
                elif utente['Ruolo'] == 2:
                    return redirect('/dashboard_meccanico')    
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

        risposta = supabase.table('PERSONA').insert(nuovo_utente).execute()
        
        id_generato = risposta.data[0]['ID_Persona']
        supabase.table('CLIENTE').insert({"ID_Persona": id_generato}).execute()

        flash("Registrazione completata! Ora puoi accedere.", "success")
        return redirect('/login')

    except Exception as e:
        print(f"ERRORE REGISTRAZIONE: {str(e)}")
        flash("Errore nel salvataggio dati.", "danger")
        return redirect('/login')

# --- HOME / SMISTAMENTO CENTRALE UNIFICATO ---
@main.route('/')
def home():
    if 'user_id' not in session: 
        return redirect('/login')
        
    if session['ruolo'] == 4: 
        return redirect('/dashboard_admin')     
    elif session['ruolo'] == 3:                
        return redirect('/salespearson')         
    elif session['ruolo'] == 2:
        return redirect('/dashboard_meccanico')
    elif session['ruolo'] == 1: 
        return redirect('/area_cliente')        
        
    return f"Benvenuto {session.get('nome', '')}! Il tuo ruolo ({session['ruolo']}) non ha ancora una home dedicata."

# --- ROTTA DASHBOARD AMMINISTRATORE ---
@main.route('/dashboard_admin')
@ruolo_richiesto(4) 
def dashboard_admin():
    try:
        # ==========================================
        # SEZIONE 1: KPI (Contatori)
        # ==========================================
        tutti_veicoli = supabase.table('VEICOLO').select('*').execute().data
        veicoli_catalogo = len([v for v in tutti_veicoli if v.get('Stato_Disponibilita') != 'A'])
        
        res_compiti = supabase.table('COMPITO').select('Stato').execute().data
        interventi_aperti = len([c for c in res_compiti if c.get('Stato') != 'Concluso'])
        
        res_val = supabase.table('VALUTAZIONE_USATO').select('ID_Usato').execute().data
        res_app = supabase.table('Approvazione_PV').select('ID_Usato').execute().data
        id_approvati = [a['ID_Usato'] for a in res_app]
        valutazioni_sospeso = len([v for v in res_val if v['ID_Usato'] not in id_approvati])

        # Prepariamo le mappe base per non fare query continue
        persone = supabase.table('PERSONA').select('ID_Persona, Nome, Cognome').execute().data
        mappa_persone = {p['ID_Persona']: f"{p['Nome']} {p['Cognome']}" for p in persone}
        
        mappa_telaio_modello = {v['NumeroTelaio']: v.get('Modello', 'Ignoto') for v in tutti_veicoli}

        # ==========================================
        # REQUISITO 5.1.17: VENDITORI (Performance)
        # ==========================================
        vendite = supabase.table('VENDITA').select('ID_Persona, ID_Contratto').execute().data
        conteggio_venditori = {}
        for vendita in vendite:
            id_venditore = vendita.get('ID_Persona')
            if id_venditore:
                nome = mappa_persone.get(id_venditore, f"ID {id_venditore}")
                conteggio_venditori[nome] = conteggio_venditori.get(nome, 0) + 1
                
        ord_venditori = sorted(conteggio_venditori.items(), key=lambda x: x[1], reverse=True)
        labels_venditori = [v[0] for v in ord_venditori]
        valori_venditori = [v[1] for v in ord_venditori]

        # ==========================================
        # REQUISITO 5.1.16: MODELLI PIU VENDUTI
        # ==========================================
        contratti_venduti_ids = [v['ID_Contratto'] for v in vendite if v.get('ID_Contratto') is not None]
        conteggio_modelli = {}
        for veicolo in tutti_veicoli:
            if veicolo.get('ID_Contratto') in contratti_venduti_ids:
                mod = veicolo.get('Modello', 'Ignoto')
                conteggio_modelli[mod] = conteggio_modelli.get(mod, 0) + 1
                
        ord_modelli = sorted(conteggio_modelli.items(), key=lambda x: x[1], reverse=True)
        labels_modelli = [m[0] for m in ord_modelli]
        valori_modelli = [m[1] for m in ord_modelli]

        # ==========================================
        # REQUISITO 5.1.18: MECCANICI PIU ATTIVI
        # ==========================================
        # Risaliamo da COMPITO a PERSONA per vedere il carico di lavoro
        tutti_i_compiti = supabase.table('COMPITO').select('ID_Persona').execute().data
        conteggio_meccanici = {}
        for compito in tutti_i_compiti:
            id_mecc = compito.get('ID_Persona')
            if id_mecc:
                nome_mecc = mappa_persone.get(id_mecc, f"ID {id_mecc}")
                conteggio_meccanici[nome_mecc] = conteggio_meccanici.get(nome_mecc, 0) + 1
        
        ord_meccanici = sorted(conteggio_meccanici.items(), key=lambda x: x[1], reverse=True)
        labels_meccanici = [m[0] for m in ord_meccanici]
        valori_meccanici = [m[1] for m in ord_meccanici]

        # ==========================================
        # REQUISITO 5.1.19: MODELLI CON ALTO RIFIUTO
        # ==========================================
        # Risaliamo dall'esito negativo al modello del veicolo usato
        esiti = supabase.table('Esito_MV').select('ID_Usato, Esito_Meccanico').execute().data
        valutazioni = supabase.table('VALUTAZIONE_USATO').select('ID_Usato, NumeroTelaio').execute().data
        mappa_usato_telaio = {v['ID_Usato']: v['NumeroTelaio'] for v in valutazioni}

        rifiuti_modelli = {}
        for esito in esiti:
            # Assumiamo che 'N' (Negativo) o 'R' (Rifiutato) sia il carattere di scarto
            if esito.get('Esito_Meccanico') in ['N', 'R']:
                telaio = mappa_usato_telaio.get(esito.get('ID_Usato'))
                if telaio:
                    mod = mappa_telaio_modello.get(telaio, 'Ignoto')
                    rifiuti_modelli[mod] = rifiuti_modelli.get(mod, 0) + 1
        
        ord_rifiuti = sorted(rifiuti_modelli.items(), key=lambda x: x[1], reverse=True)
        labels_rifiuti = [r[0] for r in ord_rifiuti]
        valori_rifiuti = [r[1] for r in ord_rifiuti]

    except Exception as e:
        print(f"\n❌ ERRORE DASHBOARD ADMIN: {str(e)}\n")
        veicoli_catalogo, interventi_aperti, valutazioni_sospeso = 0, 0, 0
        labels_modelli, valori_modelli, labels_venditori, valori_venditori = [], [], [], []
        labels_meccanici, valori_meccanici, labels_rifiuti, valori_rifiuti = [], [], [], []

    return render_template('admin/admin_dashboard.html', 
                           veicoli_catalogo=veicoli_catalogo,
                           interventi_aperti=interventi_aperti,
                           valutazioni_sospeso=valutazioni_sospeso,
                           labels_modelli=labels_modelli, valori_modelli=valori_modelli,
                           labels_venditori=labels_venditori, valori_venditori=valori_venditori,
                           labels_meccanici=labels_meccanici, valori_meccanici=valori_meccanici,
                           labels_rifiuti=labels_rifiuti, valori_rifiuti=valori_rifiuti)

# --- ROTTA AREA CLIENTE ---
@main.route('/area_cliente')
@ruolo_richiesto(1) 
def area_cliente():
    return render_template('dashboard/dashboard.html')

# --- AMMINISTRAZIONE: UTENTI ---
@main.route('/admin/utenti')
@ruolo_richiesto(4)
def gestione_utenti():
    response = supabase.table('PERSONA').select('*').execute()
    return render_template('admin/admin_user.html', utenti=response.data)

# --- LOGOUT ---
@main.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# --- AMMINISTRAZIONE: ASSUMI DIPENDENTE ---
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

# --- AMMINISTRAZIONE: CATALOGO (MERGED) ---
@main.route('/admin/catalog', methods=['GET', 'POST'])
@ruolo_richiesto(4) 
def gestione_catalogo():
    if request.method == 'POST':
        # Sotto-Azione A: Aggiungi Marca (Tua Funzione)
        if 'aggiungi_marca' in request.form: 
            nome_marca = request.form.get('nome_marca')
            try:
                supabase.table('MARCA').insert({"Nome": nome_marca, "Attiva": "Y"}).execute()
                flash(f"Marca {nome_marca} aggiunta con successo!", "success")
            except Exception as e:
                print(f"ERRORE MARCA: {e}")
                flash("Errore durante l'inserimento della marca.", "danger")
            return redirect('/admin/catalog')

        # Sotto-Azione B: Aggiungi Veicolo (Funzione del Team)
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

                # Replica della query 5.1.2.1 / 5.1.2.2: collegamento optional
                optional_selezionati = request.form.getlist('optional_ids')
                for id_opt in optional_selezionati:
                    supabase.table('Comprende_VO').insert({
                        "NumeroTelaio": numero_telaio,
                        "ID_Optional": int(id_opt)
                    }).execute()

                flash(f"Veicolo {nuovo_veicolo['Modello']} inserito correttamente nel catalogo!", "success")
            
            except Exception as e:
                print(f"ERRORE VEICOLO: {e}")
                flash("Errore durante il salvataggio del veicolo. Controlla i dati inseriti.", "danger")
            
            return redirect('/admin/catalog')

    try:
        lista_marche = supabase.table('MARCA').select('*').execute().data
        tutti_veicoli = supabase.table('VEICOLO').select('*').execute().data
        lista_veicoli = [v for v in tutti_veicoli if v['Stato_Disponibilita'] != 'A']
        veicoli_archiviati = [v for v in tutti_veicoli if v['Stato_Disponibilita'] == 'A']
        lista_optional_db = supabase.table('OPTIONAL').select('*').execute().data
        
    except:
        lista_marche, lista_veicoli, veicoli_archiviati, lista_optional_db = [], [], [], []

    return render_template('admin/catalog.html',
                           marche=lista_marche,
                           veicoli=lista_veicoli,
                           veicoli_archiviati=veicoli_archiviati,
                           lista_optional_db=lista_optional_db)

# --- ROTTA DASHBOARD MECCANICO (KANBAN BOARD) ---
@main.route('/dashboard_meccanico')
@ruolo_richiesto(2)
def dashboard_meccanico():
    try:
        id_meccanico = session.get('user_id')
        
        # 1. Carichiamo i compiti per le 3 colonne della Kanban
        response = supabase.table('COMPITO').select(
            '*, INTERVENTO(Data_Inizio, Targa, OFFICINA(Nome, Interna))'
        ).eq('ID_Persona', id_meccanico).execute()

        tutti_i_compiti = response.data
        da_fare = [c for c in tutti_i_compiti if c.get('Stato', 'Da fare') == 'Da fare']
        in_corso = [c for c in tutti_i_compiti if c.get('Stato') == 'In corso']
        finiti = [c for c in tutti_i_compiti if c.get('Stato') == 'Finito']

        # Andiamo a cercare il numero di interventi totali salvato nella tabella MECCANICO
        res_mecc = supabase.table('MECCANICO').select('Totale_interventi').eq('ID_Persona', id_meccanico).execute()
        
        # Estraiamo il numero, se non trova nulla (o è un meccanico appena assunto) di default è 0
        if res_mecc.data:
            totale_storico = res_mecc.data[0]['Totale_interventi']
        else:
            totale_storico = 0

        # 3. Inviamo tutto all'HTML (incluso il totale_storico)
        return render_template('meccanico/dashboard_meccanico.html', 
                               da_fare=da_fare, 
                               in_corso=in_corso, 
                               finiti=finiti, 
                               totale_storico=totale_storico)
                               
    except Exception as e:
        print(f"ERRORE KANBAN MECCANICO: {str(e)}")
        flash("Errore nel caricamento della tua bacheca.", "danger")
        return redirect('/')

# --- ROTTA PER PULIRE LA COLONNA "FINITI" E AGGIORNARE LE PERFORMANCE ---
@main.route('/pulisci_completati', methods=['POST'])
@ruolo_richiesto(2)
def pulisci_completati():
    try:
        id_meccanico = session.get('user_id')
        
        # 1. Contiamo quanti compiti sono in stato "Finito" prima di archiviarli
        res_finiti = supabase.table('COMPITO').select('ID_Compito').eq('ID_Persona', id_meccanico).eq('Stato', 'Finito').execute()
        numero_da_archiviare = len(res_finiti.data)
        
        if numero_da_archiviare > 0:
            # 2. Li spostiamo in "Archiviato"
            supabase.table('COMPITO').update({'Stato': 'Archiviato'}).eq('ID_Persona', id_meccanico).eq('Stato', 'Finito').execute()
            
            # 3. Aggiorniamo il contatore nella tabella MECCANICO
            res_mecc = supabase.table('MECCANICO').select('Totale_interventi').eq('ID_Persona', id_meccanico).execute()
            if res_mecc.data:
                attuale = res_mecc.data[0]['Totale_interventi']
                nuovo_totale = attuale + numero_da_archiviare
                supabase.table('MECCANICO').update({'Totale_interventi': nuovo_totale}).eq('ID_Persona', id_meccanico).execute()
                
            flash(f"Bacheca pulita! Hai registrato {numero_da_archiviare} nuovi interventi nel tuo storico.", "success")
        else:
            flash("Non ci sono compiti completati da pulire.", "info")
            
    except Exception as e:
        print(f"ERRORE PULIZIA COMPITI: {str(e)}")
        flash("Errore durante l'archiviazione dei compiti.", "danger")
        
    return redirect('/dashboard_meccanico')

# --- ROTTA PER AGGIORNARE LO STATO DEL COMPITO ---
@main.route('/aggiorna_compito/<int:id_compito>', methods=['POST'])
@ruolo_richiesto(2)
def aggiorna_compito(id_compito):
    nuovo_stato = request.form.get('nuovo_stato')
    try:
        supabase.table('COMPITO').update({'Stato': nuovo_stato}).eq('ID_Compito', id_compito).execute()
        flash("Stato del compito aggiornato con successo!", "success")
    except Exception as e:
        print(f"ERRORE AGGIORNAMENTO STATO: {str(e)}")
        flash("Si è verificato un errore durante l'aggiornamento.", "danger")
    return redirect('/dashboard_meccanico')

# --- WIZARD USATO FASE 1: PROPOSTA CLIENTE (LATO CLIENTE) ---
@main.route('/proponi_usato', methods=['GET', 'POST'])
@ruolo_richiesto(1)
def proponi_usato():
    if request.method == 'POST':
        try:
            tipo_inserimento = request.form.get('tipo_inserimento')
            
            if tipo_inserimento == 'nuovo':
                telaio = request.form.get('numero_telaio').upper()
                targa = request.form.get('targa').upper()
                nome_marca = request.form.get('marca').strip().capitalize()
                
                res_marca = supabase.table('MARCA').select('ID_Marca').eq('Nome', nome_marca).execute()
                if res_marca.data:
                    id_marca = res_marca.data[0]['ID_Marca']
                else:
                    res_nuova = supabase.table('MARCA').insert({"Nome": nome_marca, "Attiva": "Y"}).execute()
                    id_marca = res_nuova.data[0]['ID_Marca']

                # Salviamo il veicolo nuovo
                nuovo_veicolo = {
                    "NumeroTelaio": telaio,
                    "Targa": targa,
                    "Modello": request.form.get('modello')[:15],
                    "Anno_Produzione": int(request.form.get('anno')),
                    "Data_Immatricolazione": request.form.get('data_immatricolazione'),
                    "Kilometraggio": int(request.form.get('km')),
                    "Potenza_CV": int(request.form.get('potenza_cv')),
                    "Peso": float(request.form.get('peso')),
                    "Tipologia_Motrice": request.form.get('tipologia_motrice'),
                    "Classe_Inquinamento": request.form.get('classe_inquinamento'),
                    "Configurazione_Assi": request.form.get('configurazione_assi'),
                    "Numero_Assi": int(request.form.get('numero_assi')),
                    "Descrizione": request.form.get('descrizione_veicolo'),
                    "Prezzo_Base": float(request.form.get('prezzo')), 
                    "Stato_Disponibilita": 'U',
                    "ID_Marca": id_marca
                }
                supabase.table('VEICOLO').insert(nuovo_veicolo).execute()
            else:
                telaio = request.form.get('telaio_esistente')
                res_veicolo = supabase.table('VEICOLO').select('Targa').eq('NumeroTelaio', telaio).execute()
                targa = res_veicolo.data[0]['Targa'] if res_veicolo.data else ""

            # Creiamo la valutazione 
            prezzo_proposto = request.form.get('prezzo_proposto')
            prezzo_proposto = float(prezzo_proposto) if prezzo_proposto else 0.0
            
            nuova_valutazione = {
                "NumeroTelaio": telaio,
                "Targa": targa,
                "Data_Inizio": request.form.get('data'),
                "Prezzo_Proposto": prezzo_proposto,
                "Note_Cliente": request.form.get('descrizione'),
                "ID_Persona": session.get('user_id')
            }
            supabase.table('VALUTAZIONE_USATO').insert(nuova_valutazione).execute()
            flash("Proposta dell'usato inviata con successo!", "success")
            return redirect('/area_cliente')

        except Exception as e:
            print(f"ERRORE PROPOSTA USATO: {e}")
            flash(f"Errore DB: {str(e)}", "danger")
            return redirect('/proponi_usato')

    # FASE GET: Caricamento auto esistenti del cliente
    try:
        id_cliente = session.get('user_id')
        res_pren = supabase.table('PRENOTAZIONE').select('NumeroTelaio').eq('ID_Persona', id_cliente).execute()
        res_val = supabase.table('VALUTAZIONE_USATO').select('NumeroTelaio').eq('ID_Persona', id_cliente).execute()
        
        tutti_i_telai = list(set([r['NumeroTelaio'] for r in res_pren.data] + [r['NumeroTelaio'] for r in res_val.data]))
        
        auto_cliente = []
        if tutti_i_telai:
            res_veicoli = supabase.table('VEICOLO').select('*').in_('NumeroTelaio', tutti_i_telai).execute()
            auto_cliente = res_veicoli.data
            
            for auto in auto_cliente:
                id_marca = auto.get('ID_Marca')
                auto['Marca_Nome'] = "N/D"
                if id_marca:
                    res_marca = supabase.table('MARCA').select('Nome').eq('ID_Marca', id_marca).execute()
                    if res_marca.data:
                        auto['Marca_Nome'] = res_marca.data[0]['Nome']
    except Exception as e:
        auto_cliente = []

    # <-- MODIFICATO: ora punta alla cartella giusta
    return render_template('prenotazioni/proponi_usato.html', auto_cliente=auto_cliente)

# --- PRENOTAZIONE OFFICINA ---
@main.route('/prenota', methods=['GET', 'POST'])
@ruolo_richiesto(1)
def prenota_intervento():
    if request.method == 'POST':
        try:
            tipo_inserimento = request.form.get('tipo_inserimento')
            id_cliente = session.get('user_id')

            if tipo_inserimento == 'nuovo':
                telaio = request.form.get('numero_telaio').upper()
                targa = request.form.get('targa').upper()
                nome_marca = request.form.get('marca').strip().capitalize()
                
                res_marca = supabase.table('MARCA').select('ID_Marca').eq('Nome', nome_marca).execute()
                if res_marca.data:
                    id_marca = res_marca.data[0]['ID_Marca']
                else:
                    res_nuova = supabase.table('MARCA').insert({"Nome": nome_marca, "Attiva": "Y"}).execute()
                    id_marca = res_nuova.data[0]['ID_Marca']

                # Salviamo il veicolo nuovo in modo completo
                nuovo_veicolo = {
                    "NumeroTelaio": telaio,
                    "Targa": targa,
                    "Modello": request.form.get('modello')[:15],
                    "Anno_Produzione": int(request.form.get('anno')),
                    "Data_Immatricolazione": request.form.get('data_immatricolazione'),
                    "Kilometraggio": int(request.form.get('km')),
                    "Potenza_CV": int(request.form.get('potenza_cv')),
                    "Peso": float(request.form.get('peso')),
                    "Tipologia_Motrice": request.form.get('tipologia_motrice'),
                    "Classe_Inquinamento": request.form.get('classe_inquinamento'),
                    "Configurazione_Assi": request.form.get('configurazione_assi'),
                    "Numero_Assi": int(request.form.get('numero_assi')),
                    "Descrizione": request.form.get('descrizione_veicolo'),
                    "Prezzo_Base": float(request.form.get('prezzo')), 
                    "Stato_Disponibilita": 'U',
                    "ID_Marca": id_marca
                }
                supabase.table('VEICOLO').insert(nuovo_veicolo).execute()
            else:
                telaio = request.form.get('telaio_esistente')
                res_veicolo = supabase.table('VEICOLO').select('Targa').eq('NumeroTelaio', telaio).execute()
                targa = res_veicolo.data[0]['Targa'] if res_veicolo.data else ""

            # Creazione Prenotazione
            nuova_prenotazione = {
                "ID_Persona": id_cliente,
                "Targa": targa,
                "NumeroTelaio": telaio,
                "Data_Prenotazione": request.form.get('data'),
                "Ora_Incontro": request.form.get('ora'),
                "Nota_Cliente": request.form.get('note'),
                "ID_Sede": int(request.form.get('sede'))
            }

            supabase.table('PRENOTAZIONE').insert(nuova_prenotazione).execute()
            flash("Richiesta inviata con successo!", "success")
            return redirect('/area_cliente')

        except Exception as e:
            print(f"ERRORE PRENOTAZIONE: {e}")
            flash(f"Errore DB: {str(e)}", "danger")
            return redirect('/prenota')

    # FASE GET: Caricamento auto e sedi
    try:
        id_cliente = session.get('user_id')
        res_pren = supabase.table('PRENOTAZIONE').select('NumeroTelaio').eq('ID_Persona', id_cliente).execute()
        res_val = supabase.table('VALUTAZIONE_USATO').select('NumeroTelaio').eq('ID_Persona', id_cliente).execute()
        
        tutti_i_telai = list(set([r['NumeroTelaio'] for r in res_pren.data] + [r['NumeroTelaio'] for r in res_val.data]))
        
        auto_cliente = []
        if tutti_i_telai:
            res_veicoli = supabase.table('VEICOLO').select('*').in_('NumeroTelaio', tutti_i_telai).execute()
            auto_cliente = res_veicoli.data
            for auto in auto_cliente:
                id_marca = auto.get('ID_Marca')
                auto['Marca_Nome'] = "N/D"
                if id_marca:
                    res_marca = supabase.table('MARCA').select('Nome').eq('ID_Marca', id_marca).execute()
                    if res_marca.data:
                        auto['Marca_Nome'] = res_marca.data[0]['Nome']
        
        # <-- AGGIUNTO: ESTREAZIAMO LE SEDI
        sedi = supabase.table('SEDE').select('*').execute().data

    except Exception as e:
        auto_cliente = []
        sedi = []

    # <-- MODIFICATO: ora punta alla cartella giusta e passa le sedi
    return render_template('prenotazioni/prenota.html', auto_cliente=auto_cliente, sedi=sedi)
# --- WIZARD USATO FASE 2: PERIZIA TECNICA (LATO MECCANICO) ---
@main.route('/meccanico/valutazioni', methods=['GET', 'POST'])
@ruolo_richiesto(2)
def perizia_meccanico():
    if request.method == 'POST':
        try:
            nuovo_esito = {
                "ID_Usato": int(request.form.get('id_pratica')),            
                "ID_Persona": session.get('user_id'),
                "Esito_Meccanico": request.form.get('stato_meccanico')[:1], 
                "Prezzo_Consigliato": float(request.form.get('prezzo_consigliato')),
                "Descrizione": request.form.get('descrizione_danni')        
            }
            
            supabase.table('Esito_MV').insert(nuovo_esito).execute()
            flash("Perizia tecnica inviata al Capofficina!", "success")
            return redirect('/dashboard_meccanico')
            
        except Exception as e:
            print(f"🔴 ERRORE SALVATAGGIO PERIZIA: {str(e)}")
            flash(f"Errore DB: {str(e)}", "danger")
            return redirect('/meccanico/valutazioni')

    try:
        res_esiti = supabase.table('Esito_MV').select('ID_Usato').execute()
        auto_gia_valutate = [r['ID_Usato'] for r in res_esiti.data]

        res_approvate = supabase.table('Approvazione_PV').select('ID_Usato').execute()
        auto_gia_approvate = [r['ID_Usato'] for r in res_approvate.data]

        esclusioni = set(auto_gia_valutate + auto_gia_approvate)

        res_val = supabase.table('VALUTAZIONE_USATO').select('*').execute()
        pratiche_raw = res_val.data
        pratiche_completate = []

        for p in pratiche_raw:
            id_usato = p.get("ID_Usato")
            
            if id_usato in esclusioni:
                continue

            info_pratica = {
                "ID_Usato": id_usato,
                "Targa": p.get("Targa"),
                "NumeroTelaio": p.get("NumeroTelaio"),
                "Data_Inizio": p.get("Data_Inizio"),
                "ID_Persona": p.get("ID_Persona"),
                "Marca": "N/D",  
                "Modello": "",
                "Km": "N/D"
            }
            
            res_v = supabase.table('VEICOLO').select('*').eq('NumeroTelaio', p.get("NumeroTelaio")).execute()
            if res_v.data:
                veicolo = res_v.data[0]
                info_pratica["Modello"] = veicolo.get("Modello", "")
                info_pratica["Km"] = veicolo.get("Kilometraggio", "N/D")
                
                id_marca = veicolo.get("ID_Marca")
                if id_marca:
                    res_m = supabase.table('MARCA').select('Nome').eq('ID_Marca', id_marca).execute()
                    if res_m.data:
                        info_pratica["Marca"] = res_m.data[0].get("Nome", "N/D")
            
            pratiche_completate.append(info_pratica)

        return render_template('meccanico/lista_valutazioni.html', pratiche=pratiche_completate)
        
    except Exception as e:
        print(f"🔴 ERRORE LETTURA PRATICHE MECCANICO: {str(e)}")
        flash(f"Impossibile caricare le valutazioni: {str(e)}", "danger")
        return redirect('/dashboard_meccanico')

# --- WIZARD USATO FASE 3: APPROVAZIONE FINALE (LATO ADMIN) ---
@main.route('/admin/approva_usato', methods=['GET', 'POST'])
@ruolo_richiesto(4)
def approva_usato():
    if request.method == 'POST':
        try:
            id_pratica = int(request.form.get('id_pratica')) 
            prezzo_finale = float(request.form.get('prezzo_finale'))
            decisione = request.form.get('decisione') 
            note_admin = request.form.get('nota_proprietario', 'Approvato da Admin')

            supabase.table('VALUTAZIONE_USATO').update({
                "Data_Fine": request.form.get('data_approvazione'),
                "Prezzo_Finale": prezzo_finale
            }).eq('ID_Usato', id_pratica).execute()

            approvazione_data = {
                "ID_Usato": id_pratica,                                          
                "Nota_Proprietario": note_admin[:500],            
                "Stato_Decisione": decisione[:1],                
                "ID_Persona": session.get('user_id')            
            }
            
            supabase.table('Approvazione_PV').insert(approvazione_data).execute()

            if decisione.upper().startswith('A'): 
                flash("Veicolo acquistato e archiviato nello stock!", "success")
            else:
                flash("Proposta rifiutata definitivamente.", "warning")
                
            return redirect('/dashboard_admin')
            
        except Exception as e:
            print(f"🔴 ERRORE APPROVAZIONE ADMIN: {str(e)}")
            flash(f"Supabase ha rifiutato l'approvazione. Errore: {str(e)}", "danger")
            return redirect('/admin/approva_usato')

    try:
        res_approvate = supabase.table('Approvazione_PV').select('ID_Usato').execute()
        pratiche_gia_chiuse = [r['ID_Usato'] for r in res_approvate.data]

        res_esiti = supabase.table('Esito_MV').select('*').execute()
        perizie_raw = res_esiti.data
        perizie_completate = []
        
        for perizia in perizie_raw:
            id_usato = perizia.get("ID_Usato")
            
            if id_usato in pratiche_gia_chiuse:
                continue

            id_meccanico = perizia.get("ID_Persona")
            res_val = supabase.table('VALUTAZIONE_USATO').select('*').eq('ID_Usato', id_usato).execute()
            
            if res_val.data:
                valutazione = res_val.data[0]
                info_completa = {
                    "ID_Usato": id_usato,
                    "Descrizione": perizia.get("Descrizione"),
                    "Esito_Meccanico": perizia.get("Esito_Meccanico"),
                    "Prezzo_Consigliato": perizia.get("Prezzo_Consigliato"),
                    "Meccanico_Nome": "Meccanico",
                    "Meccanico_Cognome": f"(ID: {id_meccanico})",
                    "Targa": valutazione.get("Targa"),
                    "NumeroTelaio": valutazione.get("NumeroTelaio")
                }
                
                res_pers = supabase.table('PERSONA').select('Nome', 'Cognome').eq('ID_Persona', id_meccanico).execute()
                if res_pers.data:
                    persona = res_pers.data[0]
                    info_completa["Meccanico_Nome"] = persona.get("Nome")
                    info_completa["Meccanico_Cognome"] = persona.get("Cognome")
                    
                perizie_completate.append(info_completa)
            
        return render_template('admin/approva_usato.html', perizie=perizie_completate)
        
    except Exception as e:
        print(f"🔴 ERRORE LETTURA PERIZIE ADMIN: {str(e)}")
        flash(f"Impossibile caricare l'elenco delle perizie: {str(e)}", "danger")
        return redirect('/dashboard_admin')

# --- AREA CLIENTE: IL MIO GARAGE ---
@main.route('/mie_auto')
@ruolo_richiesto(1)
def mie_auto():
    try:
        id_cliente = session.get('user_id')
        
        res_pren = supabase.table('PRENOTAZIONE').select('NumeroTelaio').eq('ID_Persona', id_cliente).execute()
        telai_prenotati = [r['NumeroTelaio'] for r in res_pren.data]
        
        res_val = supabase.table('VALUTAZIONE_USATO').select('NumeroTelaio').eq('ID_Persona', id_cliente).execute()
        telai_valutati = [r['NumeroTelaio'] for r in res_val.data]
        
        tutti_i_telai = list(set(telai_prenotati + telai_valutati))
        auto_cliente = []
        
        if tutti_i_telai:
            res_veicoli = supabase.table('VEICOLO').select('*').in_('NumeroTelaio', tutti_i_telai).execute()
            auto_cliente = res_veicoli.data
            
            # MAGIA DOPPIA CHIAVE: Evita colonne vuote nell'HTML sia se cerca 'Marca' che 'Nome_Marca'
            for auto in auto_cliente:
                id_marca = auto.get('ID_Marca')
                auto['Nome_Marca'] = "N/D"
                auto['Marca'] = "N/D"
                if id_marca:
                    res_marca = supabase.table('MARCA').select('Nome').eq('ID_Marca', id_marca).execute()
                    if res_marca.data:
                        auto['Nome_Marca'] = res_marca.data[0]['Nome']
                        auto['Marca'] = res_marca.data[0]['Nome']
        
        return render_template('prenotazioni/mie_auto.html', auto=auto_cliente)
        
    except Exception as e:
        print(f"🔴 ERRORE GARAGE: {str(e)}")
        flash(f"Errore caricamento garage: {str(e)}", "danger")
        return redirect('/area_cliente')

# --- AMMINISTRAZIONE: VEDI PRENOTAZIONI IN SOSPESO ---
@main.route('/admin/prenotazioni')
@ruolo_richiesto(4) 
def gestione_prenotazioni():
    try:
        res_pren = supabase.table('PRENOTAZIONE').select('*').is_('ID_Intervento', 'null').execute()
        prenotazioni_raw = res_pren.data
        prenotazioni_pendenti = []
        
        for pren in prenotazioni_raw:
            info_pren = pren.copy()
            info_pren['PERSONA'] = {"Nome": "N/D", "Cognome": "N/D"}
            
            id_cliente = pren.get('ID_Persona')
            if id_cliente:
                res_cliente = supabase.table('PERSONA').select('Nome', 'Cognome').eq('ID_Persona', id_cliente).execute()
                if res_cliente.data:
                    info_pren['PERSONA']['Nome'] = res_cliente.data[0].get('Nome')
                    info_pren['PERSONA']['Cognome'] = res_cliente.data[0].get('Cognome')
                    
            prenotazioni_pendenti.append(info_pren)

        res_mecc = supabase.table('PERSONA').select('*').eq('Ruolo', 2).execute()
        meccanici = res_mecc.data

        return render_template('admin/gestione_prenotazioni.html', 
                               prenotazioni=prenotazioni_pendenti, meccanici=meccanici)
                               
    except Exception as e:
        return f"<h1>🔴 CRASH GESTIONE PRENOTAZIONI</h1><p>L'errore esatto di Supabase è: <b>{str(e)}</b></p>"

# --- AMMINISTRAZIONE: ASSEGNA IL LAVORO ---
@main.route('/admin/assegna_lavoro', methods=['POST'])
@ruolo_richiesto(4)
def assegna_lavoro():
    try:
        id_prenotazione = int(request.form.get('id_prenotazione'))
        targa = request.form.get('targa')
        data_inizio = request.form.get('data')
        ora_inizio = request.form.get('ora')
        id_meccanico = int(request.form.get('id_meccanico'))
        nome_compito = request.form.get('nome_compito')
        durata = int(request.form.get('durata'))

        nuovo_intervento = {
            "Targa": targa, 
            "ID_Officina": 1, 
            "Data_Inizio": data_inizio, 
            "Orario_Inizio": ora_inizio, 
            "Tipologia_Intervento": "Manutenzione", 
            "Costo": 0.0, 
            "Note": "Assegnato da Web", 
            "Durata": durata, 
            "Km_Veicolo": 0 
        }
        res_intervento = supabase.table('INTERVENTO').insert(nuovo_intervento).execute()
        id_intervento_db = res_intervento.data[0]['ID_Intervento']

        nuovo_compito = {
            "ID_Intervento": id_intervento_db, 
            "ID_Persona": id_meccanico, 
            "Nome": nome_compito[:20], 
            "Durata": durata, 
            "Data_Inizio": data_inizio,
            "Stato": "Da fare"  # <--- AGGIUNTO ESPLICITAMENTE!
        }
        supabase.table('COMPITO').insert(nuovo_compito).execute()

        supabase.table('PRENOTAZIONE').update({"ID_Intervento": id_intervento_db}).eq('ID_Prenotazione', id_prenotazione).execute()
        
        flash("Lavoro assegnato con successo al meccanico!", "success")
        return redirect('/admin/prenotazioni')
        
    except Exception as e:
        print(f"🔴 ERRORE ASSEGNAZIONE LAVORO: {e}")
        flash(f"Errore DB durante l'assegnazione: {str(e)}", "danger")
        return redirect('/admin/prenotazioni')

# --- ROTTA CATALOGO PUBBLICO (TEAM) ---
@main.route('/catalog', methods=['GET'])
def public_catalog():
    try:
        # 1. Leggiamo i filtri se l'utente ha premuto "Apply Filters"
        condition = request.args.get('condition')  # 'New' o 'Used'
        brand_name = request.args.get('brand')
        model_query = request.args.get('model')
        max_price = request.args.get('max_price')

        # 2. Peschiamo tutte le marche attive
        res_marche = supabase.table('MARCA').select('*').eq('Attiva', 'Y').execute()
        brands = res_marche.data
        mappa_marche = {marca['ID_Marca']: marca['Nome'] for marca in brands}

        # 3. Iniziamo a costruire la Query per i VEICOLI (escludendo sempre gli archiviati 'A')
        query = supabase.table('VEICOLO').select('*').neq('Stato_Disponibilita', 'A')

        # --- APPLICHIAMO I FILTRI ---
        
        # Filtro Condizione (Nel db abbiamo 'N' = Nuovo, 'U' = Usato)
        if condition == 'New':
            query = query.eq('Stato_Disponibilita', 'N')
        elif condition == 'Used':
            query = query.eq('Stato_Disponibilita', 'U')

        # Filtro Brand
        if brand_name:
            # Troviamo l'ID_Marca associato al nome selezionato
            id_marca = next((m['ID_Marca'] for m in brands if m['Nome'] == brand_name), None)
            if id_marca:
                query = query.eq('ID_Marca', id_marca)

        # Filtro Modello (ricerca parziale)
        if model_query:
            query = query.ilike('Modello', f'%{model_query}%')

        # Filtro Prezzo
        if max_price:
            query = query.lte('Prezzo_Base', float(max_price))

        # Eseguiamo la query finale!
        vehicles = query.execute().data

    except Exception as e:
        print(f"ERRORE CATALOGO PUBBLICO: {e}")
        vehicles = []
        brands = []
        mappa_marche = {}

    return render_template('public_catalog.html', vehicles=vehicles, brands=brands, mappa_marche=mappa_marche)

# --- API OPTIONAL VEICOLO (TEAM) ---
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

# --- DASHBOARD VENDITORE (TEAM) ---
@main.route('/salespearson', methods=['GET'])
@ruolo_richiesto(3)  # 3 = Venditore
def salespearson_dashboard():
    try:
        # 1. Contatore veicoli in catalogo (non archiviati)
        res_veicoli = supabase.table('VEICOLO').select('NumeroTelaio, Modello').neq('Stato_Disponibilita', 'A').execute()
        veicoli_disponibili = len(res_veicoli.data)
        
        # Prepariamo la mappa dei veicoli per tradurre il telaio nel nome del Modello
        tutti_veicoli = supabase.table('VEICOLO').select('NumeroTelaio, Modello').execute().data
        mappa_veicoli = {v['NumeroTelaio']: v['Modello'] for v in tutti_veicoli}

        # Prepariamo la mappa dei clienti per tradurre l'ID nel Nome e Cognome
        clienti = supabase.table('PERSONA').select('ID_Persona, Nome, Cognome').eq('Ruolo', 1).execute().data
        mappa_clienti = {c['ID_Persona']: f"{c['Nome']} {c['Cognome']}" for c in clienti}

        id_venditore = session['user_id']

        # 2. TRATTATIVE (Preventivi Aperti) assegnati a QUESTO venditore
        preventivi_raw = supabase.table('PREVENTIVO').select('*').eq('ID_Persona', id_venditore).eq('Stato_PreventivoChiuso', 'N').execute().data
        
        quotes = []
        for p in preventivi_raw:
            quotes.append({
                "id": p['ID_Preventivo'],
                "cliente": mappa_clienti.get(p.get('Pos_ID_Persona'), "Cliente Ignoto"),
                "veicolo": mappa_veicoli.get(p.get('NumeroTelaio'), "Veicolo Ignoto")
            })

        # 3. TEST DRIVE assegnati a QUESTO venditore in supervisione
        test_drives_raw = supabase.table('TEST_DRIVE').select('*').eq('Sup_ID_Persona', id_venditore).execute().data
        
        slot_orari = supabase.table('SLOT_ORARIO').select('*').execute().data
        mappa_slot = {s['ID_Slot']: f"{s['Ora_Inizio']} - {s['Ora_Fine']}" for s in slot_orari}
        
        # Tabella ponte per trovare a quale auto si riferisce il test drive
        utilizzo_td = supabase.table('Utilizzo_TV').select('*').execute().data
        mappa_utilizzo = {u['ID_TestDrive']: u['NumeroTelaio'] for u in utilizzo_td}

        test_drives = []
        for td in test_drives_raw:
            telaio_td = mappa_utilizzo.get(td['ID_TestDrive'], "")
            modello_td = mappa_veicoli.get(telaio_td, "Veicolo Ignoto")

            test_drives.append({
                "data": td['Data'],
                "orario": mappa_slot.get(td['ID_Slot'], "Orario ignoto"),
                "cliente": mappa_clienti.get(td['ID_Persona'], "Cliente ignoto"),
                "veicolo": modello_td
            })

    except Exception as e:
        print(f"ERRORE DASHBOARD VENDITORE: {e}")
        veicoli_disponibili, quotes, test_drives = 0, [], []

    return render_template('salespearson_dashboard.html', 
                           quotes=quotes, 
                           test_drives=test_drives, 
                           stock_count=veicoli_disponibili)

# --- TRANSACTION WIZARD VENDITORE (TEAM) ---
@main.route('/transaction_wizard', methods=['GET', 'POST'])
@ruolo_richiesto(3) # Solo per i Venditori
def transaction_wizard():
    if request.method == 'POST':
        try:
            # 1. Recupero Dati dal Form
            id_cliente = int(request.form.get('id_cliente'))
            numero_telaio = request.form.get('numero_telaio')
            tipo_contratto = request.form.get('contract_type') # Vendita, Noleggio, Finanziamento, Leasing
            data_inizio = request.form.get('start_date')
            data_fine = request.form.get('end_date') or data_inizio # Fallback
            metodo_pagamento = request.form.get('payment_method')
            id_venditore = session['user_id']
            oggi = datetime.now().strftime("%Y-%m-%d")
            ora = datetime.now().strftime("%H:%M")

            # 2. Recupero prezzo del veicolo per il contratto
            res_veicolo = supabase.table('VEICOLO').select('Prezzo_Base').eq('NumeroTelaio', numero_telaio).execute()
            prezzo = res_veicolo.data[0]['Prezzo_Base'] if res_veicolo.data else 0.0

            # 3. Creazione METODO_PAGAMENTO (Ci serve l'ID per il contratto)
            max_pag = supabase.table('METODO_PAGAMENTO').select('ID_Pagamento').order('ID_Pagamento', desc=True).limit(1).execute()
            id_pag = max_pag.data[0]['ID_Pagamento'] + 1 if max_pag.data else 1
            
            supabase.table('METODO_PAGAMENTO').insert({
                "ID_Pagamento": id_pag,
                "Circuito": "Circuito Standard",
                "Intestatario": "Cliente",
                "Tipologia": metodo_pagamento,
                "Iban": "IT00000000000000000000000000000000"
            }).execute()

            # 4. Creazione CONTRATTO
            max_contr = supabase.table('CONTRATTO').select('ID_Contratto').order('ID_Contratto', desc=True).limit(1).execute()
            id_contratto = max_contr.data[0]['ID_Contratto'] + 1 if max_contr.data else 1
            
            nuovo_contratto = {
                "ID_Contratto": id_contratto,
                "Tipo_Contratto": tipo_contratto[:14],
                "Stato": "Attivo",
                "Data_Decorrenza": data_inizio,
                "Note_Legali": f"Generato da Wizard. Tipo: {tipo_contratto}",
                "Data_Scadenza": data_fine,
                "Importo_Totale": float(prezzo),
                "Data_Stipula": oggi,
                "ID_Persona": id_cliente,
                "ID_Pagamento": id_pag
            }
            supabase.table('CONTRATTO').insert(nuovo_contratto).execute()

            # 5. SPECIALIZZAZIONE CONTRATTO IN BASE ALLA SCELTA (Query 5.1.9)
            if tipo_contratto == 'Noleggio':
                supabase.table('NOLEGGIO').insert({
                    "ID_Contratto": id_contratto,
                    "Data_Inizio": data_inizio,
                    "Data_Fine": data_fine,
                    "Franchigia_assicurativa": 500.00,
                    "Prezzo_km": 15,
                    "Km_totali": 10000
                }).execute()
            
            elif tipo_contratto == 'Vendita':
                max_v = supabase.table('VENDITA').select('ID_Vendita').order('ID_Vendita', desc=True).limit(1).execute()
                id_vendita = max_v.data[0]['ID_Vendita'] + 1 if max_v.data else 1
                supabase.table('VENDITA').insert({
                    "ID_Vendita": id_vendita,
                    "ID_Contratto": id_contratto,
                    "Stato": "C",
                    "Data_Vendita": oggi,
                    "Ora_Vendita": ora,
                    "ID_Persona": id_venditore
                }).execute()
            
            elif tipo_contratto == 'Finanziamento':
                supabase.table('FINANZIAMENTO').insert({
                    "ID_Contratto": id_contratto,
                    "Assicurazione_Credito": 1000,
                    "Spese_Apertura_Pratica": 300,
                    "Anticipo": prezzo * 0.20, # Anticipo 20%
                    "TAEG": 6.5,
                    "TAN": 5.0
                }).execute()
                
            elif tipo_contratto == 'Leasing':
                max_l = supabase.table('LEASING').select('ID_Leasing').order('ID_Leasing', desc=True).limit(1).execute()
                id_leasing = max_l.data[0]['ID_Leasing'] + 1 if max_l.data else 1
                supabase.table('LEASING').insert({
                    "ID_Contratto": id_contratto,
                    "ID_Leasing": id_leasing,
                    "Importo_Mensile": 450,
                    "Data_Inizio": data_inizio,
                    "Data_Fine": data_fine,
                    "Maxi_Canone": 5000,
                    "P_IVA_Societa": "IT123456789",
                    "Prezzo_Riscatto": prezzo * 0.40
                }).execute()

            # 6. AGGIORNAMENTO VEICOLO (Riservato/Archiviato)
            supabase.table('VEICOLO').update({
                'ID_Contratto': id_contratto,
                'Stato_Disponibilita': 'A'
            }).eq('NumeroTelaio', numero_telaio).execute()

            flash(f"Successo! {tipo_contratto} registrato e auto bloccata per il cliente.", "success")
            return redirect('/salespearson')

        except Exception as e:
            print(f"ERRORE WIZARD TRANSAZIONE: {e}")
            flash(f"Errore durante l'operazione. Dettagli: {e}", "danger")
            return redirect('/transaction_wizard')

    # --- GET: Caricamento dati per riempire i menu a tendina ---
    try:
        clienti = supabase.table('PERSONA').select('*').eq('Ruolo', 1).execute().data
        veicoli = supabase.table('VEICOLO').select('*').neq('Stato_Disponibilita', 'A').execute().data

        res_marche = supabase.table('MARCA').select('*').execute().data
        mappa_marche = {m['ID_Marca']: m['Nome'] for m in res_marche}
    except Exception as e:
        print(f"ERRORE CARICAMENTO WIZARD: {e}")
        clienti, veicoli, mappa_marche = [], [], {}

    return render_template('sales/transaction_wizard.html', clienti=clienti, veicoli=veicoli, mappa_marche=mappa_marche)

# --- CALENDARIO TEST DRIVE (TEAM) ---
@main.route('/test_drive_calendar', methods=['GET', 'POST'])
@ruolo_richiesto(3) # Solo i Venditori possono gestire i test drive
def test_drive_calendar():
    if request.method == 'POST':
        try:
            # 1. Raccogliamo i dati dal form modale
            data_td = request.form.get('data_test')
            id_slot = int(request.form.get('id_slot'))
            id_cliente = int(request.form.get('id_cliente'))
            numero_telaio = request.form.get('numero_telaio')
            id_venditore = session['user_id'] # Il venditore loggato
            
            # 2. Inserimento in TEST_DRIVE
            nuovo_td = {
                "Data": data_td,
                "ID_Slot": id_slot,
                "ID_Persona": id_cliente,
                "Sup_ID_Persona": id_venditore
            }
            res_td = supabase.table('TEST_DRIVE').insert(nuovo_td).execute()
            
            # 3. Inserimento nella tabella ponte Utilizzo_TV (Lega l'auto al Test Drive)
            if res_td.data:
                id_generato = res_td.data[0]['ID_TestDrive']
                supabase.table('Utilizzo_TV').insert({
                    "NumeroTelaio": numero_telaio,
                    "ID_TestDrive": id_generato
                }).execute()
                
            flash("Test Drive prenotato con successo!", "success")
        except Exception as e:
            print(f"ERRORE PRENOTAZIONE TEST DRIVE: {e}")
            flash("Errore durante il salvataggio nel database.", "danger")
            
        return redirect('/test_drive_calendar')

    # --- FASE DI GET: CARICAMENTO DATI PER IL CALENDARIO ---
    try:
        clienti = supabase.table('PERSONA').select('*').eq('Ruolo', 1).execute().data
        veicoli = supabase.table('VEICOLO').select('*').neq('Stato_Disponibilita', 'A').execute().data
        slot_orari = supabase.table('SLOT_ORARIO').select('*').execute().data
        
        prenotazioni = supabase.table('TEST_DRIVE').select('*').execute().data
        utilizzo = supabase.table('Utilizzo_TV').select('*').execute().data
        tutti_veicoli = supabase.table('VEICOLO').select('NumeroTelaio, Modello').execute().data
        
        mappa_slot = {s['ID_Slot']: s for s in slot_orari}
        mappa_clienti = {c['ID_Persona']: f"{c['Nome']} {c['Cognome']}" for c in clienti}
        mappa_veicoli = {v['NumeroTelaio']: v['Modello'] for v in tutti_veicoli}
        mappa_utilizzo = {u['ID_TestDrive']: u['NumeroTelaio'] for u in utilizzo}

        events = []
        for p in prenotazioni:
            slot = mappa_slot.get(p['ID_Slot'])
            if not slot: continue
            
            start_time = f"{p['Data']}T{slot['Ora_Inizio']}:00"
            end_time = f"{p['Data']}T{slot['Ora_Fine']}:00"
            
            cliente_nome = mappa_clienti.get(p['ID_Persona'], "Cliente Ignoto")
            telaio = mappa_utilizzo.get(p['ID_TestDrive'], "")
            modello = mappa_veicoli.get(telaio, "Veicolo Ignoto")

            events.append({
                "title": f"{modello} ({cliente_nome})",
                "start": start_time,
                "end": end_time,
                "backgroundColor": "#dc3545",
                "borderColor": "#dc3545"
            })
            
    except Exception as e:
        print(f"ERRORE CARICAMENTO CALENDARIO: {e}")
        clienti, veicoli, slot_orari, events = [], [], [], []

    return render_template('test_drive_calendar.html', 
                           clienti=clienti, veicoli=veicoli, 
                           slot_orari=slot_orari, events=events)

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