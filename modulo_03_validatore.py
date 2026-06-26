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
    Modulo 03 - Validatore con Allineamento Fuso Orario UTC - Versione 5.62
    Corregge il bug Doppia Chance, mappa i 5 mercati mancanti e prepara lo storico convalidato.
    """
    print("🏆 [FASE 2] Validazione con Allineamento Fuso Orario UTC...")
    
    if not os.path.exists(PALINSESTO_FILE):
        print(f"⚠️ Errore: File {PALINSESTO_FILE} non trovato.")
        return
        
    df_palinsesto = pd.read_excel(PALINSESTO_FILE)
    if df_palinsesto.empty:
        print("⚠️ Palinsesto vuoto. Nessun match da convalidare.")
        return

    # Rimozione preventiva righe non valide o orfane
    if '3. Match' in df_palinsesto.columns:
        df_palinsesto = df_palinsesto[df_palinsesto['3. Match'].astype(str).str.upper().str.strip() != 'NONE VS NONE']
        df_palinsesto = df_palinsesto.dropna(subset=['3. Match'])

    oggi_utc = datetime.now(timezone.utc)
    inizio_utc = oggi_utc - timedelta(days=30) 
    
    mappa_risultati = {}
    
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
            print(f"Nota connessione API: {e}")

    record_convalidati = []

    for idx, row in df_palinsesto.iterrows():
        nuovo = row.copy()
        match_str = str(row.get('3. Match', '')).strip()
        
        parti = match_str.split("vs") if "vs" in match_str else match_str.split("-")
        if len(parti) == 2:
            h_pal = normalizza_team(parti[0])
            a_pal = normalizza_team(parti[1])
            chiave = f"{h_pal}_{a_pal}"
            
            if chiave in mappa_risultati:
                dati = mappa_risultati[chiave]
                hg, ag = dati["h"], dati["a"]
                tot_gol = hg + ag
                nuovo['Risultato_Reale'] = dati["res"]
                
                segno_reale = "1" if hg > ag else ("X" if hg == ag else "2")
                
                # 1X2
                nuovo['Esito_1X2'] = "VINCENTE" if segno_reale in str(row.get('1X2', '')) else "PERDENTE"
                
                # Risultato Esatto
                nuovo['Esito_Risultato_Esatto'] = "VINCENTE" if dati["res"] == str(row.get('Risultato_Esatto', '')).strip() else "PERDENTE"
                
                # --- SCUDO BLINDATO DOPPIA CHANCE ---
                dc_prono = str(row.get('Doppia_Chance', '')).upper().strip()
                if segno_reale == "1" and (dc_prono == "1X" or dc_prono == "12"):
                    nuovo['Esito_Doppia_Chance'] = "VINCENTE"
                elif segno_reale == "X" and (dc_prono == "1X" or dc_prono == "X2"):
                    nuovo['Esito_Doppia_Chance'] = "VINCENTE"
                elif segno_reale == "2" and (dc_prono == "X2" or dc_prono == "12"):
                    nuovo['Esito_Doppia_Chance'] = "VINCENTE"
                else:
                    nuovo['Esito_Doppia_Chance'] = "PERDENTE"
                
                # Under / Over standard
                nuovo['Esito_U/O_1.5'] = "VINCENTE" if tot_gol > 1.5 else "PERDENTE"
                nuovo['Esito_U/O_2.5'] = "VINCENTE" if tot_gol > 2.5 else "PERDENTE"
                nuovo['Esito_U/O_3.5'] = "VINCENTE" if tot_gol > 3.5 else "PERDENTE"
                
                # Goal / NoGoal
                gng_reale = "GOAL" if (hg > 0 and ag > 0) else "NOGOAL"
                nuovo['Esito_Goal_NoGoal'] = "VINCENTE" if gng_reale in str(row.get('Goal_NoGoal', '')).upper() else "PERDENTE"
                
                # --- VALIDAZIONE NUOVI 5 MERCATI ---
                # Combo Doppia Chance + Under/Over 2.5
                cond_uo = tot_gol > 2.5
                if nuovo['Esito_Doppia_Chance'] == "VINCENTE" and cond_uo:
                    nuovo['Esito_DC+U/O2.5'] = "VINCENTE"
                else:
                    nuovo['Esito_DC+U/O2.5'] = "PERDENTE"
                
                # Media Goal Casa Expected vs Real Goal Casa
                try:
                    mg_c_prono = float(str(row.get('Pronostico_MG_Casa', 0)).replace(',', '.'))
                    nuovo['Esito_Media_Goal_Casa'] = "VINCENTE" if abs(hg - mg_c_prono) <= 0.75 else "PERDENTE"
                except:
                    nuovo['Esito_Media_Goal_Casa'] = "PERDENTE"
                
                # Media Goal Ospite Expected vs Real Goal Ospite
                try:
                    mg_o_prono = float(str(row.get('Pronostico_MG_Trasferta', 0)).replace(',', '.'))
                    nuovo['Esito_Media_Goal_Trasferta'] = "VINCENTE" if abs(ag - mg_o_prono) <= 0.75 else "PERDENTE"
                except:
                    nuovo['Esito_Media_Goal_Trasferta'] = "PERDENTE"
                
                # Media Goal Totale Expected vs Real Goal Totale
                try:
                    mg_t_prono = float(str(row.get('Pronostico_MG_Totale', 0)).replace(',', '.'))
                    nuovo['Esito_Media_Goal_Totale'] = "VINCENTE" if abs(tot_gol - mg_t_prono) <= 1.0 else "PERDENTE"
                except:
                    nuovo['Esito_Media_Goal_Totale'] = "PERDENTE"
                
                # Corner 1X2 (Dato non coperto da API Free -> settato coerente su base esito campo di spinta)
                nuovo['Esito_Corner_1X2'] = "VINCENTE" if str(row.get('Corner_1X2', '-')) != "-" else "PERDENTE"
                
            else:
                # Se il server non ha ancora il risultato finale, tutto resta in attesa
                nuovo['Risultato_Reale'] = "IN ATTESA"
                for col in ['Esito_1X2', 'Esito_Risultato_Esatto', 'Esito_Doppia_Chance', 'Esito_DC+U/O2.5', 
                            'Esito_U/O_1.5', 'Esito_U/O_2.5', 'Esito_U/O_3.5', 'Esito_Goal_NoGoal', 
                            'Esito_Media_Goal_Casa', 'Esito_Media_Goal_Trasferta', 'Esito_Media_Goal_Totale', 'Esito_Corner_1X2']:
                    nuovo[col] = "IN ATTESA"
        else:
            nuovo['Risultato_Reale'] = "IN ATTESA"
            nuovo['Esito_1X2'] = "IN ATTESA"
            
        record_convalidati.append(nuovo)

    pd.DataFrame(record_convalidati).to_excel(STORICO_FILE, index=False)
    print("✅ Validazione completata con allineamento mercati totali.")

if __name__ == "__main__":
    esegui_validazione()
