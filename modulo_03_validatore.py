import pandas as pd
import requests
import os

# --- CONFIGURAZIONE ---
PRONOSTICI_FILE = "Pronostici_App_Betting.xlsx"
OUTPUT_VALIDATO = "Storico_Validato_Betting.xlsx"

MAPPA_COMPETIZIONI = {
    "FIFA World Cup": "WC",
    "Italia_Serie_A": "SA", 
    "Inghilterra_Premier_League": "PL",
    "Spagna_La_Liga": "PD", 
    "Germania_Bundesliga": "BL1",
    "Francia_Ligue_1": "FL1", 
    "Olanda_Eredivisie": "DED",
    "Portogallo_Primeira_Liga": "PPL", 
    "Brasile_Serie_A": "BSA",
    "Inghilterra_Championship": "ELC"
}

def recupera_risultati_api(league_id):
    url = f"https://api.football-data.org/v4/competitions/{league_id}/matches?status=FINISHED"
    headers = {'X-Auth-Token': 'e0ca06c07c634d4fb0950365bd82ffd0'}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            return res.json().get('matches', [])
    except:
        pass
    return []

def esegui_validazione():
    print("\n✅ --- APP BETTING CLOUD - VALIDATORE COMPLETO ---")
    if not os.path.exists(PRONOSTICI_FILE):
        return

    df_prono = pd.read_excel(PRONOSTICI_FILE)
    if df_prono.empty:
        return

    cache_risultati = {}
    righe_validate = []

    for _, riga in df_prono.iterrows():
        camp = riga['Campionato']
        match_str = riga['3. Match']
        
        # Recupero dei Pronostici già esistenti generati dalla Fase 1
        prono_segno = riga.get('1X2', '-')
        prono_esatto = riga.get('Risultato_Esatto', '-')
        prono_dc = riga.get('Doppia_Chance', '-')
        prono_combo = riga.get('DC+U/O2.5', '-')
        prono_uo15 = riga.get('U/O_1.5', '-')
        prono_uo25 = riga.get('U/O_2.5', '-')
        prono_uo35 = riga.get('U/O_3.5', '-')
        prono_gng = riga.get('Goal_NoGoal', '-')
        
        try:
            casa_p, trasf_p = match_str.split(" - ")
            casa_p, trasf_p = casa_p.strip().lower(), trasf_p.strip().lower()
        except:
            continue

        league_id = MAPPA_COMPETIZIONI.get(camp)
        if not league_id:
            continue

        if league_id not in cache_risultati:
            cache_risultati[league_id] = recupera_risultati_api(league_id)

        match_reale = None
        for m in cache_risultati[league_id]:
            casa_r, trasf_r = m['homeTeam']['name'].lower(), m['awayTeam']['name'].lower()
            if ((casa_p in casa_r) or (casa_r in casa_p)) and ((trasf_p in trasf_r) or (trasf_r in trasf_p)):
                match_reale = m
                break

        riga_aggiornata = dict(riga)

        if match_reale and match_reale.get('score', {}).get('fullTime', {}).get('home') is not None:
            g_casa = match_reale['score']['fullTime']['home']
            g_trasf = match_reale['score']['fullTime']['away']
            tot_gol = g_casa + g_trasf

            segno_reale = '1' if g_casa > g_trasf else ('2' if g_trasf > g_casa else 'X')
            
            # Scrittura Esiti nel file Storico
            riga_aggiornata['Risultato_Reale'] = f"{g_casa}-{g_trasf}"
            riga_aggiornata['Esito_1X2'] = 'VINCENTE' if str(prono_segno).strip() == segno_reale else 'PERDENTE'
            riga_aggiornata['Esito_Risultato_Esatto'] = 'VINCENTE' if str(prono_esatto).strip() == f"{g_casa}-{g_trasf}" else 'PERDENTE'
            
            # Doppia Chance
            dc_reale = []
            if segno_reale in ['1', 'X']: dc_reale.append('1X')
            if segno_reale in ['X', '2']: dc_reale.append('X2')
            if segno_reale in ['1', '2']: dc_reale.append('12')
            riga_aggiornata['Esito_Doppia_Chance'] = 'VINCENTE' if str(prono_dc).strip().upper() in dc_reale else 'PERDENTE'
            
            # Goal / NoGoal
            gng_reale = 'GOAL' if (g_casa > 0 and g_trasf > 0) else 'NOGOAL'
            riga_aggiornata['Esito_Goal_NoGoal'] = 'VINCENTE' if str(prono_gng).strip().upper() == gng_reale else 'PERDENTE'
            
            # Under / Over
            riga_aggiornata['Esito_U/O_1.5'] = 'VINCENTE' if (str(prono_uo15).strip().upper() == 'OVER 1.5' and tot_gol > 1.5) or (str(prono_uo15).strip().upper() == 'UNDER 1.5' and tot_gol <= 1.5) else 'PERDENTE'
            riga_aggiornata['Esito_U/O_2.5'] = 'VINCENTE' if (str(prono_uo25).strip().upper() == 'OVER 2.5' and tot_gol > 2.5) or (str(prono_uo25
