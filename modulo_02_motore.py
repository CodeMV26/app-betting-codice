import pandas as pd
import numpy as np
import os
import math

def calcola_poisson_nativo(k, lmbda):
    """Calcola la probabilità di Poisson in modo nativo senza librerie esterne"""
    if lmbda <= 0:
        return 1.0 if k == 0 else 0.0
    return (math.exp(-lmbda) * (lmbda ** k)) / math.factorial(k)

def calcola_dixon_coles(lambda_casa, mu_ospite, rho=-0.05):
    """Applica il modello Dixon-Coles puro per calcolare la matrice delle probabilità."""
    matrice_prob = np.zeros((6, 6))
    for x in range(6):
        for y in range(6):
            prob_p_casa = calcola_poisson_nativo(x, lambda_casa)
            prob_p_ospite = calcola_poisson_nativo(y, mu_ospite)
            prob_base = prob_p_casa * prob_p_ospite
            
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

    # Forzatura del tipo di dato a stringa per evitare conflitti float64
    colonne_testo = ["1X2", "Risultato_Esatto", "Doppia_Chance", "DC+U/O2.5", "U/O_1.5", "U/O_2.5", "U/O_3.5", "Goal_NoGoal", "Corner_1X2"]
    for col in colonne_testo:
        if col in df.columns:
            df[col] = df[col].astype(str)

    for idx, row in df.iterrows():
        part_casa = row.get("Giocate_Casa", 10)
        part_ospite = row.get("Giocate_Ospite", 10)
        
        if part_casa == 0: part_casa = 1
        if part_ospite == 0: part_ospite = 1
        
        att_casa = (row.get("Media_Goal_Casa", 0) / part_casa)
        dif_casa = (row.get("Goal_Subiti_Casa", 0) / part_casa)
        att_ospite = (row.get("Media_Goal_Trasferta", 0) / part_ospite)
        dif_ospite = (row.get("Goal_Subiti_Ospite", 0) / part_ospite)
        
        lambda_casa = max(att_casa * dif_ospite, 0.2)
        mu_ospite = max(att_ospite * dif_casa, 0.2)
        
        matrice = calcola_dixon_coles(lambda_casa, mu_ospite)
        
        p_1 = np.sum(np.tril(matrice, -1))
        p_X = np.sum(np.diag(matrice))
        p_2 = np.sum(np.triu(matrice, 1))
        
        esiti_1x2 = ["1", "X", "2"]
        prob_1x2 = [p_1, p_X, p_2]
        df.at[idx, "1X2"] = f"{esiti_1x2[np.argmax(prob_1x2)]} ({max(prob_1x2)*100:.0f}%)"
        
        x_max, y_max = np.unravel_index(np.argmax(matrice), matrice.shape)
        df.at[idx, "Risultato_Esatto"] = f"{x_max}-{y_max} ({matrice[x_max, y_max]*100:.0f}%)"
        
        if (p_1 + p_X) > (p_X + p_2) and (p_1 + p_X) > (p_1 + p_2):
            df.at[idx, "Doppia_Chance"] = f"1X ({(p_1+p_X)*100:.0f}%)"
        elif (p_X + p_2) > (p_1 + p_2):
            df.at[idx, "Doppia_Chance"] = f"X2 ({(p_X+p_2)*100:.0f}%)"
        else:
            df.at[idx, "Doppia_Chance"] = f"12 ({(p_1+p_2)*100:.0f}%)"
            
        p_under_15 = p_under_25 = p_under_35 = 0.0
        p_goal = 0.0
        
        for x in range(6):
            for y in range(6):
                tot_g = x + y
                if tot_g < 1.5: p_under_15 += matrice[x, y]
                if tot_g < 2.5: p_under_25 += matrice[x, y]
                if tot_g < 3.5: p_under_35 += matrice[x, y]
                if x > 0 and y > 0: p_goal += matrice[x, y]
                
        df.at[idx, "U/O_1.5"] = f"OVER 1.5 ({(1-p_under_15)*100:.0f}%)" if p_under_15 < 0.5 else f"UNDER 1.5 ({p_under_15*100:.0f}%)"
        df.at[idx, "U/O_2.5"] = f"OVER 2.5 ({(1-1-p_under_25)*100:.0f}%)" if p_under_25 < 0.5 else f"UNDER 2.5 ({p_under_25*100:.0f}%)"
        df.at[idx, "U/O_3.5"] = f"OVER 3.5 ({(1-p_under_35)*100:.0f}%)" if p_under_35 < 0.5 else f"UNDER 3.5 ({p_under_35*100:.0f}%)"
        df.at[idx, "Goal_NoGoal"] = f"GG ({p_goal*100:.0f}%)" if p_goal > 0.5 else f"NG ({(1-p_goal)*100:.0f}%)"
        
        dc_pref = "1X" if (p_1 + p_X) >= (p_X + p_2) else "X2"
        uo_pref = "UN2.5" if p_under_25 >= 0.5 else "OV2.5"
        df.at[idx, "DC+U/O2.5"] = f"{dc_pref}+{uo_pref}"
        
        df.at[idx, "Pronostico_MG_Casa"] = round(lambda_casa, 1)
        df.at[idx, "Pronostico_MG_Trasferta"] = round(mu_ospite, 1)
        df.at[idx, "Pronostico_MG_Totale"] = round(lambda_casa + mu_ospite, 1)
        
        punti_c = row.get("Punti_Casa", 0)
        punti_o = row.get("Punti_Trasferta", 0)
        if punti_c > punti_o + 5:
            df.at[idx, "Corner_1X2"] = "1"
        elif punti_o > punti_c + 5:
            df.at[idx, "Corner_1X2"] = "2"
        else:
            df.at[idx, "Corner_1X2"] = "X"

    df.to_excel(file_palinsesto, index=False)

if __name__ == "__main__":
    esegui_calcolo_motore()
