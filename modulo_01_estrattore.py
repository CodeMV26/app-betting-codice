import pandas as pd
import requests
import os

# --- CONFIGURAZIONE ---
API_KEY = "e0ca06c07c634d4fb0950365bd82ffd0"
FILE_MASTER = "Database_App_Betting.xlsx"
STAGIONE = "2025"

MAPPA_LEAGUE = {
    "1": ("Italia - Serie A", "SA"),
    "2": ("Inghilterra - Premier League", "PL"),
    "3": ("Spagna - La Liga", "PD"),
    "4": ("Germania - Bundesliga", "BL1"),
    "5": ("Francia - Ligue 1", "FL1"),
    "6": ("Olanda - Eredivisie", "DED"),
    "7": ("Portogallo - Primeira Liga", "PPL"),
    "8": ("Brasile - Serie A", "BSA"),
    "9": ("Inghilterra - Championship", "ELC"),
    "10": ("Mondiali FIFA - World Cup", "WC")
}

def fetch_data(endpoint):
    url = f"https://api.football-data.org/v4/{endpoint}"
    headers = {'X-Auth-Token': API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Errore API: {response.status_code}")

def esegui_estrazione():
    print("\n⚽ --- APP BETTING CLOUD - ESTRATTORE AUTOMATICO ---")
    
    # Carichiamo il dizionario dei fogli esistenti se il file c'è già
    diz_fogli = {}
    if os.path.exists(FILE_MASTER):
        try:
            diz_fogli = pd.read_excel(FILE_MASTER, sheet_name=None, engine='openpyxl')
        except:
            diz_fogli = {}

    # Ciclo automatico su TUTTI i campionati della mappa
    for k, v in MAPPA_LEAGUE.items():
        nome_visualizzato, league_id = v
        nome_foglio = nome_visualizzato.replace(" - ", "_").replace(" ", "_")
        print(f"🔄 Scaricamento automatico: {nome_visualizzato}...")

        try:
            df_classifica = pd.DataFrame()

            if league_id == "WC":
                try:
                    data_classifica = fetch_data(f"competitions/{league_id}/standings")
                    rows_wc = []
                    for standing in data_classifica.get('standings', []):
                        for t in standing.get('table', []):
                            rows_wc.append({
                                'Squadra': t['team']['name'], 'Pt': t['points'], 'G': t['playedGames'],
                                'V': t['won'], 'N': t['draw'], 'P': t['lost'], 'GF': t['goalsFor'], 'GS': t['goalsAgainst'],
                                'Media_GF_Casa': 1.20, 'Media_GS_Casa': 1.00, 'Media_GF_Trasf': 1.10, 'Media_GS_Trasf': 1.00
                            })
                    df_classifica = pd.DataFrame(rows_wc)
                except:
                    df_classifica = pd.DataFrame(columns=['Squadra', 'Media_GF_Casa', 'Media_GS_Casa', 'Media_GF_Trasf', 'Media_GS_Trasf'])
            else:
                data_classifica = fetch_data(f"competitions/{league_id}/standings?season={STAGIONE}")
                tab_total = data_classifica['standings'][0]['table']
                tab_home = data_classifica['standings'][1]['table']
                tab_away = data_classifica['standings'][2]['table']

                rows = []
                for i in range(len(tab_total)):
                    t = tab_total[i]
                    h = tab_home[i]
                    a = tab_away[i]
                    row = {
                        'Squadra': t['team']['name'], 'Pt': t['points'], 'G': t['playedGames'],
                        'V': t['won'], 'N': t['draw'], 'P': t['lost'], 'GF': t['goalsFor'], 'GS': t['goalsAgainst'],
                        'Pt_Casa': h['points'], 'G_Casa': h['playedGames'], 'V_Casa': h['won'], 'N_Casa': h['draw'], 'P_Casa': h['lost'], 'GF_Casa': h['goalsFor'], 'GS_Casa': h['goalsAgainst'],
                        'Pt_Trasf': a['points'], 'G_Trasf': a['playedGames'], 'V_Trasf': a['won'], 'N_Trasf': a['draw'], 'P_Trasf': a['lost'], 'GF_Trasf': a['goalsFor'], 'GS_Trasf': a['goalsAgainst']
                    }
                    row['Media_GF_Casa'] = round(row['GF_Casa'] / row['G_Casa'], 2) if row['G_Casa'] > 0 else 0
                    row['Media_GS_Casa'] = round(row['GS_Casa'] / row['G_Casa'], 2) if row['G_Casa'] > 0 else 0
                    row['Media_GF_Trasf'] = round(row['GF_Trasf'] / row['G_Trasf'], 2) if row['G_Trasf'] > 0 else 0
                    row['Media_GS_Trasf'] = round(row['GS_Trasf'] / row['G_Trasf'], 2) if row['G_Trasf'] > 0 else 0
                    rows.append(row)
                df_classifica = pd.DataFrame(rows)

            endpoint_matches = f"competitions/{league_id}/matches?status=SCHEDULED"
            data_match = fetch_data(endpoint_matches)
            partite = []
            for m in data_match.get('matches', []):
                raw_date = m.get('utcDate', '')
                str_date = str(raw_date.get('utcDate', '')) if isinstance(raw_date, dict) else str(raw_date)
                clean_date = str_date[:16].replace('T', ' ')

                partite.append({
                    'Data': clean_date,
                    'Casa': m['homeTeam']['name'],
                    'Trasferta': m['awayTeam']['name'],
                    'Giornata': m.get('matchday', 1)
                })
            df_partite = pd.DataFrame(partite)

            if not df_classifica.empty:
                diz_fogli[nome_foglio] = df_classifica
            diz_fogli[f"PROSSIME_{league_id}"] = df_partite
            print(f"✅ {nome_visualizzato} completato. Partite trovate: {len(df_partite)}")

        except Exception as e:
            print(f"❌ Errore su {nome_visualizzato}: {str(e)}")

    # Scrittura finale "distruttiva positiva" di tutti i fogli accumulati
    with pd.ExcelWriter(FILE_MASTER, engine='xlsxwriter') as writer:
        for nome, dati in diz_fogli.items():
            dati.to_excel(writer, sheet_name=nome, index=False)
            writer.sheets[nome].set_column(0, 25, 18)
    
    print(f"\n🚀 Estrazione completata con successo! File temporaneo pronto.")

if __name__ == "__main__":
    esegui_estrazione()
