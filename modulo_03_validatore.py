import requests
import pandas as pd
import os
from datetime import datetime

# Configurazione API Key Football-Data.org
API_KEY = "e0ca06c07c634d4fb0950365bd82ffd0"
BASE_URL = "https://api.football-data.org/v4/"
HEADERS = {"X-Auth-Token": API_KEY}

PALINSESTO_FILE = "Pronostici_App_Betting.xlsx"
STORICO_FILE = "Storico_Validato_Betting.xlsx"

def esegui_validazione():
    """
    Modulo 03: Convalida Risultati Reali (Fase 2) - Versione 5.39
    Interroga l'API reale per trovare i match FINISHED dei 12 campionati.
    Trascina le statistiche congelate dal Palinsesto SOLO se la partita è realmente terminata.
    Elimina totalmente dati simulati o inventati.
    """
    print("🏆 [FASE 2] Avvio Validazione Reale tramite API Football-Data...")
    
    # 1. Caricamento del Palinsesto
    if not os.path.exists(PALINSESTO_FILE):
        print(f"⚠️ Errore: {PALINSESTO_FILE} non trovato. Impossibile validare.")
        return
    
    df_palinsesto = pd.read_excel(PALINSESTO_FILE)
    if df_palinsesto.empty:
        print("⚠️ Palinsesto vuoto. Nessun match da validare.")
        return

    # Caricamento dello storico esistente per evitare doppioni
    if os.path.exists(STORICO_FILE):
        try:
            df_storico_esistente = pd.read_excel(STORICO_FILE)
        except:
            df_storico_esistente = pd.DataFrame()
    else:
        df_storico_esistente = pd.DataFrame()

    # Creazione set di ID match già validati per scudo anti-doppione nativo
    ids_convalidati = set()
    if not df_storico_esistente.empty and 'Match_ID' in df_storico_esistente.columns:
        ids_convalidati = set(df_storico_esistente['Match_ID'].dropna().astype(int).tolist())

    # 2. Recupero dei match terminati (FINISHED) direttamente dall'API per i campionati presenti nel palinsesto
    campionati_da_controllare = df_palinsesto['Cod_Campionato'].dropna().unique()
    
    risultati_reali_api = {}
    
    for cod_camp in campionati_da_controllare:
        # Interroghiamo l'API per i match dell'ultimo periodo di quel campionato
        url = f"{BASE_URL}competitions/{cod_camp}/matches?status=FINISHED"
        try:
            res = requests.get(url, headers=HEADERS, timeout=12)
            if res.status_code == 200:
                matches = res.json().get("matches", [])
                for m in matches:
                    m_id = int(m.get("id"))
                    score = m.get("score", {})
                    full_time = score.get("fullTime", {})
                    home_goals = full_time.get("home")
                    away_goals = full_time.get("away")
                    
                    if home_goals is not None and away_goals is not None:
                        risultati_reali_api[m_id] = {
                            "punteggio": f"{home_goals}-{away_goals}",
                            "home_goals": home_goals,
                            "away_goals": away_goals
                        }
        except Exception as e:
            print(f"⚠️ Errore nel recupero risultati API per {cod_camp}: {str(e)}")

    record_convalidati_ora = []

    # 3. Associazione tra Palinsesto e Risultati Reali dell'API tramite Match_ID univoco
    for idx, row in df_palinsesto.iterrows():
        m_id = int(row.get('Match_ID', 0))
        
        # Scudo Anti-Doppione: Se è già dentro lo storico validato, lo saltiamo
        if m_id in ids_convalidati:
            continue
            
        # Se il match non è presente tra quelli FINISHED dell'API, significa che deve ancora essere giocato
        # o non è ancora stato refertato. Rigido divieto di inventare risultati: IMPOSTIAMO STATO DI ATTESA.
        if m_id not in risultati_reali_api:
            continue
            
        # Il match è FINISHED sul server: estraiamo i dati veri
        dati_veri = risultati_reali_api[m_id]
        
        nuovo_record = row.copy()
        nuovo_record['Risultato_Reale'] = dati_veri["punteggio"]
        
        # Calcolo dell'esito 1X2 reale basato sui gol veri dell'API
        h_g = dati_veri["home_goals"]
        a_g = dati_veri["away_goals"]
        segno_reale = "1" if h_g > a_g else ("X" if h_g == a_g else "2")
        
        pronostico_1x2 = str(row.get('1X2', ''))
        nuovo_record['Esito_1X2'] = "VINCENTE" if segno_reale in pronostico_1x2 else "PERDENTE"
        
        # Inizializzazione degli altri mercati (verranno calcolati matematicamente dai gol reali nelle prossime versioni)
        campi_esito = [
            "Esito_Risultato_Esatto", "Esito_Doppia_Chance", "Esito_DC+U/O2.5", 
            "Esito_U/O_1.5", "Esito_U/O_2.5", "Esito_U/O_3.5", "Esito_Goal_NoGoal", 
            "Esito_Media_Goal_Casa", "Esito_Media_Goal_Trasferta", "Esito_Media_Goal_Totale", "Esito_Corner_1X2"
        ]
        for col_esito in campi_esito:
            nuovo_record[col_esito] = "DA_CALCOLARE"
            
        record_convalidati_ora.append(nuovo_record)

    if not record_convalidati_ora:
        print("⚽ Nessun nuovo match terminato trovato rispetto all'ultimo controllo. Storico invariato.")
        return

    # 4. Unione sicura e salvataggio
    df_nuovi_validati = pd.DataFrame(record_convalidati_ora)
    if not df_storico_esistente.empty:
        df_finale = pd.concat([df_storico_esistente, df_nuovi_validati], ignore_index=True)
    else:
        df_finale = df_nuovi_validati

    df_finale.to_excel(STORICO_FILE, index=False)
    print(f"✅ Storico Validato aggiornato con successo! Aggiunti {len(df_nuovi_validati)} match realmente TERMINATI.")

if __name__ == "__main__":
    esegui_validazione()
