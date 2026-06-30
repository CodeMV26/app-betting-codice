import pandas as pd
import numpy as np
import os
import math

# PROGRESSIVO CHAT: #159 | Data: 30 Giugno 2026 | Ora: 21:54:10
# Versione Progetto: 6.43 (Ripristino Integrale dei 9 Mercati Statistici + Fix Dtype)

PALINSESTO_FILE = "Pronostici_App_Betting.xlsx"

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

def calcola_fascia_multigol(media_gol):
    """Genera la stringa di fascia multigol standard basata sulla media matematica"""
    try:
        val = float(media_gol)
    except:
        val = 1.2
    
    if val < 0.85:
        return "0-1 MG"
    elif val < 1.65:
        return "1-2 MG"
    elif val < 2.45:
        return "1-3 MG"
    else:
        return "2-4 MG"

def esegui_calcolo_motore():
    if not os.path.exists(PALINSESTO_FILE):
        return
    
    try:
        # Legge il file Excel generato dall'estrattore
        df = pd.read_excel(PALINSESTO_FILE)
    except:
        return

    if df.empty:
        return

    # Elenco completo di tutte le colonne di output destinate alla UI Mobile
    colonne_testo = [
        "1X2", "Risultato_Esatto", "Doppia_Chance", "DC+U/O2.5", 
        "U/O_1.5", "U/O_2.5", "U/O_3.5", "Goal_NoGoal", "Corner_1X2",
        "Pronostico_MG_Casa", "MG_Casa", "MG Casa",
        "Pronostico_MG_Trasferta", "MG_Ospite", "MG Ospite",
        "Pronostico_MG_Totale", "MG_Totale", "MG Totale"
    ]
    
    # Inizializzazione sicura e forzatura a stringa per evitare conflitti con caratteri speciali (es. '+')
    for col in colonne_testo:
        if col not in df.columns:
            df[col] = "-"
        else:
            df[col] = df[col].astype(str)

    for idx, row in df.iterrows():
        # Estrazione e normalizzazione sicura dei dati storici numerici di input
        part_casa = pd.to_numeric(row.get("Giocate_Casa", 10), errors='coerce')
        part_ospite = pd.to_numeric(row.get("Giocate_Ospite", 10), errors='coerce')
        
        if pd.isna(part_casa) or part_casa <= 0: part_casa = 1
        if pd.isna(part_ospite) or part_ospite <= 0: part_ospite = 1
        
        media_goal_casa = pd.to_numeric(row.get("Media_Goal_Casa", 0), errors='coerce')
        goal_subiti_casa = pd.to_numeric(row.get("Goal_Subiti_Casa", 0), errors='coerce')
        media_goal_ospite = pd.to_numeric(row.get("Media_Goal_Trasferta", 0), errors='coerce')
        goal_subiti_ospite = pd.to_numeric(row.get("Goal_Subiti_Ospite", 0), errors='coerce')
        
        if pd.isna(media_goal_casa): media_goal_casa = 0
        if pd.isna(goal_subiti_casa): goal_subiti_casa = 0
        if pd.isna(media_goal_ospite): media_goal_ospite = 0
        if pd.isna(goal_subiti_ospite): goal_subiti_ospite = 0

        att_casa = media_goal_casa / part_casa
        dif_casa = goal_subiti_casa / part_casa
        att_ospite = media_goal_ospite / part_ospite
        dif_ospite = goal_subiti_ospite / part_ospite
        
        # Calcolo dei parametri Lambda e Mu per la matrice di Dixon-Coles
        lambda_casa = max(att_casa * dif_ospite, 0.2)
        mu_ospite = max(att_ospite * dif_casa, 0.2)
        
        matrice = calcola_dixon_coles(lambda_casa, mu_ospite)
        
        # 1. Calcolo Mercato 1X2
        p_1 = np.sum(np.tril(matrice, -1))
        p_X = np.sum(np.diag(matrice))
        p_2 = np.sum(np.triu(matrice, 1))
        
        esiti_1x2 = ["1", "X", "2"]
        prob_1x2 = [p_1, p_X, p_2]
        df.at[idx, "1X2"] = f"{esiti_1x2[np.argmax(prob_1x2)]} ({max(prob_1x2)*100:.0f}%)"
        
        # 2. Calcolo Mercato Risultato Esatto
        x_max, y_max = np.unravel_index(np.argmax(matrice), matrice.shape)
        df.at[idx, "Risultato_Esatto"] = f"{x_max}-{y_max} ({matrice[x_max, y_max]*100:.0f}%)"
        
        # 3. Calcolo Mercato Doppia Chance
        if (p_1 + p_X) > (p_X + p_2) and (p_1 + p_X) > (p_1 + p_2):
            df.at[idx, "Doppia_Chance"] = f"1X ({(p_1+p_X)*100:.0f}%)"
        elif (p_X + p_2) > (p_1 + p_2):
            df.at[idx, "Doppia_Chance"] = f"X2 ({(p_X+p_2)*100:.0f}%)"
        else:
            df.at[idx, "Doppia_Chance"] = f"12 ({(p_1+p_2)*100:.0f}%)"
            
        # 4. Calcolo Mercati Under/Over e Goal/NoGoal
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
        df.at[idx, "U/O_2.5"] = f"OVER 2.5 ({(1-p_under_25)*100:.0f}%)" if p_under_25 < 0.5 else f"UNDER 2.5 ({p_under_25*100:.0f}%)"
        df.at[idx, "U/O_3.5"] = f"OVER 3.5 ({(1-p_under_35)*100:.0f}%)" if p_under_35 < 0.5 else f"UNDER 3.5 ({p_under_35*100:.0f}%)"
        df.at[idx, "Goal_NoGoal"] = f"GG ({p_goal*100:.0f}%)" if p_goal > 0.5 else f"NG ({(1-p_goal)*100:.0f}%)"
        
        # 5. Calcolo Mercato Combo DC + U/O 2.5
        dc_pref = "1X" if (p_1 + p_X) >= (p_X + p_2) else "X2"
        uo_pref = "UN2.5" if p_under_25 >= 0.5 else "OV2.5"
        df.at[idx, "DC+U/O2.5"] = f"{dc_pref}+{uo_pref}"
        
        # 6. Calcolo Mercati MultiGoal (Fasce testuali protette)
        mg_casa_attesa = row.get('Media_Goal_Casa_Orig', 1.2)
        mg_ospite_attesa = row.get('Media_Goal_Trasferta_Orig', 1.1)
        
        fascia_casa = calcola_fascia_multigol(mg_casa_attesa)
        fascia_ospite = calcola_fascia_multigol(mg_ospite_attesa)
        
        df.at[idx, 'Pronostico_MG_Casa'] = fascia_casa
        df.at[idx, 'MG_Casa'] = fascia_casa
        df.at[idx, 'MG Casa'] = fascia_casa
        
        df.at[idx, 'Pronostico_MG_Trasferta'] = fascia_ospite
        df.at[idx, 'MG_Ospite'] = fascia_ospite
        df.at[idx, 'MG Ospite'] = fascia_ospite
        
        fascia_combinata = f"{fascia_casa.replace(' MG','')} / {fascia_ospite.replace(' MG','')}"
        df.at[idx, 'Pronostico_MG_Totale'] = fascia_combinata
        df.at[idx, 'MG_Totale'] = fascia_combinata
        df.at[idx, 'MG Totale'] = fascia_combinata
        
        # 7. Calcolo Mercato Corner 1X2
        punti_c = pd.to_numeric(row.get("Punti_Casa", 0), errors='coerce')
        punti_o = pd.to_numeric(row.get("Punti_Trasferta", 0), errors='coerce')
        if pd.isna(punti_c): punti_c = 0
        if pd.isna(punti_o): punti_o = 0
            
        if punti_c > punti_o + 5:
            df.at[idx, "Corner_1X2"] = "1"
        elif punti_o > punti_c + 5:
            df.at[idx, "Corner_1X2"] = "2"
        else:
            df.at[idx, "Corner_1X2"] = "X"

    # Sovrascrittura protetta del file Excel
    df.to_excel(PALINSESTO_FILE, index=False)

if __name__ == "__main__":
    esegui_calcolo_motore()
