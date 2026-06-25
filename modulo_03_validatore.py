import requests
import pandas as pd
import os

# Configurazione API Key Football-Data.org
API_KEY = "e0ca06c07c634d4fb0950365bd82ffd0"
BASE_URL = "https://api.football-data.org/v4/"
HEADERS = {"X-Auth-Token": API_KEY}

PALINSESTO_FILE = "Pronostici_App_Betting.xlsx"
STORICO_FILE = "Storico_Validato_Betting.xlsx"

MAPPA_CAMPIONATI = {
    "PREMIER LEAGUE": "PL", "SERIE A": "SA", "BUNDESLIGA": "BL1", "LA LIGA": "PD",
    "PRIMERA DIVISION": "PD", "LIGUE 1": "FL1", "EREDIVISIE": "DED", "CHAMPIONSHIP": "ELC",
    "PRIMEIRA LIGA": "PPL", "CAMPEONATO BRASILEIRO SÉRIE A": "BSA", "UEFA CHAMPIONS LEAGUE": "CL"
}

def esegui_validazione():
    """
    Modulo 03: Validatore Universale Garantito - Versione 5.46
    Inclusione totale di tutti i match del Palinsesto per evitare sparizioni.
    Aggiorna i risultati reali da API per i match conclusi.
    """
    print("🏆 [FASE 2] Avvio Validatore ad Inclusione Totale...")
    
    if not os.path.exists(PALINSESTO_FILE):
        print(f"⚠️ Errore critico: {PALINSESTO_FILE} non trovato.")
        return
    
    df_palinsesto = pd.read_excel(PALINSESTO_FILE)
    print(f"📊 Righe totali rilevate nel Palinsesto: {len(df_palinsesto)}")
    
    if df_palinsesto.empty:
        print("⚠️ Palinsesto vuoto. Nessun dato da elaborare.")
        return

    # Identificazione dinamica delle colonne chiave per evitare KeyError
    col_camp = next((c for c in df_palinsesto.columns if "CAMPIONATO" in c.upper()), None)
    col_match = next((c for c in df_palinsesto.columns if "MATCH" in c.upper()), None)
    col_id = next((c for c in df_palinsesto.columns if "ID" in c.upper()), None)

    risultati_api = {}

    # Chiamata API per raccogliere i match terminati
    if col_camp:
        campionati_presenti = df_palinsesto[col_camp].dropna().unique()
        for camp in campionati_presenti:
            cod = str(camp).strip().upper()
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
                print(f"⚠️ Nota: Impossibile scaricare info via API per {cod} ({str(e)}). Procedo in modalità resiliente.")

    record_finali = []

    # Processamento di OGNI singola riga del Palinsesto (Nessuna riga viene scartata)
    for idx, row in df_palinsesto.iterrows():
        # Verifichiamo se la riga è un None vs None spurio
        if col_match and str(row[col_match]).upper() == "NONE VS NONE":
            continue
            
        nuovo_record = row.copy()
        
        # Recupero dell'ID per il match
        m_id = None
        if col_id:
            try:
                m_id = int(row[col_id])
            except:
                m_id = None

        # Controllo incrocio dati con i risultati reali dell'API
        if m_id and m_id in risultati_api:
            dati_veri = risultati_api[m_id]
            nuovo_record['Risultato_Reale'] = dati_veri["punteggio"]
            
            segno_reale = "1" if dati_veri["h"] > dati_veri["a"] else ("X" if dati_veri["h"] == dati_veri["a"] else "2")
            pronostico_1x2 = str(row.get('1X2', ''))
            nuovo_record['Esito_1X2'] = "VINCENTE" if segno_reale in pronostico_1x2 else "PERDENTE"
        else:
            # Se l'API non ha ancora il risultato o il match è futuro, resta in attesa senza sparire
            if pd.isna(row.get('Risultato_Reale')) or str(row.get('Risultato_Reale')).strip() == "" or "NON ANCORA" in str(row.get('Risultato_Reale')).upper():
                nuovo_record['Risultato_Reale'] = "NON ANCORA REALE/DA VALIDARE"
                nuovo_record['Esito_1X2'] = "IN ATTESA"

        record_finali.append(nuovo_record)

    # Salvataggio forzato dei dati
    df_nuovo_storico = pd.DataFrame(record_finali)
    df_nuovo_storico.to_excel(STORICO_FILE, index=False)
    print(f"✅ Archivio {STORICO_FILE} rigenerato correttamente. Righe scritte: {len(df_nuovo_storico)}")

if __name__ == "__main__":
    esegui_validazione()
