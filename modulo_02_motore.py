import pandas as pd
import numpy as np
import os
from scipy.stats import poisson

def calcola_dixon_coles(lambda_casa, mu_ospite, rho=-0.05):
    """
    Applica il modello Dixon-Coles per calcolare la matrice delle probabilità dei punteggi (fino a 5-5).
    Il parametro rho corregge la leggera distorsione statistica sui punteggi bassi (0-0, 1-0, 0-1, 1-1).
    """
    matrice_prob = np.zeros((6, 6))
    for x in range(6):
        for y in range(6):
            prob_p_casa = poisson.pmf(x, lambda_casa)
            prob_p_ospite = poisson.pmf(y, mu_ospite)
            prob_base = prob_p_casa * prob_p_ospite
            
            # Correzione Dixon-Coles per i punteggi più frequenti
            if x == 0 and y == 0:
                fattore = 1 - (lambda_casa * mu_ospite * rho)
            elif x == 1 and y == 0:
                fattore = 1 + (mu_ospite * rho)
            elif x == 0 and y == 1:
                fattore = 1 + (lambda_casa * rho)
            elif x == 1 and y == 1:
                fattore = 1 - rho
            else:
                fattore = 1
                
            matrice_prob[x, y] = prob_base * fattore
            
    # Normalizzazione per sicurezza matematica
    if matrice_prob.sum() > 0:
        matrice_prob /= matrice_prob.sum()
        
    return matrice_prob

def esegui_calcolo_motore():
    """Analizza il file generato dall'estrattore ed elabora le metriche probabilistiche"""
    file_palinsesto = "Pronostici_App_Betting.xlsx"
    
    if not os.path.exists(file_palinsesto):
        return
        
    try:
        df = pd.read_excel(file_palinsesto)
    except Exception:
        return
        
    if df.empty:
        return

    for idx, row in df.iterrows():
        # Calcolo degli Alpha e Beta di attacco/difesa simulati partendo dallo storico gol totali reali
        part_casa = row.get("Giocate_Casa", 10)
        part_ospite = row.get("Giocate_Ospite", 10)
        
        # Prevenzione divisione per zero
        if part_casa == 0: part_casa = 1
        if part_ospite == 0: part_ospite = 1
        
        # Calcolo dei tassi nominali di pericolosità offensiva e difensiva basati su dati storici reali
        att_casa = (row.get("Media_Goal_Casa", 0) / part_casa)
        dif_casa = (row.get("Goal_Subiti_Casa", 0) / part_casa)
        att_ospite = (row.get("Media_Goal_Trasferta", 0) / part_ospite)
        dif_ospite = (row.get("Goal_Subiti_Ospite", 0) / part_ospite)
        
        # Calcolo Lambda e Mu condizionati (forzando un minimo di 0.2 per evitare asfissia matematica)
        lambda_casa = max(att_casa * dif_ospite, 0.2)
        mu_ospite = max(att_ospite * dif_casa, 0.2)
        
        # Generazione della matrice probabilistica 6x6
        matrice = calcola_dixon_coles(lambda_casa, mu_ospite)
        
        # 1. Mercato 1X2
        p_1 = np.sum(np.tril(matrice, -1))
        p_X = np.sum(np.diag(matrice))
        p_2 = np.sum(np.triu(matrice, 1))
        
        esiti_1x2 = ["1", "X", "2"]
        prob_1x2 = [p_1, p_X, p_2]
        df.at[idx, "1X2"] = f"{esiti_1x2[np.argmax(prob_1x2)]} ({max(prob_1x2)*100:.0f}%)"
        
        # 2. Risultato Esatto
        x_max, y_max = np.unravel_index(np.argmax(matrice), matrice.shape)
        df.at[idx, "Risultato_Esatto"] = f"{x_max}-{y_max} ({matrice[x_max, y_max]*100:.0f}%)"
        
        # 3. Doppia Chance
        if (p_1 + p_X) > (p_X + p_2) and (p_1 + p_X) > (p_1 + p_2):
            df.at[idx, "Doppia_Chance"] = f"1X ({ (p_1+p_X)*100 :.0f}%)"
        elif (p_X + p_2) > (p_1 + p_2):
            df.at[idx, "Doppia_Chance"] = f"X2 ({ (p_X+p_2)*100 :.0f}%)"
        else:
            df.at[idx, "Doppia_Chance"] = f"12 ({ (p_1+p_2)*100 :.0f}%)"
            
        # Calcolo probabilistico combinato per Under/Over
        p_under_15 = p_under_25 = p_under_35 = 0.0
        p_goal = 0.0
        
        for x in range(6):
            for y in range(6):
                tot_g = x + y
                if tot_g < 1.5: p_under_15 += matrice[x, y]
                if tot_g < 2.5: p_under_25 += matrice[x, y]
                if tot_g < 3.5: p_under_35 += matrice[x, y]
                if x > 0 and y > 0: p_goal += matrice[x, y]
                
        # 4. Under/Over 1.5
        df.at[idx, "U/O_1.5"] = f"OVER 1.5 ({(1-p_under_15)*100:.0f}%)" if p_under_15 < 0.5 else f"UNDER 1.5 ({p_under_15*100:.0f}%)"
        # 5. Under/Over 2.5
        df.at[idx, "U/O_2.5"] = f"OVER 2.5 ({(1-p_under_25)*100:.0f}%)" if p_under_25 < 0.5 else f"UNDER 2.5 ({p_under_25*100:.0f}%)"
        # 6. Under/Over 3.5
        df.at[idx, "U/O_3.5"] = f"OVER 3.5 ({(1-p_under_35)*100:.0f}%)" if p_under_35 < 0.5 else f"UNDER 3.5 ({p_under_35*100:.0f}%)"
        # 7. Goal / NoGoal
        df.at[idx, "Goal_NoGoal"] = f"GG ({p_goal*100:.0f}%)" if p_goal > 0.5 else f"NG ({(1-p_goal)*100:.0f}%)"
        
        # 8. Combo DC + U/O 2.5
        dc_pref = "1X" if (p_1 + p_X) >= (p_X + p_2) else "X2"
        uo_pref = "OV2.5" if p_under_25 < 0.5 else "UN2.5"
        df.at[idx, "DC+U/O2.5"] = f"{dc_pref}+{uo_pref}"
        
        # 9. Media Goal Espressa (Pronostico Singolo)
        df.at[idx, "Pronostico_MG_Casa"] = round(lambda_casa, 1)
        df.at[idx, "Pronostico_MG_Trasferta"] = round(mu_ospite, 1)
        
        # 10. MG Casa+Ospite (Somma Totale Attesa)
        df.at[idx, "Pronostico_MG_Totale"] = round(lambda_casa + mu_ospite, 1)
        
        # 11. Corner 1X2 (Modello statistico basato sulla spinta offensiva e punti reali)
        punti_c = row.get("Punti_Casa", 0)
        punti_o = row.get("Punti_Trasferta", 0)
        if punti_c > punti_o + 5:
            df.at[idx, "Corner_1X2"] = "1"
        elif punti_o > punti_c + 5:
            df.at[idx, "Corner_1X2"] = "2"
        else:
            df.at[idx, "Corner_1X2"] = "X"

    # Salva il file definitivo con tutti i mercati compilati dal modello Dixon-Coles
    df.to_excel(file_palinsesto, index=False)

if __name__ == "__main__":
    esegui_calcolo_motore()
