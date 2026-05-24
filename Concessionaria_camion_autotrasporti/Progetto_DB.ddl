-- *********************************************
-- * Standard SQL generation                   
-- *--------------------------------------------
-- * DB-MAIN version: 11.0.2              
-- * Generator date: Sep 14 2021              
-- * Generation date: Sun May 24 09:18:06 2026 
-- * LUN file: D:\Progetto_Database\Schema_ER\Progetto_DB.lun 
-- * Schema: Concessionaria_logistica_e_autotrasporti_Trad_SQL/SQL 
-- ********************************************* 


-- Database Section
-- ________________ 

create database Concessionaria_logistica_e_autotrasporti_Trad_SQL;


-- DBSpace Section
-- _______________


-- Tables Section
-- _____________ 

create table Approvazione_PV (
     ID_Usato numeric(5) not null,
     Nota_Proprietario varchar(500) not null,
     Stato_Decisione char not null,
     ID_Persona numeric(10) not null,
     constraint ID_Appro_VALUT_ID primary key (ID_Usato));

create table ARCHIVIO (
     Tipologia_Archivio varchar(25) not null,
     ID_Archivio numeric(5) not null,
     constraint ID_ARCHIVIO_ID primary key (ID_Archivio));

create table BLOCCO (
     Data_Fine date,
     Data_Inizio date not null,
     ID_Blocco numeric(10) not null,
     Motivo varchar(100) not null,
     constraint ID_BLOCCO_ID primary key (ID_Blocco));

create table CLIENTE (
     ID_Persona numeric(10) not null,
     constraint ID_CLIEN_PERSO_ID primary key (ID_Persona));

create table COMPITO (
     ID_Compito numeric(50) not null,
     ID_Intervento numeric(50) not null,
     ID_Persona numeric(10) not null,
     Nome varchar(20) not null,
     Durata numeric(3) not null,
     Data_Inizio date not null,
     constraint ID_COMPITO_ID primary key (ID_Compito));

create table Comprende_VO (
     NumeroTelaio varchar(17) not null,
     ID_Optional numeric(10) not null,
     constraint ID_Comprende_VO_ID primary key (ID_Optional, NumeroTelaio));

create table CONCESSIONARIA (
     ID_Concessionario numeric(5) not null,
     Nome varchar(50) not null,
     Data_Apertura date not null,
     ID_Persona numeric(10) not null,
     constraint ID_CONCESSIONARIA_ID primary key (ID_Concessionario));

create table CONTRATTO (
     Tipo_Contratto varchar(14) not null,
     Stato varchar(20) not null,
     Data_Decorrenza date not null,
     Note_Legali varchar(1000) not null,
     Data_Scadenza date not null,
     Importo_Totale numeric(10,2) not null,
     Data_Stipula date not null,
     ID_Contratto numeric(10) not null,
     ID_Preventivo numeric(10),
     ID_Persona numeric(10),
     ID_Pagamento numeric(10),
     constraint ID_CONTRATTO_ID primary key (ID_Contratto),
     constraint SID_CONTR_PREVE_ID unique (ID_Preventivo));

create table Esito_MV (
     ID_Usato numeric(5) not null,
     Descrizione varchar(500) not null,
     Esito_Meccanico char not null,
     Prezzo_Consigliato numeric(6,2) not null,
     ID_Persona numeric(10) not null,
     constraint ID_Esito_MV_ID primary key (ID_Usato, ID_Persona));

create table Evento_Archivio (
     Ora_Rimozione varchar(5) not null,
     Data_Rimozione date not null,
     ID_Evento_Archiviazione numeric(7) not null,
     Ora_Inserimento varchar(5) not null,
     Data_Inserimento date not null,
     Motivo char(1) not null,
     ID_Archivio numeric(5) not null,
     NumeroTelaio varchar(17) not null,
     constraint ID_Evento_Archivio_ID primary key (ID_Evento_Archiviazione));

create table FINANZIAMENTO (
     ID_Contratto numeric(10) not null,
     Assicurazione_Credito numeric(10) not null,
     Spese_Apertura_Pratica numeric(10,2) not null,
     Anticipo numeric(10,2) not null,
     TAEG float(3) not null,
     TAN float(3) not null,
     constraint ID_FINAN_CONTR_ID primary key (ID_Contratto));

create table GRUPPO (
     ID_Gruppo numeric(5) not null,
     Indirizzo varchar(50) not null,
     ID_Ufficio numeric(5) not null,
     constraint ID_GRUPPO_ID primary key (ID_Gruppo));

create table ID_Orario (
     ID_Sede numeric(5) not null,
     ID_Orario numeric(1) not null,
     constraint ID_ID_Orario_ID primary key (ID_Sede, ID_Orario));

create table IMPIEGATO (
     ID_Persona numeric(10) not null,
     Tipologia_Lavoro varchar(20) not null,
     ID_Ufficio numeric(5) not null,
     constraint ID_IMPIE_LAVOR_ID primary key (ID_Persona));

create table INTERVENTO (
     Km_Veicolo numeric(15) not null,
     ID_Intervento numeric(50) not null,
     Targa varchar(20) not null,
     ID_Officina numeric(5) not null,
     Data_Inizio date not null,
     Orario_Inizio varchar(10) not null,
     Tipologia_Intervento varchar(20) not null,
     Costo numeric(10) not null,
     Note varchar(100) not null,
     Durata numeric(10) not null,
     Data_Fine date,
     constraint ID_INTERVENTO_ID primary key (ID_Intervento));

create table Lavora (
     ID_Assegnazione_Lavoro numeric(7) not null,
     ID_Persona numeric(10) not null,
     Data_Rimozione date not null,
     Data_Inserimento date not null,
     Motivo char(1) not null,
     Orario_Inizio varchar(5) not null,
     Orario_Fine varchar(5) not null,
     ID_Officina numeric(5) not null,
     constraint ID_Lavora_ID primary key (ID_Assegnazione_Lavoro));

create table LAVORATORE (
     ID_Persona numeric(10) not null,
     Livello numeric(1),
     Data_Assunzione date not null,
     Paga_Mensile numeric(8,2) not null,
     constraint ID_LAVOR_PERSO_ID primary key (ID_Persona));

create table LEASING (
     ID_Contratto numeric(10) not null,
     ID_Leasing numeric(10) not null,
     Importo_Mensile numeric(10) not null,
     Data_Fine date not null,
     Data_Inizio date not null,
     Maxi_Canone numeric(3) not null,
     P_IVA_Societa varchar(11) not null,
     Prezzo_Riscatto numeric(10) not null,
     constraint SID_LEASING_ID unique (ID_Leasing),
     constraint ID_LEASI_CONTR_ID primary key (ID_Contratto));

create table MARCA (
     Attiva char not null,
     Nome varchar(50) not null,
     ID_Marca numeric(10) not null,
     constraint ID_MARCA_ID primary key (ID_Marca));

create table MECCANICO (
     ID_Persona numeric(10) not null,
     Trasferte_Esterne numeric(10) not null,
     Totale_interventi numeric(10) not null,
     constraint ID_MECCA_LAVOR_ID primary key (ID_Persona));

create table METODO_PAGAMENTO (
     ID_Pagamento numeric(10) not null,
     Circuito varchar(100) not null,
     Intestatario varchar(100) not null,
     Tipologia varchar(25) not null,
     Iban char(34) not null,
     constraint ID_METODO_PAGAMENTO_ID primary key (ID_Pagamento));

create table NOLEGGIO (
     ID_Contratto numeric(10) not null,
     Data_Fine date not null,
     Data_Inizio date not null,
     Franchigia_assicurativa numeric(10,2) not null,
     Prezzo_km numeric(5) not null,
     Km_totali numeric(15) not null,
     constraint ID_NOLEG_CONTR_ID primary key (ID_Contratto),
     constraint CHK_NOLEG_DATE check (Data_Fine > Data_Inizio));

create table OFFICINA (
     ID_Officina numeric(5) not null,
     ID_Persona numeric(10) not null,
     ID_Sede numeric(5) not null,
     Interna char not null,
     Nome varchar(50) not null,
     Indirizzo varchar(50),
     constraint ID_OFFICINA_ID primary key (ID_Officina),
     constraint SID_OFFIC_LAVOR_ID unique (ID_Persona));

create table OPTIONAL (
     Nome varchar(50) not null,
     Prezzo numeric(7) not null,
     Note varchar(1000) not null,
     Tipologia_Optional varchar(25) not null,
     ID_Optional numeric(10) not null,
     constraint ID_OPTIONAL_ID primary key (ID_Optional));

create table ORARIO_SEDE (
     Orario_Chiusura_Pomeriggio varchar(5) not null,
     Orario_Chiusura_Mattina varchar(5) not null,
     Orario_Apertura_Pomeriggio varchar(5) not null,
     Orario_Apertura_Mattina varchar(5) not null,
     ID_Orario numeric(1) not null,
     constraint ID_ORARIO_SEDE_ID primary key (ID_Orario));

create table Permuta_PV (
     ID_Preventivo numeric(10) not null,
     ID_Usato numeric(5) not null,
     ValoreApplicato numeric(6,2) not null,
     constraint ID_Permu_PREVE_ID primary key (ID_Preventivo),
     constraint SID_Permu_VALUT_ID unique (ID_Usato));

create table PERSONA (
     Telefono varchar(20) not null,
     Mail varchar(50) not null,
     Password varchar(255) not null,
     Numero_Passaporto varchar(9),
     Ruolo numeric(1) not null,
     CF varchar(16),
     ID_Persona numeric(10) not null,
     Nome varchar(20) not null,
     Cognome varchar(30) not null,
     Residenza varchar(50) not null,
     ID_Blocco numeric(10),
     constraint ID_PERSONA_ID primary key (ID_Persona));

create table PRENOTAZIONE (
     Nota_Cliente varchar(100) not null,
     Data_Prenotazione date not null,
     Ora_Incontro varchar(5) not null,
     ID_Prenotazione numeric(10) not null,
     ID_Intervento numeric(50),
     Targa varchar(20) not null,
     ID_Persona numeric(10) not null,
     ID_Sede numeric(5) not null,
     NumeroTelaio varchar(17) not null,
     constraint ID_PRENOTAZIONE_ID primary key (ID_Prenotazione));

create table PREVENTIVO (
     ID_Preventivo numeric(10) not null,
     Stato_PreventivoChiuso char not null,
     Durata_Massima numeric(3) not null,
     Note varchar(10000) not null,
     Acconto numeric(6,2),
     NumeroTelaio varchar(17) not null,
     ID_Persona numeric(10) not null,
     Pos_ID_Persona numeric(10) not null,
     constraint ID_PREVENTIVO_ID primary key (ID_Preventivo));

create table PROPRIETARIO (
     ID_Persona numeric(10) not null,
     P_IVA varchar(11) not null,
     constraint ID_PROPR_LAVOR_ID primary key (ID_Persona));

create table RATE (
     ID_Contratto numeric(10) not null,
     Numero_Rata numeric(10) not null,
     Importo_Mensile numeric(10) not null,
     Data_Pagamento_Effettivo date not null,
     Stato_Pagamento char not null,
     Frequenza_Addebito varchar(15) not null,
     constraint ID_RATE_CONTR_ID primary key (ID_Contratto, Numero_Rata));

create table REPARTO (
     Mail varchar(100) not null,
     Telefono varchar(20) not null,
     Nome varchar(50) not null,
     Acronimo varchar(5) not null,
     ID_Reparto numeric(5) not null,
     ID_Persona numeric(10),
     ID_Gruppo numeric(5) not null,
     constraint ID_REPARTO_ID primary key (Acronimo, ID_Reparto),
     constraint SID_REPAR_LAVOR_ID unique (ID_Persona));

create table SEDE (
     Telefono varchar(20) not null,
     Mail varchar(50) not null,
     ID_Sede numeric(5) not null,
     Data_Apertura date not null,
     Stato_Servizio char not null,
     Denominazione varchar(20) not null,
     Indirizzo varchar(50) not null,
     ID_Concessionario numeric(5) not null,
     constraint ID_SEDE_ID primary key (ID_Sede));

create table SETTORE (
     ID_Settore numeric(5) not null,
     ID_Officina numeric(5) not null,
     Cod_Settore char(1) not null,
     Nome varchar(20) not null,
     Descrizione varchar(100) not null,
     ID_Persona numeric(10),
     constraint ID_SETTORE_ID primary key (ID_Settore));

create table SLOT_ORARIO (
     Ora_Fine varchar(5) not null,
     Ora_Inizio varchar(5) not null,
     ID_Slot numeric(10) not null,
     constraint ID_SLOT_ORARIO_ID primary key (ID_Slot));

create table Specializzato_MO (
     ID_Persona numeric(10) not null,
     ID_Settore numeric(5) not null,
     constraint ID_Specializzato_MO_ID primary key (ID_Settore, ID_Persona));

create table STRUMENTO (
     ID_Strumento numeric(5) not null,
     Nome varchar(20) not null,
     Note varchar(100) not null,
     ID_Officina numeric(5) not null,
     constraint ID_STRUMENTO_ID primary key (ID_Strumento));

create table TEST_DRIVE (
     ID_TestDrive numeric(10) not null,
     Data date not null,
     ID_Slot numeric(10) not null,
     ID_Persona numeric(10) not null,
     Sup_ID_Persona numeric(10) not null,
     constraint ID_TEST_DRIVE_ID primary key (ID_TestDrive));

create table UFFICIO (
     ID_Ufficio numeric(5) not null,
     Funzione varchar(50) not null,
     Piano numeric(3) not null,
     ID_Sede numeric(5) not null,
     constraint ID_UFFICIO_ID primary key (ID_Ufficio));

create table Usa_SS (
     ID_Settore numeric(5) not null,
     ID_Strumento numeric(5) not null,
     constraint ID_Usa_SS_ID primary key (ID_Settore, ID_Strumento));

create table Utilizzo_TV (
     NumeroTelaio varchar(17) not null,
     ID_TestDrive numeric(10) not null,
     constraint ID_Utilizzo_TV_ID primary key (NumeroTelaio, ID_TestDrive));

create table VALUTAZIONE_USATO (
     ID_Usato numeric(5) not null,
     NumeroTelaio varchar(17) not null,
     Targa varchar(20) not null,
     Data_Inizio date not null,
     Data_Fine date not null,
     Prezzo_Finale numeric(6,2) not null,
     ID_Persona numeric(10) not null,
     constraint ID_VALUTAZIONE_USATO_ID primary key (ID_Usato),
     constraint SID_VALUT_VEICO_ID unique (NumeroTelaio));

create table VEICOLO (
     Kilometraggio numeric(15),
     Anno_Produzione numeric(4) not null,
     Targa varchar(20) not null,
     Data_Arrivo_Concessionaria date not null,
     Classe_Inquinamento varchar(6) not null,
     Configurazione_Assi varchar(3) not null,
     Numero_Assi numeric(1) not null,
     NumeroTelaio varchar(17) not null,
     Tipologia_Motrice varchar(15) not null,
     Peso numeric(8,2) not null,
     Descrizione varchar(100) not null,
     Prezzo_Base numeric(10,2) not null,
     Data_Immatricolazione date not null,
     Potenza_CV numeric(4) not null,
     Stato_Disponibilita char not null,
     Modello varchar(15) not null,
     ID_Marca numeric(10) not null,
     ID_Contratto numeric(10),
     constraint ID_VEICOLO_ID primary key (NumeroTelaio));

create table VENDITA (
     ID_Vendita numeric(10) not null,
     ID_Contratto numeric(10) not null,
     Stato char not null,
     Data_Vendita date not null,
     Ora_Vendita varchar(5) not null,
     ID_Persona numeric(10) not null,
     constraint ID_VENDITA_ID primary key (ID_Vendita),
     constraint SID_VENDI_CONTR_ID unique (ID_Contratto));

create table VENDITA_TOTALE (
     ID_Contratto numeric(10) not null,
     Consegna_Effettivo_Veicolo date not null,
     Data_Saldo_Effettivo date not null,
     Sconto_Pronto_Pagamento numeric(3) not null,
     constraint ID_VENDI_CONTR_ID primary key (ID_Contratto));

create table VENDITORE (
     ID_Persona numeric(10) not null,
     Bonus_Vendite numeric(6) not null,
     ID_Ufficio numeric(5) not null,
     constraint ID_VENDI_LAVOR_ID primary key (ID_Persona));


-- Constraints Section
-- ___________________ 

alter table Approvazione_PV add constraint ID_Appro_VALUT_FK
     foreign key (ID_Usato)
     references VALUTAZIONE_USATO;

alter table Approvazione_PV add constraint REF_Appro_PROPR_FK
     foreign key (ID_Persona)
     references PROPRIETARIO;

alter table CLIENTE add constraint ID_CLIEN_PERSO_FK
     foreign key (ID_Persona)
     references PERSONA;

alter table COMPITO add constraint REF_COMPI_INTER_FK
     foreign key (ID_Intervento)
     references INTERVENTO;

alter table COMPITO add constraint REF_COMPI_MECCA_FK
     foreign key (ID_Persona)
     references MECCANICO;

alter table Comprende_VO add constraint REF_Compr_OPTIO
     foreign key (ID_Optional)
     references OPTIONAL;

alter table Comprende_VO add constraint REF_Compr_VEICO_FK
     foreign key (NumeroTelaio)
     references VEICOLO;

alter table CONCESSIONARIA add constraint REF_CONCE_PROPR_FK
     foreign key (ID_Persona)
     references PROPRIETARIO;

alter table CONTRATTO add constraint SID_CONTR_PREVE_FK
     foreign key (ID_Preventivo)
     references PREVENTIVO;

alter table CONTRATTO add constraint REF_CONTR_CLIEN_FK
     foreign key (ID_Persona)
     references CLIENTE;

alter table CONTRATTO add constraint REF_CONTR_METOD_FK
     foreign key (ID_Pagamento)
     references METODO_PAGAMENTO;

alter table Esito_MV add constraint ID_Esito_VALUT_FK
     foreign key (ID_Usato)
     references VALUTAZIONE_USATO;

alter table Esito_MV add constraint REF_Esito_MECCA_FK
     foreign key (ID_Persona)
     references MECCANICO;

alter table Evento_Archivio add constraint REF_Event_ARCHI_FK
     foreign key (ID_Archivio)
     references ARCHIVIO;

alter table Evento_Archivio add constraint REF_Event_VEICO_FK
     foreign key (NumeroTelaio)
     references VEICOLO;

alter table FINANZIAMENTO add constraint ID_FINAN_CONTR_FK
     foreign key (ID_Contratto)
     references CONTRATTO;

alter table GRUPPO add constraint REF_GRUPP_UFFIC_FK
     foreign key (ID_Ufficio)
     references UFFICIO;

alter table ID_Orario add constraint REF_ID_Or_ORARI_FK
     foreign key (ID_Orario)
     references ORARIO_SEDE;

alter table ID_Orario add constraint FKSED_ID_
     foreign key (ID_Sede)
     references SEDE;

alter table IMPIEGATO add constraint ID_IMPIE_LAVOR_FK
     foreign key (ID_Persona)
     references LAVORATORE;

alter table IMPIEGATO add constraint REF_IMPIE_UFFIC_FK
     foreign key (ID_Ufficio)
     references UFFICIO;

alter table INTERVENTO add constraint REF_INTER_OFFIC_FK
     foreign key (ID_Officina)
     references OFFICINA;

alter table Lavora add constraint REF_Lavor_OFFIC_FK
     foreign key (ID_Officina)
     references OFFICINA;

alter table Lavora add constraint SID_Lavor_MECCA_FK
     foreign key (ID_Persona)
     references MECCANICO;

alter table LAVORATORE add constraint ID_LAVOR_PERSO_FK
     foreign key (ID_Persona)
     references PERSONA;

alter table LEASING add constraint ID_LEASI_CONTR_FK
     foreign key (ID_Contratto)
     references CONTRATTO;

alter table MECCANICO add constraint ID_MECCA_LAVOR_FK
     foreign key (ID_Persona)
     references LAVORATORE;

alter table NOLEGGIO add constraint ID_NOLEG_CONTR_FK
     foreign key (ID_Contratto)
     references CONTRATTO;

alter table OFFICINA add constraint REF_OFFIC_SEDE_FK
     foreign key (ID_Sede)
     references SEDE;

alter table OFFICINA add constraint SID_OFFIC_LAVOR_FK
     foreign key (ID_Persona)
     references LAVORATORE;

alter table Permuta_PV add constraint ID_Permu_PREVE_FK
     foreign key (ID_Preventivo)
     references PREVENTIVO;

alter table Permuta_PV add constraint SID_Permu_VALUT_FK
     foreign key (ID_Usato)
     references VALUTAZIONE_USATO;

alter table PERSONA add constraint REF_PERSO_BLOCC_FK
     foreign key (ID_Blocco)
     references BLOCCO;

alter table PRENOTAZIONE add constraint REF_PRENO_INTER_FK
     foreign key (ID_Intervento)
     references INTERVENTO;

alter table PRENOTAZIONE add constraint REF_PRENO_CLIEN_FK
     foreign key (ID_Persona)
     references CLIENTE;

alter table PRENOTAZIONE add constraint REF_PRENO_SEDE_FK
     foreign key (ID_Sede)
     references SEDE;

alter table PRENOTAZIONE add constraint REF_PRENO_VEICO_FK
     foreign key (NumeroTelaio)
     references VEICOLO;

alter table PREVENTIVO add constraint REF_PREVE_VEICO_FK
     foreign key (NumeroTelaio)
     references VEICOLO;

alter table PREVENTIVO add constraint REF_PREVE_VENDI_FK
     foreign key (ID_Persona)
     references VENDITORE;

alter table PREVENTIVO add constraint REF_PREVE_CLIEN_FK
     foreign key (Pos_ID_Persona)
     references CLIENTE;

alter table PROPRIETARIO add constraint ID_PROPR_LAVOR_FK
     foreign key (ID_Persona)
     references LAVORATORE;

alter table RATE add constraint ID_RATE_CONTR_FK
     foreign key (ID_Contratto)
     references CONTRATTO;

alter table REPARTO add constraint REF_REPAR_GRUPP_FK
     foreign key (ID_Gruppo)
     references GRUPPO;

alter table REPARTO add constraint SID_REPAR_LAVOR_FK
     foreign key (ID_Persona)
     references LAVORATORE;

alter table SEDE add constraint REF_SEDE_CONCE_FK
     foreign key (ID_Concessionario)
     references CONCESSIONARIA;

alter table SETTORE add constraint REF_SETTO_OFFIC_FK
     foreign key (ID_Officina)
     references OFFICINA;

alter table SETTORE add constraint REF_SETTO_MECCA_FK
     foreign key (ID_Persona)
     references MECCANICO;

alter table Specializzato_MO add constraint REF_Speci_SETTO
     foreign key (ID_Settore)
     references SETTORE;

alter table Specializzato_MO add constraint REF_Speci_MECCA_FK
     foreign key (ID_Persona)
     references MECCANICO;

alter table STRUMENTO add constraint REF_STRUM_OFFIC_FK
     foreign key (ID_Officina)
     references OFFICINA;

alter table TEST_DRIVE add constraint REF_TEST__SLOT__FK
     foreign key (ID_Slot)
     references SLOT_ORARIO;

alter table TEST_DRIVE add constraint REF_TEST__CLIEN_FK
     foreign key (ID_Persona)
     references CLIENTE;

alter table TEST_DRIVE add constraint REF_TEST__VENDI_FK
     foreign key (Sup_ID_Persona)
     references VENDITORE;

alter table UFFICIO add constraint REF_UFFIC_SEDE_FK
     foreign key (ID_Sede)
     references SEDE;

alter table Usa_SS add constraint REF_Usa_S_STRUM_FK
     foreign key (ID_Strumento)
     references STRUMENTO;

alter table Usa_SS add constraint REF_Usa_S_SETTO
     foreign key (ID_Settore)
     references SETTORE;

alter table Utilizzo_TV add constraint REF_Utili_TEST__FK
     foreign key (ID_TestDrive)
     references TEST_DRIVE;

alter table Utilizzo_TV add constraint REF_Utili_VEICO
     foreign key (NumeroTelaio)
     references VEICOLO;

alter table VALUTAZIONE_USATO add constraint SID_VALUT_VEICO_FK
     foreign key (NumeroTelaio)
     references VEICOLO;

alter table VALUTAZIONE_USATO add constraint REF_VALUT_CLIEN_FK
     foreign key (ID_Persona)
     references CLIENTE;

alter table VEICOLO add constraint REF_VEICO_MARCA_FK
     foreign key (ID_Marca)
     references MARCA;

alter table VEICOLO add constraint REF_VEICO_CONTR_FK
     foreign key (ID_Contratto)
     references CONTRATTO;

alter table VENDITA add constraint SID_VENDI_CONTR_FK
     foreign key (ID_Contratto)
     references CONTRATTO;

alter table VENDITA add constraint REF_VENDI_VENDI_FK
     foreign key (ID_Persona)
     references VENDITORE;

alter table VENDITA_TOTALE add constraint ID_VENDI_CONTR_FK
     foreign key (ID_Contratto)
     references CONTRATTO;

alter table VENDITORE add constraint ID_VENDI_LAVOR_FK
     foreign key (ID_Persona)
     references LAVORATORE;

alter table VENDITORE add constraint REF_VENDI_UFFIC_FK
     foreign key (ID_Ufficio)
     references UFFICIO;


-- Index Section
-- _____________ 

create unique index ID_Appro_VALUT_IND
     on Approvazione_PV (ID_Usato);

create index REF_Appro_PROPR_IND
     on Approvazione_PV (ID_Persona);

create unique index ID_ARCHIVIO_IND
     on ARCHIVIO (ID_Archivio);

create unique index ID_BLOCCO_IND
     on BLOCCO (ID_Blocco);

create unique index ID_CLIEN_PERSO_IND
     on CLIENTE (ID_Persona);

create unique index ID_COMPITO_IND
     on COMPITO (ID_Compito);

create index REF_COMPI_INTER_IND
     on COMPITO (ID_Intervento);

create index REF_COMPI_MECCA_IND
     on COMPITO (ID_Persona);

create unique index ID_Comprende_VO_IND
     on Comprende_VO (ID_Optional, NumeroTelaio);

create index REF_Compr_VEICO_IND
     on Comprende_VO (NumeroTelaio);

create unique index ID_CONCESSIONARIA_IND
     on CONCESSIONARIA (ID_Concessionario);

create index REF_CONCE_PROPR_IND
     on CONCESSIONARIA (ID_Persona);

create unique index ID_CONTRATTO_IND
     on CONTRATTO (ID_Contratto);

create unique index SID_CONTR_PREVE_IND
     on CONTRATTO (ID_Preventivo);

create index REF_CONTR_CLIEN_IND
     on CONTRATTO (ID_Persona);

create index REF_Esito_VALUT_IND
     on Esito_MV (ID_Usato);

create index REF_CONTR_METOD_IND
     on CONTRATTO (ID_Pagamento);

create index REF_Esito_MECCA_IND
     on Esito_MV (ID_Persona);

create unique index ID_Evento_Archivio_IND
     on Evento_Archivio (ID_Evento_Archiviazione);

create index REF_Event_ARCHI_IND
     on Evento_Archivio (ID_Archivio);

create index REF_Event_VEICO_IND
     on Evento_Archivio (NumeroTelaio);

create unique index ID_FINAN_CONTR_IND
     on FINANZIAMENTO (ID_Contratto);

create unique index ID_GRUPPO_IND
     on GRUPPO (ID_Gruppo);

create index REF_GRUPP_UFFIC_IND
     on GRUPPO (ID_Ufficio);

create unique index ID_ID_Orario_IND
     on ID_Orario (ID_Sede, ID_Orario);

create index REF_ID_Or_ORARI_IND
     on ID_Orario (ID_Orario);

create unique index ID_IMPIE_LAVOR_IND
     on IMPIEGATO (ID_Persona);

create index REF_IMPIE_UFFIC_IND
     on IMPIEGATO (ID_Ufficio);

create unique index ID_INTERVENTO_IND
     on INTERVENTO (ID_Intervento);

create index REF_INTER_OFFIC_IND
     on INTERVENTO (ID_Officina);

create unique index ID_Lavora_IND
     on Lavora (ID_Assegnazione_Lavoro);

create index REF_Lavor_OFFIC_IND
     on Lavora (ID_Officina);

create unique index ID_LAVOR_PERSO_IND
     on LAVORATORE (ID_Persona);

create unique index SID_LEASING_IND
     on LEASING (ID_Leasing);

create unique index ID_LEASI_CONTR_IND
     on LEASING (ID_Contratto);

create unique index ID_MARCA_IND
     on MARCA (ID_Marca);

create unique index ID_MECCA_LAVOR_IND
     on MECCANICO (ID_Persona);

create unique index ID_METODO_PAGAMENTO_IND
     on METODO_PAGAMENTO (ID_Pagamento);

create index IDX_NOLEGGIO_DATE 
     on NOLEGGIO (Data_Inizio, Data_Fine);

create unique index ID_NOLEG_CONTR_IND
     on NOLEGGIO (ID_Contratto);

create unique index ID_OFFICINA_IND
     on OFFICINA (ID_Officina);

create index REF_OFFIC_SEDE_IND
     on OFFICINA (ID_Sede);

create unique index SID_OFFIC_LAVOR_IND
     on OFFICINA (ID_Persona);

create unique index ID_OPTIONAL_IND
     on OPTIONAL (ID_Optional);

create unique index ID_ORARIO_SEDE_IND
     on ORARIO_SEDE (ID_Orario);

create unique index ID_Permu_PREVE_IND
     on Permuta_PV (ID_Preventivo);

create unique index SID_Permu_VALUT_IND
     on Permuta_PV (ID_Usato);

create unique index ID_PERSONA_IND
     on PERSONA (ID_Persona);

create index REF_PERSO_BLOCC_IND
     on PERSONA (ID_Blocco);

create unique index ID_PRENOTAZIONE_IND
     on PRENOTAZIONE (ID_Prenotazione);

create index REF_PRENO_INTER_IND
     on PRENOTAZIONE (ID_Intervento);

create index REF_PRENO_CLIEN_IND
     on PRENOTAZIONE (ID_Persona);

create index REF_PRENO_SEDE_IND
     on PRENOTAZIONE (ID_Sede);

create index REF_PRENO_VEICO_IND
     on PRENOTAZIONE (NumeroTelaio);

create unique index ID_PREVENTIVO_IND
     on PREVENTIVO (ID_Preventivo);

create index REF_PREVE_VEICO_IND
     on PREVENTIVO (NumeroTelaio);

create index REF_PREVE_VENDI_IND
     on PREVENTIVO (ID_Persona);

create index REF_PREVE_CLIEN_IND
     on PREVENTIVO (Pos_ID_Persona);

create unique index ID_PROPR_LAVOR_IND
     on PROPRIETARIO (ID_Persona);

create index IDX_RATE_CONTRATTO on RATE (ID_Contratto);

create unique index ID_REPARTO_IND
     on REPARTO (Acronimo, ID_Reparto);

create index REF_REPAR_GRUPP_IND
     on REPARTO (ID_Gruppo);

create unique index SID_REPAR_LAVOR_IND
     on REPARTO (ID_Persona);

create unique index ID_SEDE_IND
     on SEDE (ID_Sede);

create index REF_SEDE_CONCE_IND
     on SEDE (ID_Concessionario);

create unique index ID_SETTORE_IND
     on SETTORE (ID_Settore);

create index REF_SETTO_OFFIC_IND
     on SETTORE (ID_Officina);

create index REF_SETTO_MECCA_IND
     on SETTORE (ID_Persona);

create unique index ID_SLOT_ORARIO_IND
     on SLOT_ORARIO (ID_Slot);

create unique index ID_Specializzato_MO_IND
     on Specializzato_MO (ID_Settore, ID_Persona);

create index REF_Speci_MECCA_IND
     on Specializzato_MO (ID_Persona);

create unique index ID_STRUMENTO_IND
     on STRUMENTO (ID_Strumento);

create index REF_STRUM_OFFIC_IND
     on STRUMENTO (ID_Officina);

create unique index ID_TEST_DRIVE_IND
     on TEST_DRIVE (ID_TestDrive);

create index REF_TEST__SLOT__IND
     on TEST_DRIVE (ID_Slot);

create index REF_TEST__CLIEN_IND
     on TEST_DRIVE (ID_Persona);

create index REF_TEST__VENDI_IND
     on TEST_DRIVE (Sup_ID_Persona);

create unique index ID_UFFICIO_IND
     on UFFICIO (ID_Ufficio);

create index REF_UFFIC_SEDE_IND
     on UFFICIO (ID_Sede);

create unique index ID_Usa_SS_IND
     on Usa_SS (ID_Settore, ID_Strumento);

create index REF_Usa_S_STRUM_IND
     on Usa_SS (ID_Strumento);

create unique index ID_Utilizzo_TV_IND
     on Utilizzo_TV (NumeroTelaio, ID_TestDrive);

create index REF_Utili_TEST__IND
     on Utilizzo_TV (ID_TestDrive);

create unique index ID_VALUTAZIONE_USATO_IND
     on VALUTAZIONE_USATO (ID_Usato);

create unique index SID_VALUT_VEICO_IND
     on VALUTAZIONE_USATO (NumeroTelaio);

create index REF_VALUT_CLIEN_IND
     on VALUTAZIONE_USATO (ID_Persona);

create index REF_VEICO_MARCA_IND
     on VEICOLO (ID_Marca);

create unique index ID_VEICOLO_IND
     on VEICOLO (NumeroTelaio);

create index REF_VEICO_CONTR_IND
     on VEICOLO (ID_Contratto);

create unique index ID_VENDITA_IND
     on VENDITA (ID_Vendita);

create unique index SID_VENDI_CONTR_IND
     on VENDITA (ID_Contratto);

create index REF_VENDI_VENDI_IND
     on VENDITA (ID_Persona);

create unique index ID_VENDI_CONTR_IND
     on VENDITA_TOTALE (ID_Contratto);

create unique index ID_VENDI_LAVOR_IND
     on VENDITORE (ID_Persona);

create index REF_VENDI_UFFIC_IND
     on VENDITORE (ID_Ufficio);

