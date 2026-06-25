import requests
import pandas as pd
import os
from datetime import datetime, timedelta

# Configurazione API Key Football-Data.org
API_KEY = "e0ca06c07c634d4fb0950365bd82ffd0"
BASE_URL = "https://api.football-data.org/v4/"
HEADERS = {"X-Auth-Token": API_KEY}

PALINSESTO_FILE = "Pronostici_App_Betting.xlsx"
STORICO_FILE = "Storico_Validato_Betting.xlsx"

def esegui_validazione():
    """
    Modulo 03: Convalida Risultati Reali (Fase 2) - Versione 5.43
    Recupera i match finiti degli ultimi 7 giorni usando il filtro temporale globale API.
    Garantisce l'aggancio dei risultati reali per i match passati nel Palinsesto.
    """
    print("🏆 [FASE 2] Avvio Validazione con Scansione Temporale Storica...")
    
    if not os.path.exists(PALINSESTO_FILE):
        print(f"⚠️ Errore: {PALINSESTO_FILE} non trovato.")
        return
    
    df_palinsesto = pd.read_excel(PALINSESTO_FILE)
    if df_palinsesto.empty:
        print("⚠️ Palinsesto vuoto.")
        return

    # Pulizia righe corrotte
    if '3. Match' in df_palinsesto.columns:
        df_palinsesto = df_palinsesto[df_palinsesto['3. Match'].astype(str).str.upper() != 'NONE VS NONE']
        df_palinsesto = df_palinsesto.dropna(subset=['3. Match'])

    # Configurazione date per recuperare i match finiti nell'ultima settimana
    oggi = datetime.now()
    una_settimana_fa = oggi - timedelta(days=7)
    
    date_from = una_settimana_fa.strftime("%Y-%m-%d")
    date_to = oggi.strftime("%Y-%m-%d")

    # Chiamata API globale sui match finiti nell'intervallo impostato
    risultati_api = {}
    url = f"{BASE_URL}matches?dateFrom={date_from}&dateTo={date_to}&status=FINISHED"
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
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
        else:
            print(f"⚠️ API Info: Status Code {res.status_code}. Tento recupero alternativo.")
    except Exception as e:
        print(f"⚠️ Errore di connessione API: {str(e)}")

    record_finali = []

    # Sincronizzazione e mappatura
    for idx, row in df_palinsesto.iterrows():
        try:
            m_id = int(row.get('Match_ID', 0))
        except:
            continue
            
        if m_id == 0:
            continue
            
        nuovo_record = row.copy()
        
        # Aggancio dei dati se presenti nel blocco storico scaricato
        if m_id in risultati_api:
            dati_veri = risultati_api[m_id]
            nuovo_record['Risultato_Reale'] = dati_veri["punteggio"]
            
            segno_reale = "1" if dati_veri["h"] > dati_veri["a"] else ("X" if dati_veri["h"] == dati_veri["a"] else "2")
            pronostico_1x2 = str(row.get('1X2', ''))
            nuovo_record['Esito_1X2'] = "VINCENTE" if segno_reale in pronostico_1x2 else "PERDENTE"
        else:
            nuovo_record['Risultato_Reale'] = "NON ANCORA REALE/DA VALIDARE"
            nuovo_record['Esito_1X2'] = "IN ATTESA"

        record_finali.append(nuovo_record)

    if record_finali:
        df_nuovo_storico = pd.DataFrame(record_finali)
        df_nuovo_storico.to_excel(STORICO_FILE, index=False)
        print(f"✅ File {STORICO_FILE} salvato. Righe totali: {len(df_nuovo_storico)}")
    else:
        print("⚠️ Nessun record generato.")

if __name__ == "__main__":
    esegui_validazione()
