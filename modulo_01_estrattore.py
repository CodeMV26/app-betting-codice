import pandas as pd
import requests
import time
from datetime import datetime, timedelta

print("⚽ --- MODULO 01: ESTRATTORE AVANZATO (ORARI ITALIANI E STATISTICHE) ---")

API_KEY = "e0ca06c07c634d4fb0950365bd82ffd0"
headers = {'X-Auth-Token': API_KEY}

# 1. RECUPERO CLASSIFICA PER STATISTICHE SQUADRE
diz_stats = {}
try:
    print("📊 Recupero classifiche per calcolo Medie Gol e Punti...")
    url_standings = "https://api.football-data.org/v4/competitions/WC/standings"
    res_st = requests.get(url_standings, headers=headers, timeout=15)
    
    if res_st.status_code == 200:
        data_st = res_st.json()
        for standing in data_st.get('standings', []):
            for t in standing.get('table', []):
                nome_squadra = t['team']['name']
                g_casa = t.get('home', {}).get('playedGames', 0)
                gf_casa = t.get('home', {}).get('goalsFor', 0)
                g_trasf = t.get('away', {}).get('playedGames', 0)
                gf_trasf = t.get('away', {}).get('goalsFor', 0)
                
                diz_stats[nome_squadra] = {
                    "Punti": t.get('points', 0),
                    "Media_GF_Casa": round(gf_casa / g_casa, 2) if g_casa > 0 else 0.0,
                    "Media_GF_Trasf": round(gf_trasf / g_trasf, 2) if g_trasf > 0 else 0.0
                }
    else:
        print(f"⚠️ Impossibile recuperare classifiche (Codice {res_st.status_code}). Usi valori di default.")
except Exception as e:
    print(f"⚠️ Errore calcolo statistiche: {e}")

# 2. RECUPERO MATCH PROGRAMMATI
URL_API = "https://api.football-data.org/v4/competitions/WC/matches?status=SCHEDULED"
partite_reali = []

data_oggi = datetime.now()
date_valide = [(data_oggi + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(5)]

try:
    response = requests.get(URL_API, headers=headers, timeout=15)
    
    if response.status_code == 200:
        data = response.json()
        matches = data.get("matches", [])
        
        for m in matches:
            utc_date = m.get("utcDate", "")
            
            if utc_date and any(utc_date.startswith(giorno) for giorno in date_valide):
                # CORREZIONE FUSO ORARIO: +2 ore rispetto a UTC (Ora legale italiana)
                try:
                    dt_utc = datetime.strptime(utc_date, "%Y-%m-%dT%H:%M:%SZ")
                    dt_italia = dt_utc + timedelta(hours=2)
                    data_ora_italiana = dt_italia.strftime("%d/%m/%Y %H:%M")
                except:
                    data_ora_italiana = utc_date
                
                squadra_casa = m['homeTeam']['name']
                squadra_trasferta = m['awayTeam']['name']
                
                # Recupero statistiche dai dizionari (se presenti, altrimenti 0)
                stats_casa = diz_stats.get(squadra_casa, {"Punti": 0, "Media_GF_Casa": 0.0, "Media_GF_Trasf": 0.0})
                stats_trasf = diz_stats.get(squadra_trasferta, {"Punti": 0, "Media_GF_Casa": 0.0, "Media_GF_Trasf": 0.0})
                
                partite_reali.append({
                    "Campionato": "FIFA World Cup",
                    "Data_Ora_Match": data_ora_italiana,
                    "3. Match": f"{squadra_casa} - {squadra_trasferta}",
                    "Punti_Casa": stats_casa["Punti"],
                    "Punti_Trasferta": stats_trasf["Punti"],
                    "Media_Goal_Casa": stats_casa["Media_GF_Casa"],
                    "Media_Goal_Trasferta": stats_trasf["Media_GF_Trasf"],
                    "1X2": "In elaborazione",
                    "Risultato_Esatto": "In elaborazione",
                    "Doppia_Chance": "In elaborazione",
                    "U/O_1.5": "In elaborazione",
                    "U/O_2.5": "In elaborazione",
                    "U/O_3.5": "In elaborazione",
                    "Goal_NoGoal": "In elaborazione",
                    "DC+U/O2.5": "In elaborazione",
                    "Corner_1X2": "Non disponibile",
                    "Odds_1X2": "Non disponibile"
                })
        print(f"✅ Trovati {len(partite_reali)} match reali con fuso orario italiano e statistiche.")
except Exception as e:
    print(f"❌ Errore estrazione: {e}")

if not partite_reali:
    partite_reali.append({
        "Campionato": "Palinsesto", "Data_Ora_Match": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "3. Match": "Nessun match nei prossimi 4 giorni", "Punti_Casa": 0, "Punti_Trasferta": 0,
        "Media_Goal_Casa": 0.0, "Media_Goal_Trasferta": 0.0, "1X2": "-", "Risultato_Esatto": "-",
        "Doppia_Chance": "-", "U/O_1.5": "-", "U/O_2.5": "-", "U/O_3.5": "-", "Goal_NoGoal": "-",
        "DC+U/O2.5": "-", "Corner_1X2": "-", "Odds_1X2": "-"
    })

df_Esito = pd.DataFrame(partite_reali)
df_Esito.to_excel("Database_App_Betting.xlsx", index=False)
print("💾 File Database_App_Betting.xlsx salvato con successo.")
