import pandas as pd
import requests
import time
from datetime import datetime, timedelta

print("⚽ --- MODULO 01: ESTRATTORE MULTI-GIORNO (OGGI + 4 GIORNI) ---")

URL_API = "https://api.football-data.org/v4/competitions/WC/matches"
headers = {"X-Auth-Token": "3ee7c0a68d0f46ffbc89bfec167ff506"}

partite_reali = []

# Calcoliamo i giorni del range in formato ISO (YYYY-MM-DD)
data_oggi = datetime.now()
date_valide = [(data_oggi + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(5)]

print(f"📅 Range di date analizzato: da {date_valide[0]} a {date_valide[-1]}")

try:
    for tentativo in range(3):
        response = requests.get(URL_API, headers=headers, timeout=15)
        if response.status_code == 200:
            break
        elif response.status_code == 429:
            print("⚠️ Troppe richieste al provider. Attendo 5 secondi e riprovo...")
            time.sleep(5)
        else:
            print(f"⚠️ Errore di risposta del server dati: {response.status_code}")
            break

    if response.status_code == 200:
        data = response.json()
        matches = data.get("matches", [])
        
        for m in matches:
            utc_date = m.get("utcDate", "")
            
            # Verifichiamo se il match rientra in uno dei 5 giorni del range
            if utc_date and any(utc_date.startswith(giorno) for giorno in date_valide):
                try:
                    dt = datetime.strptime(utc_date, "%Y-%m-%dT%H:%M:%SZ")
                    data_ora_formattata = dt.strftime("%d/%m/%Y %H:%M")
                except:
                    data_ora_formattata = utc_date

                partite_reali.append({
                    "Campionato": "FIFA World Cup",
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
        
        print(f"✅ Controllo terminato. Trovati {len(partite_reali)} match reali nel range indicato.")

except Exception as e:
    print(f"❌ Errore critico nel modulo di estrazione: {e}")

if not partite_reali:
    partite_reali.append({
        "Campionato": "Palinsesto",
        "Data_Ora_Match": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "3. Match": "Nessun match in palinsesto nei prossimi 4 giorni",
        "1X2": "-", "Risultato_Esatto": "-", "Doppia_Chance": "-",
        "U/O_1.5": "-", "U/O_2.5": "-", "U/O_3.5": "-", "Goal_NoGoal": "-"
    })

df_Esito = pd.DataFrame(partite_reali)
df_Esito.to_excel("Database_App_Betting.xlsx", index=False)
print("💾 Database_App_Betting.xlsx aggiornato con il nuovo range.")
