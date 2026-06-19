import pandas as pd
import os
import math
import numpy as np

print("🧠 --- MODULO 02: MOTORE DIXON-COLES & POISSON CON MULTIGOAL DINAMICO ---")

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

if not os.path.exists(DATABASE_FILE):
    print(f"❌ Errore critico: {DATABASE_FILE} non trovato.")
    exit()

df_ingresso = pd.read_excel(DATABASE_FILE)

if df_ingresso.empty or "Nessun match" in str(df_ingresso.iloc[0].get('3. Match', '')):
    print("⚠️ Database vuoto. Genero output pulito.")
    df_ingresso.to_excel(OUTPUT_FILE, index=False)
    exit()

print(f"📊 Calcolo MultiGoal Dinamico su {len(df_ingresso)} match reali...")
righe_pronosticate = []

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

    media_gf_casa_real = float(match_data.get('Media_Goal_Casa', 1.20))
    media_gf_trasf_real = float(match_data.get('Media_Goal_Trasferta', 1.10))
    
    if media_gf_casa_real == 0: media_gf_casa_real = 1.20
    if media_gf_trasf_real == 0: media_gf_trasf_real = 1.10

    sos_c = (media_gf_casa_real / m_h) * 1.05
    sos_t = (media_gf_trasf_real / m_a) * 0.95

    xg_c = ((media_gf_casa_real * 1.00) / m_h) * sos_c * 1.08
    xg_t = ((media_gf_trasf_real * 1.00) / m_a) * sos_t

    matrix = [[0.0 for _ in range(6)] for _ in range(6)]
    for i in range(6):
        for j in range(6):
            p = poisson(xg_c, i) * poisson(xg_t, j)
            adj = 1.12 if i == j else 1.0
            matrix[i][j] = p * dixon_coles_adj(i, j, xg_c, xg_t) * adj

    p1, px, p2, p_u15, p_u25, p_u35, p_goal = 0, 0, 0, 0, 0, 0, 0
    total_p = sum(sum(row) for row in matrix)

    prob_gol_casa = [0.0] * 6
    prob_gol_trasf = [0.0] * 6

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

    probs = {'1': p1, 'X': px, '2': p2}
    prono_s = max(probs, key=probs.get)

    over_leagues = ["Olanda_Eredivisie", "Germania_Bundesliga", "Inghilterra_Premier_League"]
    u25_threshold = 0.47 if nome_campionato in over_leagues else 0.49
    u25_label = "UNDER 2.5" if p_u25 > u25_threshold else "OVER 2.5"

    dc_val = "1X" if (p1 + px) > (p2 + px) else "X2"
    re_idx = np.unravel_index(np.argmax(matrix), (6,6))

    # Valorizzazione mercati
    match_data["1X2"] = prono_s
    match_data["Risultato_Esatto"] = f"{re_idx[0]}-{re_idx[1]}"
    match_data["Doppia_Chance"] = dc_val
    match_data["U/O_1.5"] = "UNDER 1.5" if p_u15 > 0.52 else "OVER 1.5"
    match_data["U/O_2.5"] = u25_label
    match_data["U/O_3.5"] = "UNDER 3.5" if p_u35 > 0.52 else "OVER 3.5"
    match_data["Goal_NoGoal"] = "GOAL" if p_goal > 0.52 else "NOGOAL"
    match_data["DC+U/O2.5"] = f"{dc_val}+{u25_label.split(' ')[0]}"
    match_data["Corner_1X2"] = "1" if xg_c > xg_t + 0.3 else ("2" if xg_t > xg_c + 0.3 else "X")
    
    # Assegnazione colonne MultiGoal separate
    match_data["Pronostico_MG_Casa"] = determina_miglior_multigoal(prob_gol_casa)
    match_data["Pronostico_MG_Trasferta"] = determina_miglior_multigoal(prob_gol_trasf)

    righe_pronosticate.append(match_data)

df_out = pd.DataFrame(righe_pronosticate)

# 🗄️ --- CODA DI SICUREZZA: ARCHIVIAZIONE PRE-MATCH INTEGRALE DELLE API ---
DATABASE_STORICO_GLOBALE = "Database_Storico_Completo.xlsx"

def genera_chiave_univoca_local(row):
    data = str(row.get('Data_Ora_Match', '')).strip()
    match_str = str(row.get('3. Match', '')).strip()
    return f"{data}_{match_str}".lower().replace(" ", "")

if not df_out.empty:
    print("⏳ Memorizzazione preventiva di tutte le colonne statistiche nel Database Storico...")
    
    df_da_appendere = df_out.copy()
    df_da_appendere["Risultato_Reale"] = "NON ANCORA REALE/DA VALIDARE"
    
    if os.path.exists(DATABASE_STORICO_GLOBALE):
        try:
            df_storico_esistente = pd.read_excel(DATABASE_STORICO_GLOBALE)
            
            # Uniformiamo dinamicamente le colonne
            for col in df_da_appendere.columns:
                if col not in df_storico_esistente.columns:
                    df_storico_esistente[col] = None
            for col in df_storico_esistente.columns:
                if col not in df_da_appendere.columns:
                    df_da_appendere[col] = None
            
            # Controllo univoco chiavi
            if not df_storico_esistente.empty:
                chiavi_storico = set(df_storico_esistente.apply(genera_chiave_univoca_local, axis=1))
            else:
                chiavi_storico = set()
                
            nuove_righe_effettive = []
            for _, riga in df_da_appendere.iterrows():
                if genera_chiave_univoca_local(riga) not in chiavi_storico:
                    nuove_righe_effettive.append(riga)
            
            if nuove_righe_effettive:
                df_nuove_inserite = pd.DataFrame(nuove_righe_effettive)
                df_storico_aggiornato = pd.concat([df_storico_esistente, df_nuove_inserite], ignore_index=True)
                df_storico_aggiornato.to_excel(DATABASE_STORICO_GLOBALE, index=False)
                print(f"✅ Storico aggiornato con successo: registrati {len(nuove_righe_effettive)} match con intero patrimonio statistico.")
            else:
                print("📋 Nessun nuovo match inserito: i record correnti sono già blindati nell'archivio.")
                
        except Exception as e:
            print(f"⚠️ Nota di avviso accodamento storico: {e}")
    else:
        try:
            df_da_appendere.to_excel(DATABASE_STORICO_GLOBALE, index=False)
            print("🆕 Archivio Database_Storico_Completo.xlsx non rilevato. Creato un nuovo tracciato globale.")
        except Exception as e:
            print(f"❌ Impossibile inizializzare il Database Storico: {e}")

df_out.to_excel(OUTPUT_FILE, index=False)
print(f"✅ Analisi completata. File {OUTPUT_FILE} generato correttamente.")
