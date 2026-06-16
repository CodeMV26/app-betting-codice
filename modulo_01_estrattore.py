import pandas as pd
import requests
import os
from datetime import datetime

print("⚽ --- MODULO 01: ESTRATTORE REALE ---")

# Utilizziamo la competizione FIFA World Cup (WC) o i campionati attivi in questo momento
URL_API = "https://api.football-data.org/v4/competitions/WC/matches"
headers = {"X-Auth-Token": "LA_TUA_API_KEY"} # Se usi un token, inseriscilo qui

partite_reali = []

try:
    response = requests.get(URL_API, headers=headers, timeout=15)
    
    if response.status_code == 200:
        data = response.json()
        matches = data.get("matches", [])
        
        for m in matches:
            # Filtriamo solo i match programmati o in corso reali
            if m.get("status") in ["SCHEDULED", "TIMED", "LIVE", "IN_PLAY"]:
                # Formattazione rigorosa Data e Ora (Must 4)
                utc_date = m.get("utcDate", "")
                data_ora_formattata = "Da Definire"
                if utc_date:
                    try:
                        dt = datetime.strptime(utc_date, "%Y-%m-%dT%H:%M:%SZ")
                        data_ora_formattata = dt.strftime("%d/%m/%Y %H:%M")
                    except:
                        data_ora_formattata = utc_date

                partite_reali.append({
                    "Campionato": "FIFA World Cup 2026",
                    "Data_Ora_Match": data_ora_formattata,
                    "3. Match": f"{m['homeTeam']['name']} - {m['awayTeam']['name']}",
                    "1X2": "In elaborazione",
                    "Risultato_Esatto": "In elaborazione",
                    "Doppia_Chance": "In elaborazione",
                    "U/O_1.5": "In elaborazione",
                    "U/O_2.5": "In elaborazione",
                    "U/O_3.5": "In elaborazione",
                    "Goal_NoGoal": "In elaborazione"
                })
        print(f"✅ Download completato. Trovati {len(partite_reali)} eventi reali.")
    else:
        print(f"⚠️ Server dati non disponibile (Codice {response.status_code}). Nessun dato alterato.")

except Exception as e:
    print(f"❌ Errore critico di connessione API: {e}")

# Must 1: Onestà assoluta dei dati. Se è vuoto, rimane vuoto.
if partite_reali:
    df_Esito = pd.DataFrame(partite_reali)
else:
    df_Esito = pd.DataFrame(columns=["Campionato", "Data_Ora_Match", "3. Match", "1X2", "Risultato_Esatto", "Doppia_Chance", "U/O_1.5", "U/O_2.5", "U/O_3.5", "Goal_NoGoal"])

df_Esito.to_excel("Database_App_Betting.xlsx", index=False)
print("💾 File Database_App_Betting.xlsx verificato e salvato.")
