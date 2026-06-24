import requests
import pandas as pd
import os
from datetime import datetime, timedelta

# Configurazione API Key Football-Data.org
API_KEY = "TU_API_KEY_QUI"  # Sostituisci con la tua chiave reale
BASE_URL = "https://api.football-data.org/v4/"
HEADERS = {"X-Auth-Token": API_KEY}

# I 12 Campionati blindati dal Direttore
CAMPIONATI = {
    "WC": "FIFA World Cup", "CL": "UEFA Champions League", "BL1": "Bundesliga",
    "DED": "Eredivisie", "FL1": "Ligue 1", "PD": "Primera Division",
    "SA": "Serie A", "PL": "Premier League", "ELC": "Championship",
    "PPL": "Primeira Liga", "BSA": "Campeonato Brasileiro Série A", "CLI": "Copa Libertadores"
}

def ottieni_statistiche_squadre(id_campionato):
    """Estrae la classifica completa con tutti i dati statistici disponibili in API"""
    url = f"{BASE_URL}competitions/{id_campionato}/standings"
    statistiche = {}
    try:
        response = requests.get(url, headers=HEADERS, timeout=12)
        if response.status_code == 200:
            data = response.json()
            standings = data.get("standings", [])
            for stage in standings:
                if stage.get("type") == "TOTAL":
                    for table_row in stage.get("table", []):
                        team_id = table_row["team"]["id"]
                        statistiche[team_id] = {
                            "Punti_Totali": table_row.get("points", 0),
                            "Posizione_Classifica": table_row.get("position", 0),
                            "Partite_Giocate": table_row.get("playedGames", 0),
                            "Vinte": table_row.get("won", 0),
                            "Pareggiate": table_row.get("draw", 0),
                            "Perse": table_row.get("lost", 0),
                            "Goal_Fatti_Tot": table_row.get("goalsFor", 0),
                            "Goal_Subiti_Tot": table_row.get("goalsAgainst", 0),
                            "Differenza_Reti": table_row.get("goalDifference", 0)
                        }
        return statistiche
    except Exception as e:
        print(f"Errore estrazione statistiche per {id_campionato}: {str(e)}")
        return {}

def esegui_estrazione():
    """Scarica in blocco i 12 campionati da oggi a +4 giorni riempiendo tutti i metadati"""
    data_oggi = datetime.now()
    data_fine = data_oggi + timedelta(days=4)
    
    date_from = data_oggi.strftime("%Y-%m-%d")
    date_to = data_fine.strftime("%Y-%m-%d")
    
    lista_match_totale = []
    
    # Ciclo di estrazione massivo sui 12 Campionati
    for cod_camp, nome_camp in CAMPIONATI.items():
        # 1. Scarica le statistiche/classifica del campionato corrente
        stats_campionato = ottieni_statistiche_squadre(cod_camp)
        
        # 2. Scarica i match nel range temporale stabilito
        url_matches = f"{BASE_URL}competitions/{cod_camp}/matches?dateFrom={date_from}&dateTo={date_to}"
        try:
            res = requests.get(url_matches, headers=HEADERS, timeout=12)
            if res.status_code == 200:
                matches_data = res.json().get("matches", [])
                for m in matches_data:
                    id_casa = m["homeTeam"]["id"]
                    id_ospite = m["awayTeam"]["id"]
                    
                    # Recupero dati statistici estratti in precedenza (con fallback a 0)
                    st_casa = stats_campionato.get(id_casa, {})
                    st_ospite = stats_campionato.get(id_ospite, {})
                    
                    match_dict = {
                        "Campionato": nome_camp,
                        "Cod_Campionato": cod_camp,
                        "Match_ID": m.get("id"),
                        "Data_Ora_Match": m.get("utcDate"),
                        "3. Match": f"{m['homeTeam']['name']} - {m['awayTeam']['name']}",
                        "Squadra_Casa": m['homeTeam']['name'],
                        "Squadra_Ospite": m['awayTeam']['name'],
                        
                        # --- DATI STATISTICI INTEGRALI RICHIESTI DAL DIRETTORE ---
                        "Punti_Casa": st_casa.get("Punti_Totali", 0),
                        "Punti_Trasferta": st_ospite.get("Punti_Totali", 0),
                        "PosClassifica_Casa": st_casa.get("Posizione_Classifica", 0),
                        "PosClassifica_Ospite": st_ospite.get("Posizione_Classifica", 0),
                        "Giocate_Casa": st_casa.get("Partite_Giocate", 0),
                        "Giocate_Ospite": st_ospite.get("Partite_Giocate", 0),
                        "Vinte_Casa": st_casa.get("Vinte", 0),
                        "Vinte_Ospite": st_ospite.get("Vinte", 0),
                        "Pareggi_Casa": st_casa.get("Pareggia", 0),
                        "Pareggi_Ospite": st_ospite.get("Pareggi", 0),
                        "Perse_Casa": st_casa.get("Perse", 0),
                        "Perse_Ospite": st_ospite.get("Perse", 0),
                        
                        # Dati Goal per calcoli Dixon-Coles nativi e backup _Orig
                        "Media_Goal_Casa": st_casa.get("Goal_Fatti_Tot", 0),
                        "Media_Goal_Trasferta": st_ospite.get("Goal_Fatti_Tot", 0),
                        "Media_Goal_Casa_Orig": st_casa.get("Goal_Fatti_Tot", 0),
                        "Media_Goal_Trasferta_Orig": st_ospite.get("Goal_Fatti_Tot", 0),
                        "Goal_Subiti_Casa": st_casa.get("Goal_Subiti_Tot", 0),
                        "Goal_Subiti_Ospite": st_ospite.get("Goal_Subiti_Tot", 0),
                        "Diff_Reti_Casa": st_casa.get("Differenza_Reti", 0),
                        "Diff_Reti_Ospite": st_ospite.get("Differenza_Reti", 0),
                        
                        # Inizializzazione colonne Mercati vuote (saranno popolate dal Modulo 02)
                        "1X2": None, "Risultato_Esatto": None, "Doppia_Chance": None, "DC+U/O2.5": None,
                        "U/O_1.5": None, "U/O_2.5": None, "U/O_3.5": None, "Goal_NoGoal": None,
                        "Pronostico_MG_Casa": None, "Pronostico_MG_Trasferta": None, "Pronostico_MG_Totale": None,
                        "Corner_1X2": None
                    }
                    lista_match_totale.append(match_dict)
        except Exception as e:
            print(f"Errore connessione match per {cod_camp}: {str(e)}")
            
    # Scrittura strutturata nel file temporaneo Palinsesto Excel
    df_risultato = pd.DataFrame(lista_match_totale)
    if not df_risultato.empty:
        df_risultato.to_excel("Pronostici_App_Betting.xlsx", index=False)
    else:
        # Genera un file vuoto strutturato per non mandare in crash Streamlit
        pd.DataFrame(columns=["Campionato", "3. Match"]).to_excel("Pronostici_App_Betting.xlsx", index=False)

if __name__ == "__main__":
    esegui_estrazione()
