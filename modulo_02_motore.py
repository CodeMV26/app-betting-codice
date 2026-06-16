import pandas as pd
import os
import math
import numpy as np
from datetime import datetime

print("🧠 --- MODULO 02: ANIMA DELL'APP - MOTORE DIXON-COLES & POISSON ---")

DATABASE_FILE = "Database_App_Betting.xlsx"
OUTPUT_FILE = "Pronostici_App_Betting.xlsx"

def poisson(l, k):
    if l <= 0: return 1 if k == 0 else 0
    return (math.exp(-l) * pow(l, k)) / math.factorial(k)

def dixon_coles_adj(i, j, xg_c, xg_t, rho=-0.09):
    if i == 0 and j == 0: return 1 - (xg_c * xg_t * rho)
    if i == 1 and j == 0: return 1 + (xg_t * rho)
    if i == 0 and j == 1: return 1 + (xg_c * rho)
    if i == 1 and j == 1: return 1 - rho
    return 1.0

if not os.path.exists(DATABASE_FILE):
    print(f"❌ Errore critico: {DATABASE_FILE} non trovato dal server. Avvia la Fase 1.")
    exit()

df_ingresso = pd.read_excel(DATABASE_FILE)

# Protezione: Se il database contiene il messaggio di palinsesto vuoto, genera un file vuoto coerente
if df_ingresso.empty or "Nessun match" in str(df_ingresso.iloc[0].get('3. Match', '')):
    print("⚠️ Database di partenza vuoto o nessun match reale. Genero pronostico pulito.")
    df_ingresso.to_excel(OUTPUT_FILE, index=False)
    exit()

print(f"📊 Calcolo probabilistico avanzato in corso su {len(df_ingresso)} match reali...")
righe_pronosticate = []

# Medie globali di default storiche del tuo algoritmo se mancano dati complessi
m_h = 1.20
m_a = 1.10

for idx, riga in df_ingresso.iterrows():
    match_data = dict(riga)
    match_str = match_data.get('3. Match', '')
    nome_campionato = match_data.get('Campionato', 'FIFA World Cup')
    
    try:
        casa, trasf = match_str.split(" - ")
    except:
        continue

    # Recupero delle medie estratte in tempo reale dal Modulo 01
    media_gf_casa_real = float(match_data.get('Media_Goal_Casa', 1.20))
    media_gf_trasf_real = float(match_data.get('Media_Goal_Trasferta', 1.10))
    
    # Se il Modulo 01 ha estratto 0.0 (es. inizio torneo), usiamo i pesi del modello primario
    if media_gf_casa_real == 0: media_gf_casa_real = 1.20
    if media_gf_trasf_real == 0: media_gf_trasf_real = 1.10

    # --- APPLICAZIONE ALGORITMO MATEMATICO PURO (DIXON-COLES) ---
    sos_c = (media_gf_casa_real / m_h) * 1.05
    sos_t = (media_gf_trasf_real / m_a) * 0.95

    xg_c = ((media_gf_casa_real * 1.00) / m_h) * sos_c * 1.08  # Sincronizzato con logica di attacco/difesa specchiata
    xg_t = ((media_gf_trasf_real * 1.00) / m_a) * sos_t

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

    # --- MAPPATURA STRUTTURATA E INTEGRATA SUL DATABASE CLOUD ---
    match_data["1X2"] = prono_s
    match_data["PRONOSTICO"] = prono_s  # Per allineamento con modulo 03 Validatore
    match_data["Risultato_Esatto"] = f"{re_idx[0]}-{re_idx[1]}"
    match_data["Doppia_Chance"] = dc_val
    match_data["U/O_1.5"] = "UNDER 1.5" if p_u15 > 0.52 else "OVER 1.5"
    match_data["U/O_2.5"] = u25_label
    match_data["U/O 2.5"] = u25_label  # Per allineamento con modulo 03 Validatore
    match_data["U/O_3.5"] = "UNDER 3.5" if p_u35 > 0.52 else "OVER 3.5"
    match_data["Goal_NoGoal"] = "GOAL" if p_goal > 0.52 else "NOGOAL"
    
    # Inserimento dei nuovi mercati richiesti integrati nell'algoritmo primario
    match_data["DC+U/O2.5"] = f"{dc_val}+{u25_label.split(' ')[0]}"
    match_data["Corner_1X2"] = "1" if xg_c > xg_t + 0.3 else ("2" if xg_t > xg_c + 0.3 else "X")
    match_data["Media_Goal_Casa"] = f"{round(xg_c, 2)} xG"
    match_data["Media_Goal_Trasferta"] = f"{round(xg_t, 2)} xG"
    match_data["Odds_1X2"] = match_data.get("Odds_1X2", "Non disponibile")

    righe_pronosticate.append(match_data)

df_out = pd.DataFrame(righe_pronosticate)
df_out.to_excel(OUTPUT_FILE, index=False)
print(f"✅ Analisi completata. File {OUTPUT_FILE} generato preservando il modello matematico originario.")
