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
        prono_segno = riga.get('PRONOSTICO', riga.get('1X2', '-'))
        prono_uo = riga.get('U/O_2.5', riga.get('U/O 2.5', '-'))
        prono_combo = riga.get('DC+U/O2.5', 'In elaborazione')
        
        try:
            casa_p, trasf_p = match_str.split(" - ")
            casa_p = casa_p.strip().lower()
            trasf_p = trasf_p.strip().lower()
        except:
            riga_err = dict(riga)
            riga_err['Risultato_Reale'] = 'Dato Incompleto'
            riga_err['Esito_1X2'] = 'Dato Incompleto'
            riga_err['Esito_Risultato_Esatto'] = 'Dato Incompleto'
            riga_err['Esito_U/O_2.5'] = 'Dato Incompleto'
            righe_validate.append(riga_err)
            continue

        league_id = MAPPA_COMPETIZIONI.get(camp)
        if not league_id:
            riga_err = dict(riga)
            riga_err['Risultato_Reale'] = 'Camp. Non Mappato'
            riga_err['Esito_1X2'] = 'Camp. Non Mappato'
            riga_err['Esito_Risultato_Esatto'] = 'Camp. Non Mappato'
            riga_err['Esito_U/O_2.5'] = 'Camp. Non Mappato'
            righe_validate.append(riga_err)
            continue

        if league_id not in cache_results_keys := cache_risultati.keys():
            print(f"🔄 Scaricamento risultati reali terminati per {camp}...")
            cache_risultati[league_id] = recupera_risultati_api(league_id)

        match_reale = None
        # BLINDO IL CONFRONTO: Entrambe le squadre devono combaciare per evitare finti abbinamenti
        for m in cache_risultati[league_id]:
            casa_r = m['homeTeam']['name'].lower()
            trasf_r = m['awayTeam']['name'].lower()
            
            check_casa = (casa_p in casa_r) or (casa_r in casa_p)
            check_trasf = (trasf_p in trasf_r) or (trasf_r in trasf_p)
            
            if check_casa and check_trasf:
                match_reale = m
                break

        riga_aggiornata = dict(riga)

        if match_reale and match_reale.get('score', {}).get('fullTime', {}).get('home') is not None:
            g_casa = match_reale['score']['fullTime']['home']
            g_trasf = match_reale['score']['fullTime']['away']
            tot_gol = g_casa + g_trasf

            # 1. Segno Reale e Verifica Pronostico 1X2
            segno_reale = '1' if g_casa > g_trasf else ('2' if g_trasf > g_casa else 'X')
            esito_1x2 = 'VINCENTE' if str(prono_segno).strip() == segno_reale else 'PERDENTE'

            # 2. Under/Over Reale
            uo_reale = 'OVER 2.5' if tot_gol > 2.5 else 'UNDER 2.5'
            esito_uo = 'VINCENTE' if str(prono_uo).strip().upper() == uo_reale else 'PERDENTE'
            
            # 3. Validazione Mercato Combo (DC + U/O 2.5)
            esito_combo = "PERDENTE"
            if prono_combo and prono_combo != "In elaborazione" and "+" in str(prono_combo):
                try:
                    p_dc, p_gol_str = str(prono_combo).split("+")
                    p_dc = p_dc.strip().upper()
                    p_gol_str = p_gol_str.strip().upper()

                    dc_valida = False
                    if p_dc == "1X" and segno_reale in ["1", "X"]: dc_valida = True
                    elif p_dc == "X2" and segno_reale in ["X", "2"]: dc_valida = True
                    elif p_dc == "12" and segno_reale in ["1", "2"]: dc_valida = True

                    gol_valido = False
                    if p_gol_str == "OVER" and tot_gol > 2.5: gol_valido = True
                    elif p_gol_str == "UNDER" and tot_gol <= 2.5: gol_valido = True

                    esito_combo = "VINCENTE" if (dc_valida and gol_valido) else "PERDENTE"
                except:
                    esito_combo = "Errore Analisi"

            # Scrittura colonne allineate rigidamente alle chiavi lette da app.py
            riga_aggiornata['Risultato_Reale'] = f"{g_casa}-{g_trasf}"
            riga_aggiornata['Esito_1X2'] = esito_1x2
            riga_aggiornata['Esito_Risultato_Esatto'] = 'VINCENTE' if riga.get('Risultato_Esatto') == f"{g_casa}-{g_trasf}" else 'PERDENTE'
            riga_aggiornata['Esito_U/O_2.5'] = esito_uo
            riga_aggiornata['Esito DC+U/O2.5'] = esito_combo
        else:
            riga_aggiornata['Risultato_Reale'] = 'NON ANCORA REALE/DA VALIDARE'
            riga_aggiornata['Esito_1X2'] = 'Non Disponibile'
            riga_aggiornata['Esito_Risultato_Esatto'] = 'Non Disponibile'
            riga_aggiornata['Esito_U/O_2.5'] = 'Non Disponibile'
            riga_aggiornata['Esito DC+U/O2.5'] = 'Non Disponibile'
            
        righe_validate.append(riga_aggiornata)

    # Conserva o crea il file storico finale
    df_output = pd.DataFrame(righe_validate)
    df_output.to_excel(OUTPUT_VALIDATO, index=False)
    print(f"💾 Validazione completata con successo! Storico salvato in {OUTPUT_VALIDATO}")

if __name__ == "__main__":
    esegui_validazione()
