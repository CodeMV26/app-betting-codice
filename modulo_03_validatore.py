import requests
import pandas as pd
import os

# Configurazione API Key Football-Data.org
API_KEY = "e0ca06c07c634d4fb0950365bd82ffd0"
BASE_URL = "https://api.football-data.org/v4/"
HEADERS = {"X-Auth-Token": API_KEY}

PALINSESTO_FILE = "Pronostici_App_Betting.xlsx"
STORICO_FILE = "Storico_Validato_Betting.xlsx"

# Mappatura globale di sicurezza per forzare i codici API se nel palinsesto ci sono i nomi estesi
MAPPA_CAMPIONATI = {
    "PREMIER LEAGUE": "PL", "SERIE A": "SA", "BUNDESLIGA": "BL1", "LA LIGA": "PD",
    "PRIMERA DIVISION": "PD", "LIGUE 1": "FL1", "EREDIVISIE": "DED", "CHAMPIONSHIP": "ELC",
    "PRIMEIRA LIGA": "PPL", "CAMPEONATO BRASILEIRO SÉRIE A": "BSA", "UEFA CHAMPIONS LEAGUE": "CL"
}

def esegui_validazione():
    """
    Modulo 03: Convalida Risultati Reali (Fase 2) - Versione 5.41
    Scarica i risultati reali superando i limiti di stringa del campionato.
    Se un match è finito, trascina le statistiche e calcola l'esito reale.
    Se un match non è finito, lo mantiene nello storico in attesa senza inventare dati.
    """
    print("🏆 [FASE 2] Avvio Validazione Reale e Sincronizzazione Totale...")
    
    if not os.path.exists(PALINSESTO_FILE):
        print(f"⚠️ Errore: {PALINSESTO_FILE} non trovato.")
        return
    
    df_palinsesto = pd.read_excel(PALINSESTO_FILE)
    if df_palinsesto.empty:
        print("⚠️ Palinsesto vuoto.")
        return

    # Pulizia preventiva del Palinsesto da righe corrotte o None vs None
    if '3. Match' in df_palinsesto.columns:
        df_palinsesto = df_palinsesto[df_palinsesto['3. Match'].astype(str).str.upper() != 'NONE VS NONE']
        df_palinsesto = df_palinsesto.dropna(subset=['3. Match'])

    # Identificazione colonna campionato
    col_camp = None
    for c in df_palinsesto.columns:
        if "CAMPIONATO" in c.upper():
            col_camp = c
            break

    # Recupero risultati FINISHED da tutte le competizioni attive nel palinsesto
    risultati_api = {}
    if col_camp:
        campionati_presenti = df_palinsesto[col_camp].dropna().unique()
        for camp in campionati_presenti:
            cod = str(camp).strip().upper()
            # Se è il nome lungo, lo convertiamo nel codice API corretto (es. Serie A -> SA)
            if cod in MAPPA_CAMPIONATI:
                cod = MAPPA_CAMPIONATI[cod]
            
            url = f"{BASE_URL}competitions/{cod}/matches?status=FINISHED"
            try:
                res = requests.get(url, headers=HEADERS, timeout=12)
                if res.status_code == 200:
                    matches = res.json().get("matches", [])
                    for m in matches:
                        m_id = int(m.get("id"))
                        score = m.get("score", {})
                        full_time = score.get("fullTime", {})
                        h_g = full_time.get("home")
                        a_g = full_time.get("away")
                        if h_g is not None and a_g is not None:
                            risultati_api[m_id] = {"punteggio": f"{h_g}-{a_g}", "h": h_g, "a": a_g}
            except Exception as e:
                print(f"⚠️ Impossibile scaricare storici per campionato {cod}: {str(e)}")

     record_finali = []

    # Sincronizzazione e processamento di OGNI partita del Palinsesto
    for idx, row in df_palinsesto.iterrows():
        try:
            m_id = int(row.get('Match_ID', 0))
        except:
            continue
            
        if m_id == 0:
            continue
            
        nuovo_record = row.copy()
        
        # Se il match è stato trovato tra quelli FINISHED delle API, aggiorniamo il dato reale
        if m_id in risultati_api:
            dati_veri = risultati_api[m_id]
            nuovo_record['Risultato_Reale'] = dati_veri["punteggio"]
            
            # Calcolo esito 1X2 onesto
            segno_reale = "1" if dati_veri["h"] > dati_veri["a"] else ("X" if dati_veri["h"] == dati_veri["a"] else "2")
            pronostico_1x2 = str(row.get('1X2', ''))
            nuovo_record['Esito_1X2'] = "VINCENTE" if segno_reale in pronostico_1x2 else "PERDENTE"
        else:
            # Se non è ancora finito o non refertato, resta nel database in attesa (Nessun dato inventato)
            nuovo_record['Risultato_Reale'] = "NON ANCORA REALE/DA VALIDARE"
            nuovo_record['Esito_1X2'] = "IN ATTESA"

        record_finali.append(nuovo_record)

    if record_finali:
        df_nuovo_storico = pd.DataFrame(record_finali)
        df_nuovo_storico.to_excel(STORICO_FILE, index=False)
        print(f"✅ File {STORICO_FILE} salvato con successo. Righe totali: {len(df_nuovo_storico)}")
    else:
        print("⚠️ Nessun record elaborato.")

if __name__ == "__main__":
    esegui_validazione()
