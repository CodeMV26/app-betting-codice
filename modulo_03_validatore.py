import requests
import pandas as pd
import os

# Configurazione API Key Football-Data.org
API_KEY = "e0ca06c07c634d4fb0950365bd82ffd0"
BASE_URL = "https://api.football-data.org/v4/"
HEADERS = {"X-Auth-Token": API_KEY}

PALINSESTO_FILE = "Pronostici_App_Betting.xlsx"
STORICO_FILE = "Storico_Validato_Betting.xlsx"

# Mappatura globale per forzare i codici corretti delle API v4
MAPPA_CAMPIONATI = {
    "PREMIER LEAGUE": "PL", "SERIE A": "SA", "BUNDESLIGA": "BL1", "LA LIGA": "PD",
    "PRIMERA DIVISION": "PD", "LIGUE 1": "FL1", "EREDIVISIE": "DED", "CHAMPIONSHIP": "ELC",
    "PRIMEIRA LIGA": "PPL", "CAMPEONATO BRASILEIRO SÉRIE A": "BSA", "UEFA CHAMPIONS LEAGUE": "CL"
}

def esegui_validazione():
    """
    Modulo 03: Convalida Risultati Reali (Fase 2) - Versione 5.45
    Scansione AUTOMATICA totale basata sull'endpoint di competizione.
    Scarica l'intero corso dei match del campionato e ne estrae lo stato reale.
    """
    print("🏆 [FASE 2] Avvio Validazione Automatica a Scansione Competitiva...")
    
    if not os.path.exists(PALINSESTO_FILE):
        print(f"⚠️ Errore: {PALINSESTO_FILE} non trovato.")
        return
    
    df_palinsesto = pd.read_excel(PALINSESTO_FILE)
    if df_palinsesto.empty:
        print("⚠️ Palinsesto vuoto.")
        return

    # Pulizia automatica righe corrotte
    if '3. Match' in df_palinsesto.columns:
        df_palinsesto = df_palinsesto[df_palinsesto['3. Match'].astype(str).str.upper() != 'NONE VS NONE']
        df_palinsesto = df_palinsesto.dropna(subset=['3. Match'])

    # Estrazione dei codici campionato presenti nel palinsesto
    col_camp = None
    for c in df_palinsesto.columns:
        if "CAMPIONATO" in c.upper():
            col_camp = c
            break

    risultati_api = {}

    if col_camp:
        campionati_presenti = df_palinsesto[col_camp].dropna().unique()
        for camp in campionati_presenti:
            cod = str(camp).strip().upper()
            if cod in MAPPA_CAMPIONATI:
                cod = MAPPA_CAMPIONATI[cod]
            
            # Endpoint totale per competizione (senza filtri di stato restrittivi sul server)
            url = f"{BASE_URL}competitions/{cod}/matches"
            try:
                res = requests.get(url, headers=HEADERS, timeout=15)
                if res.status_code == 200:
                    matches = res.json().get("matches", [])
                    for m in matches:
                        # Verifichiamo noi via software se il match è FINISHED
                        if str(m.get("status")).upper() == "FINISHED":
                            m_id = int(m.get("id"))
                            score = m.get("score", {})
                            full_time = score.get("fullTime", {})
                            h_g = full_time.get("home")
                            a_g = full_time.get("away")
                            if h_g is not None and a_g is not None:
                                risultati_api[m_id] = {"punteggio": f"{h_g}-{a_g}", "h": h_g, "a": a_g}
            except Exception as e:
                print(f"⚠️ Errore scansione automatica campionato {cod}: {str(e)}")

    record_finali = []

    # Mappatura e scrittura dati reali
    for idx, row in df_palinsesto.iterrows():
        try:
            m_id = int(row.get('Match_ID', 0))
        except:
            continue
            
        if m_id == 0:
            continue
            
        nuovo_record = row.copy()
        
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
        print(f"✅ File {STORICO_FILE} salvato con successo. Righe totali: {len(df_nuovo_storico)}")
    else:
        print("⚠️ Nessun record elaborato.")

if __name__ == "__main__":
    esegui_validazione()
