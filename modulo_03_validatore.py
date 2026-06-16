import pandas as pd
import requests
import os

# --- CONFIGURAZIONE ---
PRONOSTICI_FILE = "Pronostici_App_Betting.xlsx"
OUTPUT_VALIDATO = "Storico_Validato_Betting.xlsx"

# Allineato esattamente con le stringhe prodotte dal Modulo 01
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
    print("\n✅ --- APP BETTING CLOUD - VALIDATORE PRONOSTICI AVANZATO ---")
    if not os.path.exists(PRONOSTICI_FILE):
        print(f"⚠️ Nessun file {PRONOSTICI_FILE} trovato. Salto la validazione.")
        return

    df_prono = pd.read_excel(PRONOSTICI_FILE)
    if df_prono.empty:
        print("⚠️ Il file dei pronostici è vuoto.")
        return

    cache_risultati = {}
    righe_validate = []

    for _, riga in df_prono.iterrows():
        camp = riga['Campionato']
        match_str = riga['3. Match']
        prono_segno = riga.get('PRONOSTICO', '-')
        prono_uo = riga.get('U/O 2.5', '-')
        prono_combo = riga.get('DC+U/O2.5', 'In elaborazione')
        
        try:
            casa_p, trasf_p = match_str.split(" - ")
        except:
            righe_validate.append({**dict(riga), 'Esito 1X2': 'Dato Incompleto', 'Esito U/O': 'Dato Incompleto', 'Esito DC+U/O2.5': 'Dato Incompleto'})
            continue

        league_id = MAPPA_COMPETIZIONI.get(camp)
        if not league_id:
            righe_validate.append({**dict(riga), 'Esito 1X2': 'Campionato Non Mappato', 'Esito U/O': 'Campionato Non Mappato', 'Esito DC+U/O2.5': 'Campionato Non Mappato'})
            continue

        if league_id not in cache_risultati:
            print(f"🔄 Scaricamento risultati reali terminati per {camp}...")
            cache_risultati[league_id] = recupera_risultati_api(league_id)

        match_reale = None
        for m in cache_risultati[league_id]:
            casa_r = m['homeTeam']['name']
            trasf_r = m['awayTeam']['name']
            if casa_p.strip().lower() in casa_r.lower() or casa_r.lower() in casa_p.lower():
                match_reale = m
                break

        riga_aggiornata = dict(riga)

        if match_reale and match_reale.get('score', {}).get('fullTime', {}).get('home') is not None:
            g_casa = match_reale['score']['fullTime']['home']
            g_trasf = match_reale['score']['fullTime']['away']
            tot_gol = g_casa + g_trasf

            # 1. Segno Reale e Doppia Chance Reale
            segno_reale = '1' if g_casa > g_trasf else ('2' if g_trasf > g_casa else 'X')
            esito_1x2 = 'VINCENTE' if str(prono_segno).strip() == segno_reale else 'PERDENTE'

            # 2. Under/Over Reale
            uo_reale = 'OVER 2.5' if tot_gol > 2.5 else 'UNDER 2.5'
            esito_uo = 'VINCENTE' if str(prono_uo).strip() == uo_reale else 'PERDENTE'
            
            # 3. Validazione Mercato Combo (DC + U/O 2.5)
            esito_combo = "Non Disponibile"
            if prono_combo and prono_combo != "In elaborazione" and "+" in str(prono_combo):
                try:
                    p_dc, p_gol = str(prono_combo).split("+")
                    p_dc = p_dc.strip()
                    p_gol = p_gol.strip()

                    # Verifica Doppia Chance
                    dc_valida = False
                    if p_dc == "1X" and segno_reale in ["1", "X"]: dc_valida = True
                    elif p_dc == "X2" and segno_reale in ["X", "2"]: dc_valida = True
                    elif p_dc == "12" and segno_reale in ["1", "2"]: dc_valida = True

                    # Verifica Under/Over
                    gol_valido = False
                    if p_gol == "OVER 2.5" and tot_gol > 2.5: gol_valido = True
                    elif p_gol == "UNDER 2.5" and tot_gol <= 2.5: gol_valido = True

                    esito_combo = "VINCENTE" if (dc_valida and gol_valido) else "PERDENTE"
                except:
                    esito_combo = "Errore Analisi"

            riga_aggiornata['Risultato Reale'] = f"{g_casa}-{g_trasf}"
            riga_aggiornata['Esito 1X2'] = esito_1x2
            riga_aggiornata['Esito U/O 2.5'] = esito_uo
            riga_aggiornata['Esito DC+U/O2.5'] = esito_combo
        else:
            riga_aggiornata['Risultato Reale'] = "In Attesa"
            riga_aggiornata['Esito 1X2'] = "Non Disponibile"
            riga_aggiornata['Esito U/O 2.5'] = "Non Disponibile"
            riga_aggiornata['Esito DC+U/O2.5'] = "Non Disponibile"
            
        righe_validate.append(riga_aggiornata)

    df_output = pd.DataFrame(righe_validate)
    df_output.to_excel(OUTPUT_VALIDATO, index=False)
    print(f"💾 Validazione completata! Storico salvato in {OUTPUT_VALIDATO}")

if __name__ == "__main__":
    esegui_validazione()
