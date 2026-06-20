from functools import wraps
from flask import Blueprint, render_template, request, redirect, session, flash, jsonify
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

                # SMISTAMENTO AUTOMATICO DOPO IL LOGIN (COMPLETO)
                if utente['Ruolo'] == 4:
                    return redirect('/dashboard_admin')
                elif utente['Ruolo'] == 3:
                    return redirect('/salesperson')
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
        
        supabase.table('PERSONA').insert(nuovo_utente).execute()
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
        return redirect('/salesperson')         
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
        labels_modelli, valori_modelli, labels_venditori, valori_venditori = [], [], [], []

    return render_template('admin/dashboard.html', 
                           labels_modelli=labels_modelli, valori_modelli=valori_modelli,
                           labels_venditori=labels_venditori, valori_venditori=valori_venditori)

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
                flash(f"Veicolo {nuovo_veicolo['Modello']} inserito correttamente nel catalogo!", "success")
            except Exception as e:
                print(f"ERRORE VEICOLO: {e}")
                flash("Errore durante il salvataggio del veicolo. Controlla i dati inseriti.", "danger")
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

# --- ROTTA DASHBOARD MECCANICO (KANBAN BOARD) ---
@main.route('/dashboard_meccanico')
@ruolo_richiesto(2)
def dashboard_meccanico():
    try:
        id_meccanico = session.get('user_id')
        response = supabase.table('COMPITO').select(
            '*, INTERVENTO(Data_Inizio, Targa, OFFICINA(Nome, Interna))'
        ).eq('ID_Persona', id_meccanico).execute()

        tutti_i_compiti = response.data
        da_fare = [c for c in tutti_i_compiti if c.get('Stato', 'Da fare') == 'Da fare']
        in_corso = [c for c in tutti_i_compiti if c.get('Stato') == 'In corso']
        finiti = [c for c in tutti_i_compiti if c.get('Stato') == 'Finito']

        return render_template('meccanico/dashboard_meccanico.html', 
                               da_fare=da_fare, in_corso=in_corso, finiti=finiti)
    except Exception as e:
        print(f"ERRORE KANBAN MECCANICO: {str(e)}")
        flash("Errore nel caricamento della tua bacheca.", "danger")
        return redirect('/')

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

# --- ROTTA PRENOTAZIONE INTERVENTO (LATO CLIENTE) ---
@main.route('/prenota', methods=['GET', 'POST'])
@ruolo_richiesto(1) 
def prenota_intervento():
    if request.method == 'POST':
        try:
            targa = request.form.get('targa').upper()
            telaio = request.form.get('telaio').upper()
            id_cliente = session.get('user_id')

            res_veicolo = supabase.table('VEICOLO').select('NumeroTelaio').eq('NumeroTelaio', telaio).execute()
            
            if not res_veicolo.data:
                nuovo_veicolo_generico = {
                    "NumeroTelaio": telaio,
                    "Targa": targa,
                    "Modello": "Auto Cliente",  
                    "Kilometraggio": 0,          
                    "ID_Marca": 1                
                }
                supabase.table('VEICOLO').insert(nuovo_veicolo_generico).execute()

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
            print(f"🔴 ERRORE PRENOTAZIONE AUTOMATICA: {str(e)}")
            flash(f"Errore DB: {str(e)}", "danger")
            return redirect('/prenota')
            
    return render_template('prenotazioni/prenota.html')

# --- WIZARD USATO FASE 1: PROPOSTA CLIENTE (LATO CLIENTE) ---
@main.route('/proponi_usato', methods=['GET', 'POST'])
@ruolo_richiesto(1)
def proponi_usato():
    if request.method == 'POST':
        try:
            targa = request.form.get('targa').upper()
            telaio = request.form.get('telaio').upper()
            nome_marca_inserita = request.form.get('marca').strip().capitalize()
            
            res_marca = supabase.table('MARCA').select('ID_Marca').eq('Nome', nome_marca_inserita).execute()
            
            if res_marca.data:
                id_marca_corretta = res_marca.data[0]['ID_Marca']
            else:
                res_nuova = supabase.table('MARCA').insert({"Nome": nome_marca_inserita, "Attiva": "Y"}).execute()
                id_marca_corretta = res_nuova.data[0]['ID_Marca']

            nuovo_veicolo = {
                "NumeroTelaio": telaio,
                "Targa": targa,
                "Modello": request.form.get('modello')[:15], 
                "Kilometraggio": int(request.form.get('km')), 
                "ID_Marca": id_marca_corretta  
            }
            
            try:
                supabase.table('VEICOLO').insert(nuovo_veicolo).execute()
            except Exception as e_veicolo:
                print(f"ERRORE INSERIMENTO VEICOLO: {str(e_veicolo)}")
                flash(f"Impossibile registrare il veicolo nei sistemi.", "danger")
                return redirect('/proponi_usato')
                
            nuova_valutazione = {
                "NumeroTelaio": telaio,
                "Targa": targa,
                "Data_Inizio": request.form.get('data'),
                "ID_Persona": session.get('user_id')
            }
            supabase.table('VALUTAZIONE_USATO').insert(nuova_valutazione).execute()
            
            flash("Proposta dell'usato inviata con successo!", "success")
            return redirect('/area_cliente')
            
        except Exception as e:
            print(f"🔴 ERRORE FATALE DB VALUTAZIONE: {str(e)}")
            flash(f"Supabase ha rifiutato la valutazione. Errore: {str(e)}", "danger")
            return redirect('/proponi_usato')
            
    return render_template('prenotazioni/proponi_usato.html')

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

# --- AREA CLIENTE: IL MIO GARAGE PERFECT FIX ---
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
            "Data_Inizio": data_inizio
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
        vehicles, brands, mappa_marche = [], [], {}

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
                           quotes=quotes, test_drives=test_drives, stock_count=veicoli_disponibili)

# --- TRANSACTION WIZARD VENDITORE (TEAM) ---
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

    return render_template('sales/transaction_wizard.html', clienti=clienti, veicoli=veicoli, mappa_marche=mappa_marche)

# --- CALENDARIO TEST DRIVE (TEAM) ---
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
    return render_template('test_drive_calendar.html')
