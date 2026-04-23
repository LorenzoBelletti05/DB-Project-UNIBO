-- *********************************************
-- * Standard SQL generation                   
-- *--------------------------------------------
-- * DB-MAIN version: 11.0.2              
-- * Generator date: Sep 14 2021              
-- * Generation date: Wed Apr 22 19:46:15 2026 
-- * LUN file: D:\Progetto_Database\Schema_ER\Progetto_DB.lun 
-- * Schema: Copy_Concessionaria_logistica_e_autotrasporti/SQL 
-- ********************************************* 


-- Database Section
-- ________________ 

create database Copy_Concessionaria_logistica_e_autotrasporti;


-- DBSpace Section
-- _______________


-- Tables Section
-- _____________ 

create table Approvazione (
     CF varchar(16) not null,
     ID_Persona numeric(10) not null,
     Nota_Proprietario varchar(500) not null,
     Stato_Decisione char not null,
     ID_Usato varchar(50) not null,
     constraint FKApp_PRO_ID primary key (CF, ID_Persona));

create table ARCHIVIO (
     ID_ARC -- Sequence attribute not implemented -- not null,
     Data_Inserimento char(1) not null,
     Ora_Inserimento char(1) not null,
     Motivo_Inserimento char(1) not null,
     constraint ID_ID primary key (ID_ARC));

create table BLOCCO (
     Durata varchar(5) not null,
     Data_Inizio_Blocco date not null,
     Motivo varchar(100) not null);

create table CLIENTE (
     CF varchar(16) not null,
     ID_Persona numeric(10) not null,
     constraint FKPER_CLI_ID primary key (CF, ID_Persona));

create table Codice_Settore (
     CF varchar(16) not null,
     ID_Persona numeric(10) not null,
     Codice_Settore numeric(2) not null,
     constraint ID_Codice_Settore_ID primary key (CF, ID_Persona, Codice_Settore));

create table Compito (
     CF varchar(16) not null,
     ID_Persona numeric(10) not null,
     ID_Compito numeric(10) not null,
     ID_Intervento varchar(20) not null,
     Nome varchar(20) not null,
     Durata numeric(3) not null,
     Data_Inizio date not null,
     constraint ID_Compito_ID primary key (CF, ID_Persona, ID_Compito),
     constraint SID_Compito_ID unique (ID_Intervento, ID_Compito));

create table Comprende1 (
     ID_Optional numeric(10) not null,
     ID_Veicolo numeric(10) not null,
     constraint ID_Comprende1_ID primary key (ID_Optional, ID_Veicolo));

create table CONCESSIONARIO (
     ID_Concessionario numeric(5) not null,
     Nome varchar(50) not null,
     Data_Apertura date not null,
     CF varchar(16) not null,
     ID_Persona numeric(10) not null,
     constraint ID_CONCESSIONARIO_ID primary key (ID_Concessionario));

create table CONTRATTO (
     Sta_Bozza char(1) not null,
     Sta_Rifiutato char(1) not null,
     Sta_Accettato char(1) not null,
     Sta_Iniziato char(1) not null,
     Data_Decorrenza date not null,
     Note_Legali char(99999) not null,
     Data_Scadenza date not null,
     Importo_Totale float(1) not null,
     Data_Stipula date not null,
     ID_Contratto -- Sequence attribute not implemented -- not null,
     ID_Preventivo numeric(10) not null,
     ID_MET numeric(10) not null,
     VENDITA_TOTALE numeric(10),
     RATE numeric(10),
     NOLEGGIO numeric(10),
     LEASING numeric(10),
     FINANZIAMENTO numeric(10),
     constraint ID_CONTRATTO_ID primary key (ID_Contratto),
     constraint SID_CONTRATTO_ID unique (ID_MET, ID_Contratto),
     constraint FKComprende__ID unique (ID_Preventivo));

create table Esito (
     CF varchar(16) not null,
     ID_Persona numeric(10) not null,
     Descrizione varchar(500) not null,
     Esito_Meccanico char not null,
     Prezzo_Consigliato numeric(6,2) not null,
     ID_Usato varchar(50) not null,
     constraint FKEsi_MEC_ID primary key (CF, ID_Persona));

create table FINANZIAMENTO (
     ID_Contratto numeric(10) not null,
     Assicurazione_Credito numeric(1) not null,
     Spese_Apertura_Pratica float(1) not null,
     Anticipo float(1) not null,
     TAEG numeric(1) not null,
     TAN numeric(1) not null,
     constraint FKCON_FIN_ID primary key (ID_Contratto));

create table GRUPPO (
     ID_Ufficio numeric(5) not null,
     ID_Gruppo numeric(5) not null,
     Ind_Via varchar(50) not null,
     Ind_Civico varchar(5) not null,
     Ind_CAP numeric(5) not null,
     Ind_Provincia varchar(10) not null,
     constraint ID_GRUPPO_ID primary key (ID_Ufficio, ID_Gruppo));

create table IMPIEGATO (
     CF varchar(16) not null,
     ID_Persona numeric(10) not null,
     Tipologia_Lavoro varchar(20) not null,
     ID_Ufficio numeric(5) not null,
     constraint FKLAV_IMP_ID primary key (CF, ID_Persona));

create table INTERVENTO (
     ID_Intervento varchar(20) not null,
     Data_Inizio date not null,
     Orario_Inizio varchar(10) not null,
     Tipologia_Intervento varchar(20) not null,
     Costo numeric(10) not null,
     Note varchar(100) not null,
     Durata numeric(10) not null,
     Data_Fine date,
     ID_Officina numeric(50) not null,
     constraint ID_INTERVENTO_ID primary key (ID_Intervento));

create table LAVORATORE (
     CF varchar(16) not null,
     ID_Persona numeric(10) not null,
     Livello numeric(1),
     Data_Assunzione date not null,
     Paga_Mensile numeric(5,2) not null,
     Spe_Venditore char(1) not null,
     Spe_Impiegato char(1) not null,
     Spe_Meccanico char(1) not null,
     Spe_Proprietario char(1) not null,
     VENDITORE varchar(16),
     PROPRIETARIO varchar(16),
     MECCANICO varchar(16),
     IMPIEGATO varchar(16),
     constraint FKPER_LAV_ID primary key (CF, ID_Persona));

create table LEASING (
     ID_Contratto numeric(10) not null,
     Maxi_Canone float(1) not null,
     P.IVA_Societa char(1) not null,
     Durata_Leasing numeric(1) not null,
     Prezzo_Riscatto float(1) not null,
     constraint FKCON_LEA_ID primary key (ID_Contratto));

create table MECCANICO (
     CF varchar(16) not null,
     ID_Persona numeric(10) not null,
     constraint FKLAV_MEC_ID primary key (CF, ID_Persona));

create table METODO_PAGAMENTO (
     ID_MET -- Sequence attribute not implemented -- not null,
     Circuito char(100) not null,
     Intestatario char(100) not null,
     Tipologia char(100) not null,
     Iban char(27) not null,
     constraint ID_ID primary key (ID_MET));

create table NOLEGGIO (
     ID_Contratto numeric(10) not null,
     Ser_Elettronica char(1) not null,
     Ser_Meccanica char(1) not null,
     Ser_Idraulica char(1) not null,
     Ser_Carrozzeria char(1) not null,
     Ser_Interni char(1) not null,
     Ser_Freni char(1) not null,
     Ser_Gomme char(1) not null,
     Franchigia_assicurativa char(1) not null,
     Prezzo_km float(1) not null,
     Km_totali float(1) not null,
     constraint FKCON_NOL_ID primary key (ID_Contratto));

create table NUOVO (
     ID_Veicolo numeric(10) not null,
     Ora_Fine numeric(10) not null,
     constraint FKVEI_NUO_ID primary key (ID_Veicolo));

create table OFFICINA (
     ID_Officina numeric(50) not null,
     ID_Capo numeric(10) not null,
     Interna char not null,
     Nome varchar(50) not null,
     Ind_Via varchar(50),
     Ind_Civico varchar(5),
     Ind_CAP numeric(5),
     Ind_Provincia varchar(10),
     ID_Sede char(1) not null,
     constraint ID_OFFICINA_ID primary key (ID_Officina));

create table OPTIONAL (
     Nome char(1) not null,
     Prezzo char(1) not null,
     Note char(1) not null,
     Tipologia char(1) not null,
     ID_Optional -- Sequence attribute not implemented -- not null,
     constraint ID_OPTIONAL_ID primary key (ID_Optional));

create table PERSONA (
     CF varchar(16) not null,
     ID_Persona numeric(10),
     Nome varchar(30) not null,
     Cognome varchar(30) not null,
     Res_Via varchar(50) not null,
     Res_Civico varchar(5) not null,
     Res_CAP numeric(5) not null,
     Res_Provincia varchar(10) not null,
     Res_Citta varchar(20) not null,
     Rec_Telefono varchar(20) not null,
     Rec_Mail varchar(100) not null,
     Cre_Mail varchar(50) not null,
     Cre_Password varchar(16) not null,
     LAVORATORE varchar(16),
     CLIENTE varchar(16),
     constraint ID_PERSONA_ID primary key (CF, ID_Persona));

create table PRENOTAZIONE (
     Nota_Cliente char(1) not null,
     Data_Prenotazione char(1) not null,
     Ora_Incontro char(1) not null,
     Indirizzo char(1) not null,
     ID_Prenotazione -- Sequence attribute not implemented -- not null,
     ID_Sede char(1) not null,
     ID_Veicolo numeric(10) not null,
     ID_Intervento varchar(20),
     CF varchar(16) not null,
     ID_Persona numeric(10) not null,
     constraint ID_PRENOTAZIONE_ID primary key (ID_Prenotazione));

create table PREVENTIVO (
     ID_Preventivo -- Sequence attribute not implemented -- not null,
     CF varchar(16) not null,
     ID_Persona numeric(10) not null,
     Ins_CF varchar(16) not null,
     Ins_ID_Persona numeric(10) not null,
     Stato_PreventivoChiuso char not null,
     Durata_Massima numeric(3) not null,
     Note varchar(10000) not null,
     Acconto numeric(6,2),
     constraint ID_PREVENTIVO_ID primary key (ID_Preventivo),
     constraint SID_PREVENTIVO_1_ID unique (Ins_CF, Ins_ID_Persona, ID_Preventivo),
     constraint SID_PREVENTIVO_ID unique (CF, ID_Persona, ID_Preventivo));

create table PROPRIETARIO (
     CF varchar(16) not null,
     ID_Persona numeric(10) not null,
     constraint FKLAV_PRO_ID primary key (CF, ID_Persona));

create table RATE (
     ID_Contratto numeric(10) not null,
     Importo_Mensile float(1) not null,
     Numero_Rata char(1) not null,
     Data_Pagamento_Effettivo char(1) not null,
     Stato_Pagamento char(1) not null,
     Tipologia_Addebito char(1) not null,
     constraint FKCON_RAT_ID primary key (ID_Contratto));

create table REPARTO (
     ID_Responsabile numeric(5) not null,
     Nome varchar(50) not null,
     Con_Mail varchar(100) not null,
     Con_Telefono varchar(20) not null,
     Acronimo varchar(5) not null,
     ID_Reparto numeric(5) not null,
     ID_Ufficio numeric(5) not null,
     ID_Gruppo numeric(5) not null,
     constraint ID_REPARTO_ID primary key (Acronimo, ID_Reparto),
     constraint SID_REPARTO_ID unique (ID_Ufficio, ID_Gruppo, Acronimo, ID_Reparto));

create table Lavora (
     ID_Officina numeric(50) not null,
     Orario_Inizio varchar(5) not null,
     Orario_Fine varchar(5) not null,
     CF varchar(16) not null,
     ID_Persona numeric(10) not null,
     constraint FKLav_OFF_ID primary key (ID_Officina));

create table Orario (
     ID_Ufficio numeric(5) not null,
     Orario varchar(11) not null,
     constraint ID_Orario_ID primary key (ID_Ufficio, Orario));

create table Orario_1 (
     ID_Sede char(1) not null,
     Orario varchar(11) not null,
     constraint ID_Orario_1_ID primary key (ID_Sede, Orario));

create table Permuta (
     ID_Usato varchar(50) not null,
     ID_Preventivo numeric(10) not null,
     ValoreApplicato numeric(6,2) not null,
     constraint FKPer_VAL_ID primary key (ID_Usato),
     constraint FKPer_PRE_ID unique (ID_Preventivo));

create table SEDE (
     ID_Sede char(1) not null,
     Data_Apertura date not null,
     Stato_Servizio char not null,
     Denominazione varchar(20) not null,
     Rec_Telefono varchar(20) not null,
     Rec_Mail varchar(100) not null,
     Ind_Via varchar(50) not null,
     Ind_Civico varchar(5) not null,
     Ind_CAP numeric(5) not null,
     Ind_Provincia varchar(10) not null,
     ID_Concessionario numeric(5) not null,
     constraint ID_SEDE_ID primary key (ID_Sede));

create table SETTORE (
     ID_Officina numeric(50) not null,
     ID_Settore varchar(50) not null,
     Cod_Settore char(1) not null,
     Nome varchar(20) not null,
     Descrizione varchar(100) not null,
     ID_Responsabile varchar(20) not null,
     constraint ID_SETTORE_ID primary key (ID_Officina, ID_Settore));

create table STRUMENTO (
     ID_Officina numeric(50) not null,
     ID_Strumento varchar(50) not null,
     ID_Tipo_Officina varchar(50) not null,
     Nome varchar(20) not null,
     Note varchar(100) not null,
     constraint ID_STRUMENTO_ID primary key (ID_Officina, ID_Strumento));

create table TEST_DRIVE (
     Ora_Fine -- Sequence attribute not implemented -- not null,
     Ora_Inizio -- Sequence attribute not implemented -- not null,
     Data char(1) not null,
     ID_TestDrive -- Sequence attribute not implemented -- not null,
     CF varchar(16) not null,
     ID_Persona numeric(10) not null,
     constraint ID_TEST_DRIVE_ID primary key (Ora_Fine),
     constraint SID_TEST_DRIVE_1_ID unique (Ora_Inizio),
     constraint SID_TEST_DRIVE_ID unique (ID_TestDrive));

create table UFFICIO (
     ID_Ufficio numeric(5) not null,
     ID_Officina numeric(50) not null,
     Funzione varchar(50) not null,
     Piano numeric(3) not null,
     ID_Sede char(1) not null,
     constraint ID_UFFICIO_ID primary key (ID_Ufficio),
     constraint FKHa__ID unique (ID_Officina));

create table USATO (
     ID_Veicolo numeric(10) not null,
     ID_Usato varchar(50) not null,
     Kilometraggio char(1) not null,
     constraint FKVEI_USA_ID primary key (ID_Veicolo),
     constraint FKCoinvolge_ID unique (ID_Usato));

create table VALUTAZIONE_USATO (
     ID_Usato varchar(50) not null,
     Data_Inizio date not null,
     Data_Fine date not null,
     Prezzo_Finale numeric(6,2) not null,
     CF varchar(16) not null,
     ID_Persona numeric(10) not null,
     constraint ID_VALUTAZIONE_USATO_ID primary key (ID_Usato));

create table VEICOLO (
     Tipologia_Motrice char(1) not null,
     Peso char(1) not null,
     Descrizione char(1) not null,
     Prezzo_Base char(1) not null,
     Anno_Immatricolazione char(1) not null,
     Potenza_CV char(1) not null,
     Sta_Disponibile char(1) not null,
     Sta_Bloccato char(1) not null,
     Modello char(1) not null,
     Marca char(1) not null,
     ID_Veicolo -- Sequence attribute not implemented -- not null,
     ID_Preventivo numeric(10) not null,
     USATO numeric(10),
     NUOVO numeric(10),
     ID_ARC numeric(10) not null,
     constraint ID_VEICOLO_ID primary key (ID_Veicolo),
     constraint FKAssociato1_ID unique (ID_Preventivo));

create table Vendita (
     ID_Vendita varchar(10) not null,
     Stato char not null,
     Data date not null,
     Ora numeric(4) not null,
     ID_Contratto numeric(10) not null,
     constraint ID_Vendita_ID primary key (ID_Vendita),
     constraint SID_Vendita_ID unique (Data, Ora),
     constraint FKTerminazione_ID unique (ID_Contratto));

create table VENDITA_TOTALE (
     ID_Contratto numeric(10) not null,
     Consegna_Effettivo_Veicolo date not null,
     Data_Saldo_Effettivo date not null,
     Sconto_Pronto_Pagamento numeric(1) not null,
     constraint FKCON_VEN_ID primary key (ID_Contratto));

create table VENDITORE (
     CF varchar(16) not null,
     ID_Persona numeric(10) not null,
     Bonus_Vendite numeric(6) not null,
     Ora_Fine numeric(10) not null,
     ID_Ufficio numeric(5) not null,
     constraint FKLAV_VEN_ID primary key (CF, ID_Persona));


-- Constraints Section
-- ___________________ 

alter table Approvazione add constraint FKApp_VAL_FK
     foreign key (ID_Usato)
     references VALUTAZIONE_USATO;

alter table Approvazione add constraint FKApp_PRO_FK
     foreign key (CF, ID_Persona)
     references PROPRIETARIO;

alter table CLIENTE add constraint FKPER_CLI_FK
     foreign key (CF, ID_Persona)
     references PERSONA;

alter table Codice_Settore add constraint FKMEC_Cod
     foreign key (CF, ID_Persona)
     references MECCANICO;

alter table Compito add constraint FKSpecifico
     foreign key (ID_Intervento)
     references INTERVENTO;

alter table Compito add constraint FKAssegnato
     foreign key (CF, ID_Persona)
     references MECCANICO;

alter table Comprende1 add constraint FKCom_VEI_FK
     foreign key (ID_Veicolo)
     references VEICOLO;

alter table Comprende1 add constraint FKCom_OPT
     foreign key (ID_Optional)
     references OPTIONAL;

alter table CONCESSIONARIO add constraint FKGestisce_FK
     foreign key (CF, ID_Persona)
     references PROPRIETARIO;

alter table CONTRATTO add constraint ID_CONTRATTO_CHK
     check(exists(select * from Vendita
                  where Vendita.ID_Contratto = ID_Contratto)); 

alter table CONTRATTO add constraint LSTONE_CONTRATTO
     check(RATE is not null or NOLEGGIO is not null or LEASING is not null or FINANZIAMENTO is not null or VENDITA_TOTALE is not null); 

alter table CONTRATTO add constraint FKComprende__FK
     foreign key (ID_Preventivo)
     references PREVENTIVO;

alter table CONTRATTO add constraint FKAssociato_
     foreign key (ID_MET)
     references METODO_PAGAMENTO;

alter table Esito add constraint FKEsi_VAL_FK
     foreign key (ID_Usato)
     references VALUTAZIONE_USATO;

alter table Esito add constraint FKEsi_MEC_FK
     foreign key (CF, ID_Persona)
     references MECCANICO;

alter table FINANZIAMENTO add constraint FKCON_FIN_FK
     foreign key (ID_Contratto)
     references CONTRATTO;

alter table GRUPPO add constraint FKHa
     foreign key (ID_Ufficio)
     references UFFICIO;

alter table IMPIEGATO add constraint FKLAV_IMP_FK
     foreign key (CF, ID_Persona)
     references LAVORATORE;

alter table IMPIEGATO add constraint FKLavora___FK
     foreign key (ID_Ufficio)
     references UFFICIO;

alter table INTERVENTO add constraint FKEffettua_FK
     foreign key (ID_Officina)
     references OFFICINA;

alter table LAVORATORE add constraint LSTONE_LAVORATORE
     check(VENDITORE is not null or IMPIEGATO is not null or PROPRIETARIO is not null or MECCANICO is not null); 

alter table LAVORATORE add constraint FKPER_LAV_FK
     foreign key (CF, ID_Persona)
     references PERSONA;

alter table LEASING add constraint FKCON_LEA_FK
     foreign key (ID_Contratto)
     references CONTRATTO;

alter table MECCANICO add constraint FKLAV_MEC_CHK
     check(exists(select * from Codice_Settore
                  where Codice_Settore.CF = CF and Codice_Settore.ID_Persona = ID_Persona)); 

alter table MECCANICO add constraint FKLAV_MEC_CHK
     check(exists(select * from Esito
                  where Esito.CF = CF and Esito.ID_Persona = ID_Persona)); 

alter table MECCANICO add constraint FKLAV_MEC_FK
     foreign key (CF, ID_Persona)
     references LAVORATORE;

alter table NOLEGGIO add constraint FKCON_NOL_FK
     foreign key (ID_Contratto)
     references CONTRATTO;

alter table NUOVO add constraint FKVEI_NUO_FK
     foreign key (ID_Veicolo)
     references VEICOLO;

alter table NUOVO add constraint FKUtilizzo_FK
     foreign key (Ora_Fine)
     references TEST_DRIVE;

alter table OFFICINA add constraint ID_OFFICINA_CHK
     check(exists(select * from UFFICIO
                  where UFFICIO.ID_Officina = ID_Officina)); 

alter table OFFICINA add constraint ID_OFFICINA_CHK
     check(exists(select * from Lavora
                  where Lavora.ID_Officina = ID_Officina)); 

alter table OFFICINA add constraint COEX_OFFICINA
     check((Ind_Via is not null and Ind_Civico is not null and Ind_CAP is not null and Ind_Provincia is not null)
           or (Ind_Via is null and Ind_Civico is null and Ind_CAP is null and Ind_Provincia is null)); 

alter table OFFICINA add constraint FKInclude_FK
     foreign key (ID_Sede)
     references SEDE;

alter table PERSONA add constraint LSTONE_PERSONA
     check(CLIENTE is not null or LAVORATORE is not null); 

alter table PRENOTAZIONE add constraint FKRichiede1_FK
     foreign key (ID_Sede)
     references SEDE;

alter table PRENOTAZIONE add constraint FKComprende2_FK
     foreign key (ID_Veicolo)
     references VEICOLO;

alter table PRENOTAZIONE add constraint FKAssociato_FK
     foreign key (ID_Intervento)
     references INTERVENTO;

alter table PRENOTAZIONE add constraint FKRichiede_FK
     foreign key (CF, ID_Persona)
     references CLIENTE;

alter table PREVENTIVO add constraint ID_PREVENTIVO_CHK
     check(exists(select * from VEICOLO
                  where VEICOLO.ID_Preventivo = ID_Preventivo)); 

alter table PREVENTIVO add constraint FKPossiede_
     foreign key (CF, ID_Persona)
     references CLIENTE;

alter table PREVENTIVO add constraint FKInstaura
     foreign key (Ins_CF, Ins_ID_Persona)
     references VENDITORE;

alter table PROPRIETARIO add constraint FKLAV_PRO_CHK
     check(exists(select * from Approvazione
                  where Approvazione.CF = CF and Approvazione.ID_Persona = ID_Persona)); 

alter table PROPRIETARIO add constraint FKLAV_PRO_FK
     foreign key (CF, ID_Persona)
     references LAVORATORE;

alter table RATE add constraint FKCON_RAT_FK
     foreign key (ID_Contratto)
     references CONTRATTO;

alter table REPARTO add constraint FKAppartenenza
     foreign key (ID_Ufficio, ID_Gruppo)
     references GRUPPO;

alter table Lavora add constraint FKLav_OFF_FK
     foreign key (ID_Officina)
     references OFFICINA;

alter table Lavora add constraint FKLav_MEC_1_FK
     foreign key (CF, ID_Persona)
     references MECCANICO;

alter table Orario add constraint FKUFF_Ora
     foreign key (ID_Ufficio)
     references UFFICIO;

alter table Orario_1 add constraint FKSED_Ora
     foreign key (ID_Sede)
     references SEDE;

alter table Permuta add constraint FKPer_VAL_FK
     foreign key (ID_Usato)
     references VALUTAZIONE_USATO;

alter table Permuta add constraint FKPer_PRE_FK
     foreign key (ID_Preventivo)
     references PREVENTIVO;

alter table SEDE add constraint ID_SEDE_CHK
     check(exists(select * from Orario_1
                  where Orario_1.ID_Sede = ID_Sede)); 

alter table SEDE add constraint FKPossiede_FK
     foreign key (ID_Concessionario)
     references CONCESSIONARIO;

alter table SETTORE add constraint FKComprende
     foreign key (ID_Officina)
     references OFFICINA;

alter table STRUMENTO add constraint FKDetiene
     foreign key (ID_Officina)
     references OFFICINA;

alter table TEST_DRIVE add constraint ID_TEST_DRIVE_CHK
     check(exists(select * from VENDITORE
                  where VENDITORE.Ora_Fine = Ora_Fine)); 

alter table TEST_DRIVE add constraint FKPartecipa_FK
     foreign key (CF, ID_Persona)
     references CLIENTE;

alter table UFFICIO add constraint ID_UFFICIO_CHK
     check(exists(select * from VENDITORE
                  where VENDITORE.ID_Ufficio = ID_Ufficio)); 

alter table UFFICIO add constraint ID_UFFICIO_CHK
     check(exists(select * from IMPIEGATO
                  where IMPIEGATO.ID_Ufficio = ID_Ufficio)); 

alter table UFFICIO add constraint ID_UFFICIO_CHK
     check(exists(select * from Orario
                  where Orario.ID_Ufficio = ID_Ufficio)); 

alter table UFFICIO add constraint FKHa__FK
     foreign key (ID_Officina)
     references OFFICINA;

alter table UFFICIO add constraint FKComposto_FK
     foreign key (ID_Sede)
     references SEDE;

alter table USATO add constraint FKVEI_USA_FK
     foreign key (ID_Veicolo)
     references VEICOLO;

alter table USATO add constraint FKCoinvolge_FK
     foreign key (ID_Usato)
     references VALUTAZIONE_USATO;

alter table VALUTAZIONE_USATO add constraint ID_VALUTAZIONE_USATO_CHK
     check(exists(select * from USATO
                  where USATO.ID_Usato = ID_Usato)); 

alter table VALUTAZIONE_USATO add constraint FKInizia_FK
     foreign key (CF, ID_Persona)
     references CLIENTE;

alter table VEICOLO add constraint EXTONE_VEICOLO
     check((USATO is not null and NUOVO is null)
           or (USATO is null and NUOVO is not null)); 

alter table VEICOLO add constraint FKAssociato1_FK
     foreign key (ID_Preventivo)
     references PREVENTIVO;

alter table VEICOLO add constraint FKCompare_FK
     foreign key (ID_ARC)
     references ARCHIVIO;

alter table Vendita add constraint FKTerminazione_FK
     foreign key (ID_Contratto)
     references CONTRATTO;

alter table VENDITA_TOTALE add constraint FKCON_VEN_FK
     foreign key (ID_Contratto)
     references CONTRATTO;

alter table VENDITORE add constraint FKSupervisiona_FK
     foreign key (Ora_Fine)
     references TEST_DRIVE;

alter table VENDITORE add constraint FKLAV_VEN_FK
     foreign key (CF, ID_Persona)
     references LAVORATORE;

alter table VENDITORE add constraint FK_Lavora__FK
     foreign key (ID_Ufficio)
     references UFFICIO;


-- Index Section
-- _____________ 

create index FKApp_VAL_IND
     on Approvazione (ID_Usato);

create unique index FKApp_PRO_IND
     on Approvazione (CF, ID_Persona);

create unique index ID_IND
     on ARCHIVIO (ID_ARC);

create unique index FKPER_CLI_IND
     on CLIENTE (CF, ID_Persona);

create unique index ID_Codice_Settore_IND
     on Codice_Settore (CF, ID_Persona, Codice_Settore);

create unique index ID_Compito_IND
     on Compito (CF, ID_Persona, ID_Compito);

create unique index SID_Compito_IND
     on Compito (ID_Intervento, ID_Compito);

create unique index ID_Comprende1_IND
     on Comprende1 (ID_Optional, ID_Veicolo);

create index FKCom_VEI_IND
     on Comprende1 (ID_Veicolo);

create unique index ID_CONCESSIONARIO_IND
     on CONCESSIONARIO (ID_Concessionario);

create index FKGestisce_IND
     on CONCESSIONARIO (CF, ID_Persona);

create unique index ID_CONTRATTO_IND
     on CONTRATTO (ID_Contratto);

create unique index SID_CONTRATTO_IND
     on CONTRATTO (ID_MET, ID_Contratto);

create unique index FKComprende__IND
     on CONTRATTO (ID_Preventivo);

create index FKEsi_VAL_IND
     on Esito (ID_Usato);

create unique index FKEsi_MEC_IND
     on Esito (CF, ID_Persona);

create unique index FKCON_FIN_IND
     on FINANZIAMENTO (ID_Contratto);

create unique index ID_GRUPPO_IND
     on GRUPPO (ID_Ufficio, ID_Gruppo);

create unique index FKLAV_IMP_IND
     on IMPIEGATO (CF, ID_Persona);

create index FKLavora___IND
     on IMPIEGATO (ID_Ufficio);

create unique index ID_INTERVENTO_IND
     on INTERVENTO (ID_Intervento);

create index FKEffettua_IND
     on INTERVENTO (ID_Officina);

create unique index FKPER_LAV_IND
     on LAVORATORE (CF, ID_Persona);

create unique index FKCON_LEA_IND
     on LEASING (ID_Contratto);

create unique index FKLAV_MEC_IND
     on MECCANICO (CF, ID_Persona);

create unique index ID_IND
     on METODO_PAGAMENTO (ID_MET);

create unique index FKCON_NOL_IND
     on NOLEGGIO (ID_Contratto);

create unique index FKVEI_NUO_IND
     on NUOVO (ID_Veicolo);

create index FKUtilizzo_IND
     on NUOVO (Ora_Fine);

create unique index ID_OFFICINA_IND
     on OFFICINA (ID_Officina);

create index FKInclude_IND
     on OFFICINA (ID_Sede);

create unique index ID_OPTIONAL_IND
     on OPTIONAL (ID_Optional);

create unique index ID_PERSONA_IND
     on PERSONA (CF, ID_Persona);

create unique index ID_PRENOTAZIONE_IND
     on PRENOTAZIONE (ID_Prenotazione);

create index FKRichiede1_IND
     on PRENOTAZIONE (ID_Sede);

create index FKComprende2_IND
     on PRENOTAZIONE (ID_Veicolo);

create index FKAssociato_IND
     on PRENOTAZIONE (ID_Intervento);

create index FKRichiede_IND
     on PRENOTAZIONE (CF, ID_Persona);

create unique index ID_PREVENTIVO_IND
     on PREVENTIVO (ID_Preventivo);

create unique index SID_PREVENTIVO_1_IND
     on PREVENTIVO (Ins_CF, Ins_ID_Persona, ID_Preventivo);

create unique index SID_PREVENTIVO_IND
     on PREVENTIVO (CF, ID_Persona, ID_Preventivo);

create unique index FKLAV_PRO_IND
     on PROPRIETARIO (CF, ID_Persona);

create unique index FKCON_RAT_IND
     on RATE (ID_Contratto);

create unique index ID_REPARTO_IND
     on REPARTO (Acronimo, ID_Reparto);

create unique index SID_REPARTO_IND
     on REPARTO (ID_Ufficio, ID_Gruppo, Acronimo, ID_Reparto);

create unique index FKLav_OFF_IND
     on Lavora (ID_Officina);

create index FKLav_MEC_1_IND
     on Lavora (CF, ID_Persona);

create unique index ID_Orario_IND
     on Orario (ID_Ufficio, Orario);

create unique index ID_Orario_1_IND
     on Orario_1 (ID_Sede, Orario);

create unique index FKPer_VAL_IND
     on Permuta (ID_Usato);

create unique index FKPer_PRE_IND
     on Permuta (ID_Preventivo);

create unique index ID_SEDE_IND
     on SEDE (ID_Sede);

create index FKPossiede_IND
     on SEDE (ID_Concessionario);

create unique index ID_SETTORE_IND
     on SETTORE (ID_Officina, ID_Settore);

create unique index ID_STRUMENTO_IND
     on STRUMENTO (ID_Officina, ID_Strumento);

create unique index ID_TEST_DRIVE_IND
     on TEST_DRIVE (Ora_Fine);

create unique index SID_TEST_DRIVE_1_IND
     on TEST_DRIVE (Ora_Inizio);

create unique index SID_TEST_DRIVE_IND
     on TEST_DRIVE (ID_TestDrive);

create index FKPartecipa_IND
     on TEST_DRIVE (CF, ID_Persona);

create unique index ID_UFFICIO_IND
     on UFFICIO (ID_Ufficio);

create unique index FKHa__IND
     on UFFICIO (ID_Officina);

create index FKComposto_IND
     on UFFICIO (ID_Sede);

create unique index FKVEI_USA_IND
     on USATO (ID_Veicolo);

create unique index FKCoinvolge_IND
     on USATO (ID_Usato);

create unique index ID_VALUTAZIONE_USATO_IND
     on VALUTAZIONE_USATO (ID_Usato);

create index FKInizia_IND
     on VALUTAZIONE_USATO (CF, ID_Persona);

create unique index ID_VEICOLO_IND
     on VEICOLO (ID_Veicolo);

create unique index FKAssociato1_IND
     on VEICOLO (ID_Preventivo);

create index FKCompare_IND
     on VEICOLO (ID_ARC);

create unique index ID_Vendita_IND
     on Vendita (ID_Vendita);

create unique index SID_Vendita_IND
     on Vendita (Data, Ora);

create unique index FKTerminazione_IND
     on Vendita (ID_Contratto);

create unique index FKCON_VEN_IND
     on VENDITA_TOTALE (ID_Contratto);

create index FKSupervisiona_IND
     on VENDITORE (Ora_Fine);

create unique index FKLAV_VEN_IND
     on VENDITORE (CF, ID_Persona);

create index FK_Lavora__IND
     on VENDITORE (ID_Ufficio);

