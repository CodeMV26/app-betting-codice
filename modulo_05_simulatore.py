import pandas as pd
import os
import math
import numpy as np

print("🔬 --- MODULO 05: SIMULATORE DI STRATEGIE & BACKTESTING ---")

DATABASE_STORICO = "Database_Storico_Completo.xlsx"

def poisson(l, k):
    if l <= 0: return 1 if k == 0 else 0
    return (math.exp(-l) * pow(l, k)) / math.factorial(k)

def dixon_coles_adj(i, j, xg_c, xg_t, rho=-0.09):
    if i == 0 and j == 0: return 1 - (xg_c * xg_t * rho)
    if i == 1 and j == 0: return 1 + (xg_t * rho)
    if i == 0 and j == 1: return 1 + (xg_c * rho)
    if i == 1 and j == 1: return 1 - rho
    return 1.0

def determina_miglior_multigoal(prob_vettore):
    range_disponibili = {
        "1-2 MG": sum(prob_vettore[1:3]),
        "1-3 MG": sum(prob_vettore[1:4]),
        "1-4 MG": sum(prob_vettore[1:5]),
        "2-3 MG": sum(prob_vettore[2:4]),
        "2-4 MG": sum(prob_vettore[2:5]),
        "3+ MG": sum(prob_vettore[3:]),
        "0-1 MG": sum(prob_vettore[0:2])
    }
    return max(range_disponibili, key=range_disponibili.get)

def esegui_backtest():
    if not os.path.exists(DATABASE_STORICO):
        print(f"❌ Errore: {DATABASE_STORICO} non trovato. Popola prima l'archivio con il Modulo 04.")
        return

    df_storico = pd.read_excel(DATABASE_STORICO)
    tot_matches = len(df_storico)
    if tot_matches == 0:
        print("⚠️ Il database storico è vuoto. Impossibile simulare.")
        return

    print(f"📈 Avvio simulazione su {tot_matches} matches storici archiviati...")

    # =========================================================================
    # CONFIGURAZIONE MODELLI SPECIFICI PER MERCATO (PARAMETRI EDITABILI)
    # Modificando questi parametri qui sotto, cambi le regole del simulatore!
    # =========================================================================
    SOGLIA_UNDER_OVER_15 = 0.52
    SOGLIA_UNDER_OVER_25 = 0.49  # Baseline originale Modulo 02
    SOGLIA_UNDER_OVER_35 = 0.52
    SOGLIA_GOAL_NOGOAL   = 0.52
    
    PESO_MEDIE_CASA      = 1.05  # Modificabile per testare variazioni di peso complessive
    PESO_MEDIE_TRASFERTA = 0.95
    # =========================================================================

    contatori_vincenti = {
        "1X2": 0, "Risultato_Esatto": 0, "Doppia_Chance": 0, "Combo_DC_UO25": 0,
        "UO_15": 0, "UO_25": 0, "UO_35": 0, "Goal_NoGoal": 0,
        "MG_Casa": 0, "MG_Ospite": 0, "Corner_1X2": 0
    }

    for idx, row in df_storico.iterrows():
        res_reale = str(row.get('Risultato_Reale', '-'))
        if "-" not in res_reale or "NON ANCORA" in res_reale:
            continue
        
        g_casa_reali, g_trasf_reali = map(int, res_reale.split("-"))
        tot_gol_reali = g_casa_reali + g_trasf_reali
        segno_reale = '1' if g_casa_reali > g_trasf_reali else ('2' if g_trasf_reali > g_casa_reali else 'X')

        # 1. Estrazione dati statistici di input storici originari
        media_gf_casa = float(row.get('Media_Goal_Casa_Orig', row.get('Media_Goal_Casa', 1.20)))
        media_gf_trasf = float(row.get('Media_Goal_Trasferta_Orig', row.get('Media_Goal_Trasferta', 1.10)))
        
        # Gestione di eventuale testo MultiGoal rimasto sovrascritto
        if isinstance(media_gf_casa, str) or math.isnan(media_gf_casa): media_gf_casa = 1.20
        if isinstance(media_gf_trasf, str) or math.isnan(media_gf_trasf): media_gf_trasf = 1.10

        m_h, m_a = 1.20, 1.10
        sos_c = (media_gf_casa / m_h) * PESO_MEDIE_CASA
        sos_t = (media_gf_trasf / m_a) * PESO_MEDIE_TRASFERTA

        xg_c = ((media_gf_casa * 1.00) / m_h) * sos_c * 1.08
        xg_t = ((media_gf_trasf * 1.00) / m_a) * sos_t

        # 2. Generazione Matrice Dixon-Coles simulata
        matrix = [[0.0 for _ in range(6)] for _ in range(6)]
        for i in range(6):
            for j in range(6):
                p = poisson(xg_c, i) * poisson(xg_t, j)
                adj = 1.12 if i == j else 1.0
                matrix[i][j] = p * dixon_coles_adj(i, j, xg_c, xg_t) * adj

        p1, px, p2, p_u15, p_u25, p_u35, p_goal = 0, 0, 0, 0, 0, 0, 0
        total_p = sum(sum(row) for row in matrix)
        prob_gol_casa, prob_gol_trasf = [0.0] * 6, [0.0] * 6

        for i in range(6):
            for j in range(6):
                prob = matrix[i][j] / total_p
                prob_gol_casa[i] += prob
                prob_gol_trasf[j] += prob
                if i > j: p1 += prob
                elif i == j: px += prob
                else: p2 += prob
                s = i + j
                if s < 1.5: p_u15 += prob
                if s < 2.5: p_u25 += prob
                if s < 3.5: p_u35 += prob
                if i > 0 and j > 0: p_goal += prob

        # 3. APPLICAZIONE MODELLI SPECIFICI SIMULATI SUI SINGOLI MERCATI
        sim_1x2 = max({'1': p1, 'X': px, '2': p2}, key={'1': p1, 'X': px, '2': p2}.get)
        sim_esatto = f"{np.unravel_index(np.argmax(matrix), (6,6))[0]}-{np.unravel_index(np.argmax(matrix), (6,6))[1]}"
        sim_dc = "1X" if (p1 + px) > (p2 + px) else "X2"
        
        # Test Modello Specifico U/O 2.5 basato sulla soglia configurata
        sim_uo25 = "UNDER 2.5" if p_u25 > SOGLIA_UNDER_OVER_25 else "OVER 2.5"
        sim_uo15 = "UNDER 1.5" if p_u15 > SOGLIA_UNDER_OVER_15 else "OVER 1.5"
        sim_uo35 = "UNDER 3.5" if p_u35 > SOGLIA_UNDER_OVER_35 else "OVER 3.5"
        sim_gng  = "GOAL" if p_goal > SOGLIA_GOAL_NOGOAL else "NOGOAL"
        sim_combo = f"{sim_dc}+{sim_uo25.split(' ')[0]}"
        
        sim_mg_casa = determina_miglior_multigoal(prob_gol_casa)
        sim_mg_ospite = determina_miglior_multigoal(prob_gol_trasf)
        sim_corner = "1" if xg_c > xg_t + 0.3 else ("2" if xg_t > xg_c + 0.3 else "X")

        # 4. CONFRONTO DIRETTO E VERIFICA ACCURATEZZA SIMULATA
        if sim_1x2 == segno_reale: contatori_vincenti["1X2"] += 1
        if sim_esatto == res_reale: contatori_vincenti["Risultato_Esatto"] += 1
        if sim_dc in ['1X' if segno_reale in ['1','X'] else ('X2' if segno_reale in ['X','2'] else '12')]: contatori_vincenti["Doppia_Chance"] += 1
        
        if (sim_uo15 == "OVER 1.5" and tot_gol_reali > 1.5) or (sim_uo15 == "UNDER 1.5" and tot_gol_reali <= 1.5): contatori_vincenti["UO_15"] += 1
        if (sim_uo25 == "OVER 2.5" and tot_gol_reali > 2.5) or (sim_uo25 == "UNDER 2.5" and tot_gol_reali <= 2.5): contatori_vincenti["UO_25"] += 1
        if (sim_uo25 == "OVER 3.5" and tot_gol_reali > 3.5) or (sim_uo25 == "UNDER 3.5" and tot_gol_reali <= 3.5): contatori_vincenti["UO_35"] += 1
        if (sim_gng == "GOAL" and g_casa_reali > 0 and g_trasf_reali > 0) or (sim_gng == "NOGOAL" and (g_casa_reali == 0 or g_trasf_reali == 0)): contatori_vincenti["Goal_NoGoal"] += 1
        
        # Convalida MultiGoal d'archivio simulata
        def check_mg(p_str, gol):
            p = p_str.replace("MG","").strip()
            if "-" in p:
                g_min, g_max = map(int, p.split("-"))
                return g_min <= gol <= g_max
            return gol >= 3 if "3+" in p else False

        if check_mg(sim_mg_casa, g_casa_reali): contatori_vincenti["MG_Casa"] += 1
        if check_mg(sim_mg_ospite, g_trasf_reali): contatori_vincenti["MG_Ospite"] += 1
        if sim_combo == row.get('DC+U/O2.5') and row.get('Esito_DC+U/O2.5') == 'VINCENTE': contatori_vincenti["Combo_DC_UO25"] += 1

    # =========================================================================
    # 5. GENERAZIONE DEL REPORT DI RITORNO DELLE PERCENTUALI
    # =========================================================================
    print("\n📊 ==================================================")
    print(f"🎯 REPORT SIMULATORE ACCURATEZZA SU {tot_matches} MATCH STORICI:")
    print("======================================================")
    for mercato, vinti in contatori_vincenti.items():
        acc = (vinti / tot_matches) * 100
        print(f"🔹 {mercato.replace('_',' ')}: {acc:.1f}% ({vinti}/{tot_matches} indovinate)")
    print("======================================================\n")

if __name__ == "__main__":
    esegui_backtest()
