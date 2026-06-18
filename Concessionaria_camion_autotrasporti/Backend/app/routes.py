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
            # QUERY: Ricerca utente usando 'Mail'
            response = supabase.table('PERSONA').select('*').eq('Mail', email).execute()
            utenti = response.data

            if not utenti:
                flash("Account inesistente. Registrati.", "warning")
                return redirect('/login')
                
            utente = utenti[0]
            # Controllo password
            if utente['Password'] == password:
                session['user_id'] = utente['ID_Persona']
                session['ruolo'] = utente['Ruolo'] 
                session['nome'] = utente['Nome']

                # SMISTAMENTO AUTOMATICO DOPO IL LOGIN
                if utente['Ruolo'] == 4:
                    return redirect('/dashboard_admin')
                elif utente['Ruolo'] == 2:  # 2 è il Meccanico nel tuo DB
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
            "Ruolo": 1  # 1 = Cliente
        }
        
        supabase.table('PERSONA').insert(nuovo_utente).execute()
        flash("Registrazione completata! Ora puoi accedere.", "success")
        return redirect('/login')
        
    except Exception as e:
        print(f"ERRORE REGISTRAZIONE: {str(e)}")
        flash("Errore nel salvataggio dati.", "danger")
        return redirect('/login')

# --- HOME / SMISTAMENTO CENTRALE ---
@main.route('/')
def home():
    if 'user_id' not in session: return redirect('/login')
    if session['ruolo'] == 4: return redirect('/dashboard_admin')
    if session['ruolo'] == 2: return redirect('/dashboard_meccanico')
    if session['ruolo'] == 1: return redirect('/area_cliente')
    return "Benvenuto!"

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
    return render_template('admin_utenti.html', utenti=response.data)

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

# --- AMMINISTRAZIONE: CATALOGO ---
@main.route('/admin/catalog', methods=['GET', 'POST'])
@ruolo_richiesto(4) 
def gestione_catalogo():
    if request.method == 'POST':
        if 'aggiungi_marca' in request.form:
            nome_marca = request.form.get('nome_marca')
            try:
                supabase.table('MARCA').insert({"Nome": nome_marca, "Attiva": "Y"}).execute()
                flash(f"Marca {nome_marca} aggiunta con successo!", "success")
            except Exception as e:
                print(f"ERRORE MARCA: {e}")
                flash("Errore durante l'inserimento della marca.", "danger")
            return redirect('/admin/catalog')
    try:
        res_marche = supabase.table('MARCA').select('*').execute()
        lista_marche = res_marche.data
        res_veicoli = supabase.table('VEICOLO').select('*').execute()
        lista_veicoli = res_veicoli.data
    except Exception as e:
        print(f"ERRORE LETTURA CATALOGO: {e}")
        lista_marche, lista_veicoli = [], []
    return render_template('admin/catalog.html', marche=lista_marche, veicoli=lista_veicoli)

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
            nuova_prenotazione = {
                "ID_Persona": session.get('user_id'),
                "Targa": request.form.get('targa').upper(),
                "NumeroTelaio": request.form.get('telaio').upper(),
                "Data_Prenotazione": request.form.get('data'),
                "Ora_Incontro": request.form.get('ora'),
                "Nota_Cliente": request.form.get('note'),
                "ID_Sede": int(request.form.get('sede'))
            }
            supabase.table('PRENOTAZIONE').insert(nuova_prenotazione).execute()
            flash("Richiesta inviata con successo!", "success")
            return redirect('/area_cliente')
        except Exception as e:
            # 🛑 ORA STAMPIAMO L'ERRORE VERO DIRETTAMENTE SULLO SCHERMO!
            print(f"🔴 ERRORE PRENOTAZIONE: {str(e)}")
            flash(f"Errore DB: {str(e)}", "danger")
            return redirect('/prenota')
            
    return render_template('prenotazioni/prenota.html')

# =====================================================================
# --- WIZARD USATO FASE 1: PROPOSTA CLIENTE (LATO CLIENTE) ---
# =====================================================================
@main.route('/proponi_usato', methods=['GET', 'POST'])
@ruolo_richiesto(1)
def proponi_usato():
    if request.method == 'POST':
        try:
            targa = request.form.get('targa').upper()
            telaio = request.form.get('telaio').upper()
            
            # Formattiamo bene il nome inserito dall'utente (es. "scania" -> "Scania")
            nome_marca_inserita = request.form.get('marca').strip().capitalize()
            
            # --- MAGIA DINAMICA: Gestione della Marca ---
            # 1. Cerchiamo se la marca esiste già nel DB
            res_marca = supabase.table('MARCA').select('ID_Marca').eq('Nome', nome_marca_inserita).execute()
            
            if res_marca.data:
                # Se la marca esiste già, prendiamo il suo ID
                id_marca_corretta = res_marca.data[0]['ID_Marca']
            else:
                # Se non esiste, la inseriamo automaticamente nel catalogo!
                res_nuova = supabase.table('MARCA').insert({"Nome": nome_marca_inserita, "Attiva": "Y"}).execute()
                # E recuperiamo il nuovo ID appena generato
                id_marca_corretta = res_nuova.data[0]['ID_Marca']

            # PASSO 1: Inseriamo il veicolo
            nuovo_veicolo = {
                "NumeroTelaio": telaio,
                "Targa": targa,
                "Modello": request.form.get('modello')[:15], 
                "Kilometraggio": int(request.form.get('km')), 
                "ID_Marca": id_marca_corretta  # 🛑 ORA USA L'ID REALE, NON PIÙ 1 FISSO!
            }
            
            try:
                supabase.table('VEICOLO').insert(nuovo_veicolo).execute()
            except Exception as e_veicolo:
                print(f"ERRORE INSERIMENTO VEICOLO: {str(e_veicolo)}")
                flash(f"Impossibile registrare il veicolo nei sistemi.", "danger")
                return redirect('/proponi_usato')
                
            # PASSO 2: Inseriamo la pratica
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

# =====================================================================
# --- WIZARD USATO FASE 2: PERIZIA TECNICA (LATO MECCANICO) ---
# =====================================================================
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

    # --- LATO GET (Lettura pratiche in attesa) ---
    try:
        # FILTRO 1: Troviamo le auto che hanno già ricevuto una perizia dal meccanico
        res_esiti = supabase.table('Esito_MV').select('ID_Usato').execute()
        auto_gia_valutate = [r['ID_Usato'] for r in res_esiti.data]

        # 🛑 FILTRO 2 (NUOVO): Troviamo le auto già ACCETTATE o RIFIUTATE definitivamente dall'Admin
        res_approvate = supabase.table('Approvazione_PV').select('ID_Usato').execute()
        auto_gia_approvate = [r['ID_Usato'] for r in res_approvate.data]

        # Uniamo le esclusioni in un unico set per velocizzare il controllo
        esclusioni = set(auto_gia_valutate + auto_gia_approvate)

        # 1. Prendiamo tutte le pratiche proposte dai clienti
        res_val = supabase.table('VALUTAZIONE_USATO').select('*').execute()
        pratiche_raw = res_val.data
        pratiche_completate = []

        for p in pratiche_raw:
            id_usato = p.get("ID_Usato")
            
            # Se la pratica è già stata gestita dal meccanico o chiusa dall'admin, la nascondiamo!
            if id_usato in esclusioni:
                continue

            info_pratica = {
                "ID_Usato": id_usato,
                "Targa": p.get("Targa"),
                "NumeroTelaio": p.get("NumeroTelaio"),
                "Data_Inizio": p.get("Data_Inizio"),
                "ID_Persona": p.get("ID_Persona"),
                "Marca": "N/D",  # Valore di default se non troviamo la marca
                "Modello": "",
                "Km": "N/D"
            }
            
            # Recuperiamo i dettagli del veicolo tramite Telaio
            res_v = supabase.table('VEICOLO').select('*').eq('NumeroTelaio', p.get("NumeroTelaio")).execute()
            if res_v.data:
                veicolo = res_v.data[0]
                info_pratica["Modello"] = veicolo.get("Modello", "")
                info_pratica["Km"] = veicolo.get("Kilometraggio", "N/D")
                
                # ✨ RISOLUZIONE BUG N/D: Recuperiamo il nome testuale della Marca usando l'ID_Marca
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

# =====================================================================
# --- WIZARD USATO FASE 3: APPROVAZIONE FINALE (LATO ADMIN) ---
# =====================================================================
@main.route('/admin/approva_usato', methods=['GET', 'POST'])
@ruolo_richiesto(4)
def approva_usato():
    if request.method == 'POST':
        try:
            id_pratica = int(request.form.get('id_pratica')) 
            prezzo_finale = float(request.form.get('prezzo_finale'))
            decisione = request.form.get('decisione') 
            note_admin = request.form.get('nota_proprietario', 'Approvato da Admin')

            # 1. Aggiorniamo la chiusura della pratica su VALUTAZIONE_USATO
            supabase.table('VALUTAZIONE_USATO').update({
                "Data_Fine": request.form.get('data_approvazione'),
                "Prezzo_Finale": prezzo_finale
            }).eq('ID_Usato', id_pratica).execute()

            # 2. Strutturiamo i dati per la tabella Approvazione_PV
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

    # --- LATO GET (Lettura delle perizie da mostrare all'Admin senza JOIN fallimentari) ---
    try:
        # 0. IL FILTRO INFALLIBILE: Prendiamo tutti gli ID delle pratiche GIÀ VALUTATE dall'Admin
        res_approvate = supabase.table('Approvazione_PV').select('ID_Usato').execute()
        
        # Creiamo una lista semplice in Python con solo i numeri delle pratiche concluse
        pratiche_gia_chiuse = [r['ID_Usato'] for r in res_approvate.data]

        # 1. Prendiamo tutte le perizie tecniche inserite dai meccanici
        res_esiti = supabase.table('Esito_MV').select('*').execute()
        perizie_raw = res_esiti.data
        
        perizie_completate = []
        
        # 2. Per ogni perizia, andiamo a recuperare i dati e FILTRIAMO quelle concluse
        for perizia in perizie_raw:
            id_usato = perizia.get("ID_Usato")
            
            # 🛑 FILTRO MAGICO 2.0: Se questo ID è già nella tabella Approvazione_PV, l'admin ha già deciso. SALTIAMO!
            if id_usato in pratiche_gia_chiuse:
                continue

            id_meccanico = perizia.get("ID_Persona")
            
            # Recuperiamo i dati della VALUTAZIONE_USATO
            res_val = supabase.table('VALUTAZIONE_USATO').select('*').eq('ID_Usato', id_usato).execute()
            
            if res_val.data:
                valutazione = res_val.data[0]
                
                # Se arriviamo qui, la pratica è ancora da approvare. Creiamo lo scheletro:
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
                
                # Recuperiamo il Nome e Cognome del meccanico direttamente da PERSONA
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
        res = supabase.table('VEICOLO').select('*').eq('ID_Persona', id_cliente).execute()
        auto_cliente = res.data
        return render_template('prenotazioni/mie_auto.html', auto=auto_cliente)
    except Exception as e:
        print(f"ERRORE LETTURA AUTO: {e}")
        return redirect('/area_cliente')

# --- AMMINISTRAZIONE: VEDI PRENOTAZIONI IN SOSPESO ---
@main.route('/admin/prenotazioni')
@ruolo_richiesto(4) 
def gestione_prenotazioni():
    try:
        res_pren = supabase.table('PRENOTAZIONE').select('*, PERSONA(Nome, Cognome)').is_('ID_Intervento', 'null').execute()
        prenotazioni_pendenti = res_pren.data

        res_mecc = supabase.table('PERSONA').select('*').in_('Ruolo', [2, 3]).execute()
        meccanici = res_mecc.data

        return render_template('admin/gestione_prenotazioni.html', 
                               prenotazioni=prenotazioni_pendenti, meccanici=meccanici)
    except Exception as e:
        print(f"ERRORE LETTURA PRENOTAZIONI: {e}")
        return redirect('/dashboard_admin')

# --- AMMINISTRAZIONE: ASSEGNA IL LAVORO ---
@main.route('/admin/assegna_lavoro', methods=['POST'])
@ruolo_richiesto(4)
def assegna_lavoro():
    try:
        id_prenotazione = request.form.get('id_prenotazione')
        targa = request.form.get('targa')
        data_inizio = request.form.get('data')
        ora_inizio = request.form.get('ora')
        id_meccanico = request.form.get('id_meccanico')
        nome_compito = request.form.get('nome_compito')
        durata = request.form.get('durata')

        # 1. Inseriamo l'Intervento (senza ID manuale) 
        res_intervento = supabase.table('INTERVENTO').insert({
            "Targa": targa, "ID_Officina": 1, 
            "Data_Inizio": data_inizio, "Orario_Inizio": ora_inizio, 
            "Tipologia_Intervento": "Manutenzione", "Costo": 0, "Note": "Web", 
            "Durata": int(durata), "Km_Veicolo": 0 
        }).execute()

        # 2. Catturiamo l'ID generato automaticamente in tempo reale dall'auto-increment del DB
        id_intervento_db = res_intervento.data[0]['ID_Intervento']

        # 3. Creiamo il record Compito agganciandoci la FK corretta appena ottenuta
        supabase.table('COMPITO').insert({
            "ID_Intervento": id_intervento_db, 
            "ID_Persona": int(id_meccanico), "Nome": nome_compito[:20], 
            "Durata": int(durata), "Data_Inizio": data_inizio, "Stato": "Da fare"
        }).execute()

        # 4. Aggiorniamo lo stato della prenotazione legando l'intervento generato
        supabase.table('PRENOTAZIONE').update({"ID_Intervento": id_intervento_db}).eq('ID_Prenotazione', id_prenotazione).execute()
        
        flash("Lavoro assegnato con successo!", "success")
    except Exception as e:
        print(f"ERRORE ASSEGNAZIONE: {e}")
        flash("Errore durante l'assegnazione.", "danger")
    return redirect('/admin/prenotazioni')