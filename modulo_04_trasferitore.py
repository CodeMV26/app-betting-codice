import sys
import os
import pandas as pd
import requests
import base64

# PROGRESSIVO CHAT: #160 | Data: 15 Luglio 2026 | Ora: 13:42:18
# Versione Progetto: 7.00 | MODULO 04: ARCHIVIAZIONE CON PUSH AUTOMATICO SU GITHUB E BACKUP PERMANENTE TOKENS

STORICO_FILE = "Storico_Validato_Betting.xlsx"
DATABASE_STORICO_GLOBALE = "Database_Storico_Completo.xlsx"

def genera_chiave_univoca_local(row):
    data = str(row.get('Data_Ora_Match', row.get('Data', row.get('2. Data', '')))).strip()
    match_str = str(row.get('3. Match', row.get('Match', ''))).strip()
    return f"{data}_{match_str}".lower().replace(" ", "")

def _push_to_github_repository(percorso_file_locale, nome_file_su_github):
    """
    Invia tramite API di GitHub il file Excel aggiornato direttamente nella repository
    utilizzando il token di autenticazione configurato nei Secrets di Streamlit.
    Garantisce la persistenza assoluta dei dati contro l'ibernazione cloud.
    """
    try:
        # Recupero parametri di sicurezza dai Secrets di Streamlit o variabili d'ambiente
        token = os.environ.get("GITHUB_TOKEN") or (st.secrets["GITHUB_TOKEN"] if "st" in sys.modules else None)
        # Identificazione repository (estrazione dinamica o fallback configurato)
        repo = os.environ.get("GITHUB_REPOSITORY", "CodeMV26/Betting_Pro_Mobile") # Fallback sicuro sul tuo account
        
        if not token:
            print("⚠️ GITHUB_TOKEN non trovato nei Secrets. Sincronizzazione Cloud saltata (Scrittura solo Locale).")
            return False
            
        url = f"https://api.github.com/repos/{repo}/contents/{nome_file_su_github}"
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # 1. Recupero dello SHA del file se già esistente su GitHub (necessario per l'update)
        sha = None
        r_get = requests.get(url, headers=headers)
        if r_get.status_code == 200:
            sha = r_get.json().get("sha")
            
        # 2. Lettura e codifica del file Excel locale in Base64
        with open(percorso_file_locale, "rb") as f:
            content_base64 = base64.b64encode(f.read()).decode("utf-8")
            
        # 3. Payload di caricamento
        payload = {
            "message": f"🤖 [Auto-Commit] Aggiornamento Database Storico - Letargo Safe",
            "content": content_base64,
            "branch": "main" # Canale principale
        }
        if sha:
            payload["sha"] = sha
            
        r_put = requests.put(url, headers=headers, json=payload)
        if r_put.status_code in [200, 201]:
            print(f"🚀 [SINCRO GITHUB] File {nome_file_su_github} salvato con successo nella repository cloud!")
            return True
        else:
            print(f"❌ Errore sincronizzazione cloud GitHub API. Status Code: {r_put.status_code}, Risposta: {r_put.text}")
            return False
            
    except Exception as e:
        print(f"⚠️ Errore imprevisto durante il Push automatico su GitHub: {str(e)}")
        return False

def _logica_core_trasferimento():
    if not os.path.exists(STORICO_FILE):
        print("⚠️ File storico sorgente non trovato.")
        return
        
    try:
        df_storico_corrente = pd.read_excel(STORICO_FILE)
        if df_storico_corrente.empty:
            print("⚠️ Lo storico sorgente è vuoto. Nessun dato da trasferire.")
            return
            
        # BASE STATICA: Colonne di controllo fisse
        colonne_base = ["Risultato_Reale", "Risultato Reale"]
        
        # RILEVAMENTO DINAMICO: Cattura istantaneamente ogni variante dei 12 mercati ed esiti presenti nello Storico
        colonne_rilevate_dinamiche = []
        parole_chiave_mercati = ["1X2", "CH.", "CHANCE", "U/O", "OVER", "UNDER", "GOAL", "CORNER", "MG", "CASA", "OSPITE", "TRASFERTA", "ESITO"]
        
        for col in df_storico_corrente.columns:
            col_upper = str(col).upper()
            if any(p_chiave in col_upper for p_chiave in parole_chiave_mercati) or col_upper.startswith("ESITO"):
                if col not in colonne_rilevate_dinamiche:
                    colonne_rilevate_dinamiche.append(col)
                    
        # Unione finale per comporre l'elenco totale delle colonne dei mercati da blindare
        colonne_mercati_testo = list(set(colonne_base + colonne_rilevate_dinamiche))

        # Assicura l'esistenza di tutte le colonne nello storico corrente e forzane il tipo stringa
        for col in colonne_mercati_testo:
            if col not in df_storico_corrente.columns:
                df_storico_corrente[col] = "-"
            df_storico_corrente[col] = df_storico_corrente[col].astype(str).str.strip()

        # DIVISIONE DEI MATCH: Isola le partite TERMINATE e VALIDATE da quelle ancora IN ATTESA
        maschera_terminati = (
            df_storico_corrente['Risultato_Reale'].notna() & 
            (df_storico_corrente['Risultato_Reale'].astype(str).str.upper().str.strip() != "IN ATTESA") &
            (df_storico_corrente['Risultato_Reale'].astype(str).str.upper().str.strip() != "NAN") &
            (df_storico_corrente['Risultato_Reale'].astype(str).str.strip() != "")
        )
        
        df_da_trasferire = df_storico_corrente[maschera_terminati].copy()
        df_da_mantenere_in_storico = df_storico_corrente[~maschera_terminati].copy()

        if df_da_trasferire.empty:
            print("ℹ️ Nessun match terminato e validato trovato nello Storico. Fase 3 saltata.")
            return

        print(f"📈 Trovati {len(df_da_trasferire)} match terminati da spostare nel Database globale.")

        # Caricamento o creazione del Database Storico Globale
        if os.path.exists(DATABASE_STORICO_GLOBALE):
            df_db_esistente = pd.read_excel(DATABASE_STORICO_GLOBALE)
            if not df_db_esistente.empty:
                # -------------------------------------------------------------
                # MODIFICA RIGIDA E DEFINITIVA: Creazione di una struttura unificata pulita
                # Uniamo le colonne fisicamente presenti in entrambi i file per evitare disallineamenti di indice
                colonne_totali = list(df_db_esistente.columns)
                for c in df_da_trasferire.columns:
                    if c not in colonne_totali:
                        colonne_totali.append(c)
                
                # Assegnazione forzata delle nuove colonne vuote come stringhe pulite sul database esistente
                for col in colonne_totali:
                    if col not in df_db_esistente.columns:
                        df_db_esistente[col] = "-"
                    df_db_esistente[col] = df_db_esistente[col].astype(str).str.strip()
                # -------------------------------------------------------------
                
                # Mappatura chiavi presenti nel Database per evitare duplicazioni esatte dello stesso evento
                mappa_chiavi_db = {genera_chiave_univoca_local(riga): idx for idx, riga in df_db_esistente.iterrows()}
                
                record_effettivi_nuovi = []
                for _, riga in df_da_trasferire.iterrows():
                    chiave_nuova = genera_chiave_univoca_local(riga)
                    if chiave_nuova in mappa_chiavi_db:
                        # Aggiorna in modo incondizionato ogni singola colonna inclusi tutti i 12 mercati ed esiti rilevati
                        idx_db = mappa_chiavi_db[chiave_nuova]
                        for col in df_da_trasferire.columns:
                            df_db_esistente.at[idx_db, col] = str(riga[col]).strip()
                    else:
                        record_effettivi_nuovi.append(riga)
                
                if record_effettivi_nuovi:
                    df_nuovi_inserimenti = pd.DataFrame(record_effettivi_nuovi)
                    # Allinea lo schema dei nuovi inserimenti prima della concatenazione
                    for col in df_db_esistente.columns:
                        if col not in df_nuovi_inserimenti.columns:
                            df_nuovi_inserimenti[col] = "-"
                    df_db_finale = pd.concat([df_db_esistente, df_nuovi_inserimenti], ignore_index=True, sort=False)
                else:
                    df_db_finale = df_db_esistente
            else:
                df_db_finale = df_da_trasferire
        else:
            df_db_finale = df_da_trasferire

        # Sincronizzazione finale di sicurezza sulla struttura prima della scrittura su disco
        for col in colonne_mercati_testo:
            if col not in df_db_finale.columns:
                df_db_finale[col] = "-"
            df_db_finale[col] = df_db_finale[col].astype(str).str.strip()

        # 1. SALVATAGGIO SCRITTURA NEL DATABASE GLOBALE LOCALE (Garantisce la crescita infinita)
        df_db_finale.to_excel(DATABASE_STORICO_GLOBALE, index=False)
        print(f"✅ Database Definitivo aggiornato con successo localmente. Totale record attuali: {len(df_db_finale)}")

        # 2. SINCRONIZZAZIONE FORZATA CLOUD (Risolve il problema dell'ibernazione)
        _push_to_github_repository(DATABASE_STORICO_GLOBALE, DATABASE_STORICO_GLOBALE)

        # 3. PULIZIA REALE DELLO STORICO: Salviamo nello Storico solo i match non ancora convalidati
        df_da_mantenere_in_storico.to_excel(STORICO_FILE, index=False)
        print(f"🧹 Pulizia completata localmente: rimossi {len(df_da_trasferire)} eventi terminati dallo Storico ({len(df_da_mantenere_in_storico)} rimasti in attesa).")
        
        # Sincronizziamo anche lo Storico_Validato_Betting pulito su GitHub per consistenza
        _push_to_github_repository(STORICO_FILE, STORICO_FILE)

    except Exception as e:
        print(f"❌ Errore controllato durante il trasferimento: {e}")
        raise e

def esegui_allineamento():
    _logica_core_trasferimento()

def esegui_trasferimento():
    _logica_core_trasferimento()

sys.modules[__name__].esegui_allineamento = esegui_allineamento
sys.modules[__name__].esegui_trasferimento = esegui_trasferimento
