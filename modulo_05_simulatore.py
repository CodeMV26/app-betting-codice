import numpy as np
import pandas as pd
import math

# PROGRESSIVO CHAT: #121 | Data: 28 Giugno 2026 | Ora: 21:37:14
# Versione Progetto: 6.14 | MODULO 05: MOTORE DI BACKTESTING ISOLATO (VERSIONE INTEGRALE)

def poisson_prob(lam, k):
    """Calcola la probabilità di Poisson pura."""
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return (math.exp(-lam) * pow(lam, k)) / math.factorial(k)

def dixon_coles_adjustment(i, j, xg_casa, xg_ospite, rho=-0.09):
    """Applica la correzione di Dixon-Coles per i punteggi bassi (0-0, 1-0, 0-1, 1-1)."""
    if i == 0 and j == 0: return 1 - (xg_casa * xg_ospite * rho)
    if i == 1 and j == 0: return 1 + (xg_ospite * rho)
    if i == 0 and j == 1: return 1 + (xg_casa * rho)
    if i == 1 and j == 1: return 1 - rho
    return 1.0

def calcola_distribuzione_punteggi(xg_casa, xg_ospite):
    """Genera la matrice di probabilità 6x6 corretta per il fattore pareggio."""
    matrice = [[0.0 for _ in range(6)] for _ in range(6)]
    for i in range(6):
        for j in range(6):
            prob = poisson_prob(xg_casa, i) * poisson_prob(xg_ospite, j) * dixon_coles_adjustment(i, j, xg_casa, xg_ospite)
            if i == j:
                prob *= 1.12  # Incremento accoppiamento simmetrico pareggi
            matrice[i][j] = prob
            
    totale = sum(sum(r) for r in matrice)
    if totale > 0:
        matrice = [[cell / totale for cell in row] for row in matrice]
    return matrice

def determina_miglior_multigol(prob_vett):
    """Determina la fascia multigol a massima espressione probabilistica."""
    fasce = {
        "1-2 MG": sum(prob_vett[1:3]),
        "1-3 MG": sum(prob_vett[1:4]),
        "1-4 MG": sum(prob_vett[1:5]),
        "2-3 MG": sum(prob_vett[2:4]),
        "2-4 MG": sum(prob_vett[2:5]),
        "3+ MG": sum(prob_vett[3:]),
        "0-1 MG": sum(prob_vett[0:2])
    }
    return max(fasce, key=fasce.get)

def esegui_simulazione_archivio(df_database, s_uo15, s_uo25, s_uo35, s_gng, peso_casa, peso_trasferta):
    """
    Esegue il ricalcolo matematico massivo di tutto l'archivio storico applicando 
    le nuove soglie e pesi dinamici passati dall'interfaccia utente.
    """
    df_validi = df_database[df_database['Risultato_Reale'].astype(str).str.contains("-")].copy()
    df_validi = df_validi[~df_validi['Risultato_Reale'].astype(str).str.contains("NON ANCORA")]
    
    totale_match = len(df_validi)
    if totale_match == 0:
        return {}, 0
        
    vinti = {
        "1X2": 0, "Ris. Esatto": 0, "Doppia Chance": 0, "Combo DC + U/O": 0,
        "U/O 1.5": 0, "U/O 2.5": 0, "U/O 3.5": 0, "Goal/NoGoal": 0,
        "MG Casa": 0, "MG Ospite": 0, "Corner 1X2": 0
    }
    
    for _, row in df_validi.iterrows():
        res_reale = str(row.get('Risultato_Reale', '0-0')).strip()
        g_casa, g_ospite = map(int, res_reale.split("-"))
        somma_gol = g_casa + g_ospite
        segno_reale = '1' if g_casa > g_ospite else ('2' if g_ospite > g_casa else 'X')
        
        m_gf_c = float(row.get('Media_Goal_Casa_Orig', row.get('Media_Goal_Casa', 1.20)))
        m_gf_t = float(row.get('Media_Goal_Trasferta_Orig', row.get('Media_Goal_Trasferta', 1.10)))
        if math.isnan(m_gf_c): m_gf_c = 1.20
        if math.isnan(m_gf_t): m_gf_t = 1.10
        
        sos_c = (m_gf_c / 1.20) * peso_casa
        sos_t = (m_gf_t / 1.10) * peso_trasferta
        xg_c = ((m_gf_c * 1.00) / 1.20) * sos_c * 1.08
        xg_t = ((m_gf_t * 1.00) / 1.10) * sos_t
        
        matrice = calcola_distribuzione_punteggi(xg_c, xg_t)
        
        p1, px, p2, pu15, pu25, pu35, pgoal = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        prob_c, prob_t = [0.0] * 6, [0.0] * 6
        
        for i in range(6):
            for j in range(6):
                p_cell = matrice[i][j]
                prob_c[i] += p_cell
                prob_t[j] += p_cell
                
                if i > j: p1 += p_cell
                elif i == j: px += p_cell
                else: p2 += p_cell
                
                if (i + j) < 1.5: pu15 += p_cell
                if (i + j) < 2.5: pu25 += p_cell
                if (i + j) < 3.5: pu35 += p_cell
                if i > 0 and j > 0: pgoal += p_cell
                
        prono_1x2 = max({'1': p1, 'X': px, '2': p2}, key={'1': p1, 'X': px, '2': p2}.get)
        prono_ex = f"{np.unravel_index(np.argmax(matrice), (6,6))[0]}-{np.unravel_index(np.argmax(matrice), (6,6))[1]}"
        prono_dc = "1X" if (p1 + px) > (p2 + px) else "X2"
        prono_uo15 = "UNDER 1.5" if pu15 > s_uo15 else "OVER 1.5"
        prono_uo25 = "UNDER 2.5" if pu25 > s_uo25 else "OVER 2.5"
        prono_uo35 = "UNDER 3.5" if pu35 > s_uo35 else "OVER 3.5"
        prono_gng = "GOAL" if pgoal > s_gng else "NOGOAL"
        prono_combo = f"{prono_dc}+{prono_uo25.split(' ')[0]}"
        
        if prono_1x2 == segno_reale: vinti["1X2"] += 1
        if prono_ex == res_reale: vinti["Ris. Esatto"] += 1
        if (prono_dc == "1X" and segno_reale in ['1','X']) or (prono_dc == "X2" and segno_reale in ['X','2']): vinti["Doppia Chance"] += 1
        if (prono_uo15 == "OVER 1.5" and somma_gol > 1.5) or (prono_uo15 == "UNDER 1.5" and somma_gol <= 1.5): vinti["U/O 1.5"] += 1
        if (prono_uo25 == "OVER 2.5" and somma_gol > 2.5) or (prono_uo25 == "UNDER 2.5" and somma_gol <= 2.5): vinti["U/O 2.5"] += 1
        if (prono_uo35 == "OVER 3.5" and somma_gol > 3.5) or (prono_uo35 == "UNDER 3.5" and somma_gol <= 3.5): vinti["U/O 3.5"] += 1
        if (prono_gng == "GOAL" and g_casa > 0 and g_ospite > 0) or (prono_gng == "NOGOAL" and (g_casa == 0 or g_ospite == 0)): vinti["Goal/NoGoal"] += 1
        
        def check_multigol_coerenza(p_str, gol_effettivi):
            p = p_str.replace("MG","").strip()
            if "-" in p:
                g_min, g_max = map(int, p.split("-"))
                return g_min <= gol_effettivi <= g_max
            return gol_effettivi >= 3 if "3+" in p else False

        if check_multigol_coerenza(determina_miglior_multigol(prob_c), g_casa): vinti["MG Casa"] += 1
        if check_multigol_coerenza(determina_miglior_multigol(prob_t), g_ospite): vinti["MG Ospite"] += 1
        
        if prono_combo == row.get('DC+U/O2.5') and row.get('Esito_DC+U/O2.5') == 'VINCENTE': vinti["Combo DC + U/O"] += 1
        if ("1" in row.get('Esito_Corner_1X2', 'X') and xg_c > xg_t + 0.3) or ("2" in row.get('Esito_Corner_1X2', 'X') and xg_t > xg_c + 0.3): vinti["Corner 1X2"] += 1

    risultati_percentuali = {m: f"{(vinti[m]/totale_match)*100:.1f}% ({vinti[m]}/{totale_match})" for m in vinti}
    return risultati_percentuali, totale_match
