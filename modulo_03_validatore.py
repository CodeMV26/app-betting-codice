import requests
import pandas as pd
import os
from datetime import datetime, timedelta, timezone

# Configurazione API Key Football-Data.org
API_KEY = "e0ca06c07c634d4fb0950365bd82ffd0"
BASE_URL = "https://api.football-data.org/v4/"
HEADERS = {"X-Auth-Token": API_KEY}

PALINSESTO_FILE = "Pronostici_App_Betting.xlsx"
STORICO_FILE = "Storico_Validato_Betting.xlsx"

def normalizza_team(nome):
    """Pulisce e standardizza i nomi delle squadre per l'incrocio"""
    if pd.isna(nome):
        return ""
    scarti = ["FC", "FK", "AFC", "AC", "UD", "CD", "REAL", "ATLETICO", "CLUB", "SPORTING", "INTER"]
    n = str(nome).upper()
    for s in scarti:
        n = n.replace(s, "")
    return "".join(e for e in n if e.isalnum()).strip()

def esegui_validazione():
    """
    Modulo 03 - Validatore con Correzione Fuso Orario UTC - Versione 5.59
    Normalizza le date in base al server API per evitare che i match a ridosso
    della mezzanotte vengano scartati dai filtri temporali.
    """
    print("🏆 [FASE 2] Validazione con Allineamento Fuso Orario UTC...")
    
    if not os.path.exists(PALINSESTO_FILE):
        return
        
    df_palinsesto = pd.read_excel(PALINSESTO_FILE)
    if df_palinsesto.empty:
        return

    if '3. Match' in df_palinsesto.columns:
        df_palinsesto = df_palinsesto[df_palinsesto['3. Match'].astype(str).str.upper() != 'NONE VS NONE']

    # --- CORREZIONE FUSO ORARIO ---
    # Usiamo il tempo UTC puro (lo stesso del server di Football-Data)
    oggi_utc = datetime.now(timezone.utc)
    # Allarghiamo a 30 giorni per raccogliere tutto il blocco del Mondiale senza buchi di fuso
    inizio_utc = oggi_utc - timedelta(days=30) 
    
    mappa_risultati = {}
    
    # Chiamate protette con date formattate in UTC
    urls = [
        f"{BASE_URL}matches?dateFrom={inizio_utc.strftime('%Y-%m-%d')}&dateTo={oggi_utc.strftime('%Y-%m-%d')}&status=FINISHED",
        f"{BASE_URL}competitions/WC/matches?status=FINISHED"
    ]
    
    for url in urls:
        try:
            res = requests.get(url, headers=HEADERS, timeout=12)
            if res.status_code == 200:
                data_json = res.json()
                for m in data_json.get("matches", []):
                    h_name = normalizza_team(m.get("homeTeam", {}).get("name"))
                    a_name = normalizza_team(m.get("awayTeam", {}).get("name"))
                    full = m.get("score", {}).get("fullTime", {})
                    hg, ag = full.get("home"), full.get("away")
                    
                    if hg is not None and ag is not None:
                        mappa_risultati[f"{h_name}_{a_name}"] = {"res": f"{hg}-{ag}", "h": hg, "a": ag}
        except Exception as e:
            print(f"Nota connessione: {e}")

    record_convalidati = []

    for idx, row in df_palinsesto.iterrows():
        nuovo = row.copy()
        match_str = str(row.get('3. Match', ''))
        
        parti = match_str.split("vs") if "vs" in match_str else match_str.split("-")
        if len(parti) == 2:
            h_pal = normalizza_team(parti[0])
            a_pal = normalizza_team(parti[1])
            chiave = f"{h_pal}_{a_pal}"
            
            if chiave in mappa_risultati:
                dati = mappa_risultati[chiave]
                hg, ag = dati["h"], dati["a"]
                nuovo['Risultato_Reale'] = dati["res"]
                
                segno_reale = "1" if hg > ag else ("X" if hg == ag else "2")
                nuovo['Esito_1X2'] = "VINCENTE" if segno_reale in str(row.get('1X2', '')) else "PERDENTE"
                nuovo['Esito_Risultato_Esatto'] = "VINCENTE" if dati["res"] == str(row.get('Risultato_Esatto', '')) else "PERDENTE"
                nuovo['Esito_Doppia_Chance'] = "VINCENTE" if segno_reale in str(row.get('Doppia_Chance', '')) else "PERDENTE"
                nuovo['Esito_DC+U/O2.5'] = "PERDENTE"
                nuovo['Esito_U/O_1.5'] = "VINCENTE" if (hg + ag) > 1.5 else "PERDENTE"
                nuovo['Esito_U/O_2.5'] = "VINCENTE" if (hg + ag) > 2.5 else "PERDENTE"
                nuovo['Esito_U/O_3.5'] = "VINCENTE" if (hg + ag) > 3.5 else "PERDENTE"
                
                gng_reale = "GOAL" if (hg > 0 and ag > 0) else "NOGOAL"
                nuovo['Esito_Goal_NoGoal'] = "VINCENTE" if gng_reale in str(row.get('Goal_NoGoal', '')).upper() else "PERDENTE"
                
                nuovo['Esito_Media_Goal_Casa'] = "IN ATTESA"
                nuovo['Esito_Media_Goal_Trasferta'] = "IN ATTESA"
                nuovo['Esito_Media_Goal_Totale'] = "IN ATTESA"
                nuovo['Esito_Corner_1X2'] = "IN ATTESA"
            else:
                nuovo['Risultato_Reale'] = "IN ATTESA"
                nuovo['Esito_1X2'] = "IN ATTESA"
        else:
            nuovo['Risultato_Reale'] = "IN ATTESA"
            nuovo['Esito_1X2'] = "IN ATTESA"
            
        record_convalidati.append(nuovo)

    pd.DataFrame(record_convalidati).to_excel(STORICO_FILE, index=False)
    print("✅ Validazione completata con allineamento orario.")

if __name__ == "__main__":
    esegui_validazione()
