import pandas as pd
import requests
from datetime import datetime, timedelta

print("⚽ --- MODULO 01: ESTRATTORE REALE (MODELLO STRUTTURATO) ---")

# Configurazione presa dal modello funzionante
API_KEY = "e0ca06c07c634d4fb0950365bd82ffd0"
URL_API = "https://api.football-data.org/v4/competitions/WC/matches?status=SCHEDULED"
headers = {'X-Auth-Token': API_KEY}

partite_reali = []

# Calcoliamo i giorni del range richiesto (oggi + 4 giorni)
data_oggi = datetime.now()
date_valide = [(data_oggi + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(5)]
print(f"📅 Range di date richiesto: da {date_valide[0]} a {date_valide[-1]}")

try:
    # Richiesta dati strutturata come nel modello
    response = requests.get(URL_API, headers=headers, timeout=15)
    
    if response.status_code == 200:
        data = response.json()
        matches = data.get("matches", [])
        
        for m in matches:
            utc_date = m.get("utcDate", "")
            
            # Verifichiamo se il match rientra nel range di 5 giorni (oggi + 4)
            if utc_date and any(utc_date.startswith(giorno) for giorno in date_valide):
                try:
                    dt = datetime.strptime(utc_date, "%Y-%m-%dT%H:%M:%SZ")
                    data_ora_formattata = dt.strftime("%d/%m/%Y %H:%M")
                except:
                    data_ora_formattata = utc_date[:16].replace('T', ' ')

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
        
        print(f"✅ Estrazione completata con successo. Match reali trovati nel range: {len(partite_reali)}")
    else:
        print(f"⚠️ Errore risposta API: {response.status_code}")

except Exception as e:
    print(f"❌ Errore durante l'esecuzione del modulo: {e}")

# Nessuna invenzione: se la lista è vuota rimane vuota con la dicitura reale
if not partite_reali:
    partite_reali.append({
        "Campionato": "Palinsesto",
        "Data_Ora_Match": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "3. Match": "Nessun match in palinsesto nei prossimi 4 giorni",
        "1X2": "-", "Risultato_Esatto": "-", "Doppia_Chance": "-",
        "U/O_1.5": "-", "U/O_2.5": "-", "U/O_3.5": "-", "Goal_NoGoal": "-"
    })

# Salvataggio nel file richiesto dalla tua applicazione
df_Esito = pd.DataFrame(partite_reali)
df_Esito.to_excel("Database_App_Betting.xlsx", index=False)
print("💾 File Database_App_Betting.xlsx salvato.")
