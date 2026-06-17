import pandas as pd
import requests
import os

PRONOSTICI_FILE = "Pronostici_App_Betting.xlsx"
OUTPUT_VALIDATO = "Storico_Validato_Betting.xlsx"

MAPPA_COMPETIZIONI = {
    "FIFA World Cup": "WC", "Italia_Serie_A": "SA", "Inghilterra_Premier_League": "PL",
    "Spagna_La_Liga": "PD", "Germania_Bundesliga": "BL1", "Francia_Ligue_1": "FL1", 
    "Olanda_Eredivisie": "DED", "Portogallo_Primeira_Liga": "PPL", "Brasile_Serie_A": "BSA",
    "Inghilterra_Championship": "ELC"
}

def recupera_risultati_api(league_id):
    url = f"https://api.football-data.org/v4/competitions/{league_id}/matches?status=FINISHED"
    headers = {'X-Auth-Token': 'e0ca06c07c634d4fb0950365bd82ffd0'}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200: return res.json().get('matches', [])
    except: pass
    return []

def valida_range_multigoal(prono_str, gol_reali):
    try:
        prono_clean = str(prono_str).strip().replace(" ", "")
        if "-" in prono_clean:
            g_min, g_max = map(int, prono_clean.split("-"))
            return 'VINCENTE' if g_min <= gol_reali <= g_max else 'PERDENTE'
    except: pass
    return 'PERDENTE'

def esegui_validazione():
    print("\n✅ --- VALIDATORE MATEMATICO INTEGRALE (11 MERCATI) ---")
    if not os.path.exists(PRONOSTICI_FILE): return
    df_prono = pd.read_excel(PRONOSTICI_FILE)
    if df_prono.empty: return

    cache_risultati = {}
    righe_validate = []

    for _, riga in df_prono.iterrows():
        camp = riga['Campionato']
        match_str = riga['3. Match']
        
        # Estrazione pronostici originali della Fase 1
        p_1x2 = riga.get('1X2', '-')
        p_esatto = riga.get('Risultato_Esatto', '-')
        p_dc = riga.get('Doppia_Chance', '-')
        p_combo = riga.get('DC+U/O2.5', '-')
        p_uo15 = riga.get('U/O_1.5', '-')
        p_uo25 = riga.get('U/O_2.5', '-')
        p_uo35 = riga.get('U/O_3.5', '-')
        p_gng = riga.get('Goal_NoGoal', '-')
        p_mg_casa = riga.get('Media_Goal_Casa', riga.get('MG_Casa', '-'))
        p_mg_out = riga.get('Media_Goal_Trasferta', riga.get('MG_Ospite', '-'))
        p_corner = riga.get('Corner_1X2', '-')
        
        try:
            casa_p, trasf_p = match_str.split(" - ")
            casa_p, trasf_p = casa_p.strip().lower(), trasf_p.strip().lower()
        except: continue

        league_id = MAPPA_COMPETIZIONI.get(camp)
        if not league_id: continue

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
            g_casa = int(match_reale['score']['fullTime']['home'])
            g_trasf = int(match_reale['score']['fullTime']['away'])
            tot_gol = g_casa + g_trasf
            segno_reale = '1' if g_casa > g_trasf else ('2' if g_trasf > g_casa else 'X')

            riga_aggiornata['Risultato_Reale'] = f"{g_casa}-{g_trasf}"
            
            # 1) Calcoli Matematici Rigorosi (Nessun "In attesa" se terminata)
            riga_aggiornata['Esito_1X2'] = 'VINCENTE' if str(p_1x2).strip() == segno_reale else 'PERDENTE'
            riga_aggiornata['Esito_Risultato_Esatto'] = 'VINCENTE' if str(p_esatto).strip() == f"{g_casa}-{g_trasf}" else 'PERDENTE'
            
            dc_reale = []
            if segno_reale in ['1', 'X']: dc_reale.append('1X')
            if segno_reale in ['X', '2']: dc_reale.append('X2')
            if segno_reale in ['1', '2']: dc_reale.append('12')
            riga_aggiornata['Esito_Doppia_Chance'] = 'VINCENTE' if str(p_dc).strip().upper() in dc_reale else 'PERDENTE'
            
            gng_reale = 'GOAL' if (g_casa > 0 and g_trasf > 0) else 'NOGOAL'
            riga_aggiornata['Esito_Goal_NoGoal'] = 'VINCENTE' if str(p_gng).strip().upper() == gng_reale else 'PERDENTE'
            
            riga_aggiornata['Esito_U/O_1.5'] = 'VINCENTE' if (str(p_uo15).strip().upper() == 'OVER 1.5' and tot_gol > 1.5) or (str(p_uo15).strip().upper() == 'UNDER 1.5' and tot_gol <= 1.5) else 'PERDENTE'
            riga_aggiornata['Esito_U/O_2.5'] = 'VINCENTE' if (str(p_uo25).strip().upper() == 'OVER 2.5' and tot_gol > 2.5) or (str(p_uo25).strip().upper() == 'UNDER 2.5' and tot_gol <= 2.5) else 'PERDENTE'
            riga_aggiornata['Esito_U/O_3.5'] = 'VINCENTE' if (str(p_uo35).strip().upper() == 'OVER 3.5' and tot_gol > 3.5) or (str(p_uo35).strip().upper() == 'UNDER 3.5' and tot_gol <= 3.5) else 'PERDENTE'
            
            riga_aggiornata['Esito_Media_Goal_Casa'] = valida_range_multigoal(p_mg_casa, g_casa)
            riga_aggiornata['Esito_Media_Goal_Trasferta'] = valida_range_multigoal(p_mg_out, g_trasf)
            riga_aggiornata['Esito_DC+U/O2.5'] = 'VINCENTE' if riga_aggiornata['Esito_Doppia_Chance'] == 'VINCENTE' and riga_aggiornata['Esito_U/O_2.5'] == 'VINCENTE' else 'PERDENTE'
            
            # Angoli: Lasciato esplicitamente come 'In attesa' per rispetto del dato mancante nell'API
            riga_aggiornata['Esito_Corner_1X2'] = 'In attesa'
        else:
            riga_aggiornata['Risultato_Reale'] = 'NON ANCORA REALE/DA VALIDARE'
            for k in ['Esito_1X2', 'Esito_Risultato_Esatto', 'Esito_Doppia_Chance', 'Esito_Goal_NoGoal', 'Esito_U/O_1.5', 'Esito_U/O_2.5', 'Esito_U/O_3.5', 'Esito_Media_Goal_Casa', 'Esito_Media_Goal_Trasferta', 'Esito_Corner_1X2', 'Esito_DC+U/O2.5']:
                riga_aggiornata[k] = 'Non Disponibile'
                
        righe_validate.append(riga_aggiornata)

    pd.DataFrame(righe_validate).to_excel(OUTPUT_VALIDATO, index=False)

if __name__ == "__main__":
    esegui_validazione()
