import pandas as pd
import os
import math
import numpy as np

# --- CONFIGURAZIONE ---
SORGENTE = "Database_App_Betting.xlsx"
OUTPUT = "Pronostici_App_Betting.xlsx"

MAPPA_FOGLI_PROSSIME = {
    "Italia_Serie_A": "PROSSIME_SA", "Inghilterra_Premier_League": "PROSSIME_PL",
    "Spagna_La_Liga": "PROSSIME_PD", "Germania_Bundesliga": "PROSSIME_BL1",
    "Francia_Ligue_1": "PROSSIME_FL1", "Olanda_Eredivisie": "PROSSIME_DED",
    "Portogallo_Primeira_Liga": "PROSSIME_PPL", "Brasile_Serie_A": "PROSSIME_BSA",
    "Inghilterra_Championship": "PROSSIME_ELC", "Mondiali_FIFA_World_Cup": "PROSSIME_WC"
}

def poisson(l, k):
    if l <= 0: return 1 if k == 0 else 0
    return (math.exp(-l) * pow(l, k)) / math.factorial(k)

def dixon_coles_adj(i, j, xg_c, xg_t, rho=-0.09):
    if i == 0 and j == 0: return 1 - (xg_c * xg_t * rho)
    if i == 1 and j == 0: return 1 + (xg_t * rho)
    if i == 0 and j == 1: return 1 + (xg_c * rho)
    if i == 1 and j == 1: return 1 - rho
    return 1.0

def calcola_analisi_v_x21(casa, trasf, df_c, m_h, m_a, nome_campionato):
    try:
        riga_casa = df_c[df_c['Squadra'].str.strip() == casa.strip()]
        riga_trasf = df_c[df_c['Squadra'].str.strip() == trasf.strip()]
        if riga_casa.empty or riga_trasf.empty: return None
        d_c, d_t = riga_casa.iloc[0], riga_trasf.iloc[0]

        sos_c = (d_c['Media_GF_Casa'] / m_h) * 1.05
        sos_t = (d_t['Media_GF_Trasf'] / m_a) * 0.95

        xg_c = ((d_c['Media_GF_Casa'] * d_t['Media_GS_Trasf']) / m_h) * sos_c * 1.08
        xg_t = ((d_t['Media_GF_Trasf'] * d_c['Media_GS_Casa']) / m_a) * sos_t

        matrix = [[0.0 for _ in range(6)] for _ in range(6)]
        for i in range(6):
            for j in range(6):
                p = poisson(xg_c, i) * poisson(xg_t, j)
                adj = 1.12 if i == j else 1.0
                matrix[i][j] = p * dixon_coles_adj(i, j, xg_c, xg_t) * adj

        p1, px, p2, p_u15, p_u25, p_u35, p_goal = 0, 0, 0, 0, 0, 0, 0
        total_p = sum(sum(row) for row in matrix)

        for i in range(6):
            for j in range(6):
                prob = matrix[i][j] / total_p
                if i > j: p1 += prob
                elif i == j: px += prob
                else: p2 += prob
                s = i + j
                if s < 1.5: p_u15 += prob
                if s < 2.5: p_u25 += prob
                if s < 3.5: p_u35 += prob
                if i > 0 and j > 0: p_goal += prob

        probs = {'1': p1, 'X': px, '2': p2}
        prono_s = max(probs, key=probs.get)

        over_leagues = ["Olanda_Eredivisie", "Germania_Bundesliga", "Inghilterra_Premier_League"]
        u25_threshold = 0.47 if nome_campionato in over_leagues else 0.49
        u25_label = "UNDER 2.5" if p_u25 > u25_threshold else "OVER 2.5"

        dc_val = "1X" if (p1 + px) > (p2 + px) else "X2"
        re_idx = np.unravel_index(np.argmax(matrix), (6,6))

        return {
            'xG_Home': round(xg_c, 2), 'xG_Away': round(xg_t, 2),
            'PRONOSTICO': prono_s, 'Prob_Segno': f"{round(probs[prono_s] * 100)}%",
            'U/O 1.5': "UNDER 1.5" if p_u15 > 0.52 else "OVER 1.5",
            'U/O 2.5': u25_label, 'U/O 3.5': "UNDER 3.5" if p_u35 > 0.52 else "OVER 3.5",
            'Goal/NoGoal': "GOAL" if p_goal > 0.52 else "NOGOAL",
            'Doppia Chance': dc_val, 'Risultato Esatto': f"{re_idx[0]}-{re_idx[1]}",
            'Corner (1X2)': "1" if xg_c > xg_t + 0.3 else ("2" if xg_t > xg_c + 0.3 else "X"),
            'MG Casa': "1-2 MG" if re_idx[0] <= 2 else "3+ MG",
            'MG Ospite': "1-2 MG" if re_idx[1] <= 2 else "3+ MG",
            'DC + U/O 2.5': f"{dc_val} + {u25_label.split(' ')[0]}",
            'Affidabilità': f"{min(int(probs[prono_s] * 240), 100)}%"
        }
    except: return None

def esegui_motore():
    print("\n🧠 --- APP BETTING CLOUD - MOTORE DECISIONALE ---")
    if not os.path.exists(SORGENTE):
        print(f"❌ Errore: File {SORGENTE} non trovato.")
        return

    xls = pd.ExcelFile(SORGENTE)
    fogli_campionato = [f for f in xls.sheet_names if not f.startswith("PROSSIME_")]

    lista_totale = []
    for f in fogli_campionato:
        foglio_target_prossime = MAPPA_FOGLI_PROSSIME.get(f)
        if not foglio_target_prossime or foglio_target_prossime not in xls.sheet_names:
            continue

        print(f"🔄 Calcolo algoritmi per: {f}...")
        df_c = pd.read_excel(SORGENTE, sheet_name=f)
        df_p = pd.read_excel(SORGENTE, sheet_name=foglio_target_prossime)

        m_h = df_c['Media_GF_Casa'].mean() if not df_c['Media_GF_Casa'].empty else 1.20
        m_a = df_c['Media_GF_Trasf'].mean() if not df_c['Media_GF_Trasf'].empty else 1.10

        for _, r_match in df_p.iterrows():
            res = calcola_analisi_v_x21(r_match['Casa'], r_match['Trasferta'], df_c, m_h, m_a, f)
            if res:
                lista_totale.append({
                    'Campionato': f, '2. Data': r_match['Data'], '3. Match': f"{r_match['Casa']} - {r_match['Trasferta']}",
                    **res
                })

    if lista_totale:
        df_out = pd.DataFrame(lista_totale)
        df_out.to_excel(OUTPUT, index=False)
        print(f"\n📊 Calcoli completati! Generati {len(df_out)} pronostici in totale.")
    else:
        print("⚠️ Nessun match elaborato dal motore.")

if __name__ == "__main__":
    esegui_motore()
