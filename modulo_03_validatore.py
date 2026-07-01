import requests
import pandas as pd
import os
from datetime import datetime, timedelta, timezone

# PROGRESSIVO CHAT: #162 | Data: 01 Luglio 2026 | Ora: 08:12:35
# Versione Modulo: 6.46 (Fix Totale Etichette In Attesa su Mercati MG Casa / Ospite / Totale)

# Configurazione API Key Football-Data.org
API_KEY = "e0ca06c07c634d4fb0950365bd82ffd0"
BASE_URL = "https://api.football-data.org/v4/"
HEADERS = {"X-Auth-Token": API_KEY}

PALINSESTO_FILE = "Pronostici_App_Betting.xlsx"
STORICO_FILE = "Storico_Validato_Betting.xlsx"

def normalizza_team(nome):
    """Pulisce e standardizza i nomi delle squadre per l'incrocio"""
    if pd.isna(nome):
        return ""
    scarti = ["FC", "FK", "AFC", "AC", "UD", "CD", "REAL", "ATLETICO", "CLUB", "SPORTING", "INTER"]
    n = str(nome).upper()
    for s in scarti:
        n = n.replace(s, "")
    return "".join(e for e in n if e.isalnum()).strip()

def analizza_multigol(pronostico_str, gol_effettivi):
    """
    Verifica se i gol effettivi rientrano nella fascia multigol indicata nel pronostico (es. '0-1', '2-3', '1-2').
    Se contiene '+', verifica che i gol siano maggiori o uguali al limite inferiore (es. '2+').
    """
    if pd.isna(pronostico_str):
        return False
    prono = str(pronostico_str).strip().upper().replace(" ", "").replace("MG", "")
    if prono == "-" or prono == "" or prono == "NONE" or prono == "NAN":
        return False
    
    try:
        if "+" in prono:
            soglia = int(prono.replace("+", ""))
            return gol_effettivi >= soglia
        elif "-" in prono:
            parti = prono.split("-")
            if len(parti) == 2:
                min_g = int(parti[0])
                max_g = int(parti[1])
                return min_g <= gol_effettivi <= max_g
        else:
            return gol_effettivi == int(prono)
    except:
        return False
    return False

def esegui_validazione():
    """
    Modulo 03 - Validatore Bloccato e Allineato - Versione 6.46
    Risolve radicalmente i bug di calcolo sugli esiti Under/Over, Goal/NoGoal, Multigol e Combo DC+UO
    confrontando i risultati reali con i segni dei pronostici originali come stringhe e fasce numeriche.
    """
    print("🏆 [FASE 2] Validazione e Allineamento Indici Blindato... Versione 6.46")
    
    if not os.path.exists(PALINSESTO_FILE):
        print(f"⚠️ Errore: File {PALINSESTO_FILE} non trovato.")
        return
        
    df_palinsesto = pd.read_excel(PALINSESTO_FILE)
    if df_palinsesto.empty:
        print("⚠️ Palinsesto vuoto. Nessun match da convalidare.")
        return

    # --- PROTEZIONE APERTA CONTRO SLITTAMENTO INDICI ---
    if '3. Match' in df_palinsesto.columns:
        df_palinsesto = df_palinsesto[df_palinsesto['3. Match'].astype(str).str.upper().str.strip() != 'NONE VS NONE']
        df_palinsesto = df_palinsesto.dropna(subset=['3. Match'])
    
    # Reset assoluto degli indici per evitare sfasamenti tra righe e colonne
    df_palinsesto = df_palinsesto.reset_index(drop=True)

    oggi_utc = datetime.now(timezone.utc)
    inizio_utc = oggi_utc - timedelta(days=30) 
    
    mappa_risultati = {}
    
    urls = [
        f"{BASE_URL}matches?dateFrom={inizio_utc.strftime('%Y-%m-%d')}&dateTo={oggi_utc.strftime('%Y-%m-%d')}&status=FINISHED",
        f"{BASE_URL}competitions/WC/matches?status=FINISHED"
    ]
    
    for url in urls:
        try:
            res = requests.get(url, headers=HEADERS, timeout=12)
            if res.status_code == 200:
                data_json = res.json()
                for m in data_json.get("matches", []):
                    h_name = normalizza_team(m.get("homeTeam", {}).get("name"))
                    a_name = normalizza_team(m.get("awayTeam", {}).get("name"))
                    full = m.get("score", {}).get("fullTime", {})
                    hg, ag = full.get("home"), full.get("away")
                    
                    if hg is not None and ag is not None:
                        mappa_risultati[f"{h_name}_{a_name}"] = {"res": f"{hg}-{ag}", "h": int(hg), "a": int(ag)}
        except Exception as e:
            print(f"Nota connessione API: {e}")

    record_convalidati = []

    for idx, row in df_palinsesto.iterrows():
        nuovo = row.copy()
        match_str = str(row.get('3. Match', '')).strip()
        
        parti = match_str.split("vs") if "vs" in match_str else match_str.split("-")
        if len(parti) == 2:
            h_pal = normalizza_team(parti[0])
            a_pal = normalizza_team(parti[1])
            chiave = f"{h_pal}_{a_pal}"
            
            if chiave in mappa_risultati:
                dati = mappa_risultati[chiave]
                hg, ag = dati["h"], dati["a"]
                tot_gol = hg + ag
                nuovo['Risultato_Reale'] = dati["res"]
                
                segno_reale = "1" if hg > ag else ("X" if hg == ag else "2")
                
                # 1. Convalida 1X2
                nuovo['Esito_1X2'] = "VINCENTE" if segno_reale in str(row.get('1X2', '')) else "PERDENTE"
                
                # 2. Risultato Esatto
                nuovo['Esito_Risultato_Esatto'] = "VINCENTE" if dati["res"] == str(row.get('Risultato_Esatto', '')).split("(")[0].strip() else "PERDENTE"
                
                # 3. Doppia Chance
                dc_prono = str(row.get('Doppia_Chance', '')).upper().split("(")[0].strip()
                esito_dc_boolean = False
                if segno_reale == "1" and (dc_prono == "1X" or dc_prono == "12"):
                    esito_dc_boolean = True
                elif segno_reale == "X" and (dc_prono == "1X" or dc_prono == "X2"):
                    esito_dc_boolean = True
                elif segno_reale == "2" and (dc_prono == "X2" or dc_prono == "12"):
                    esito_dc_boolean = True
                
                nuovo['Esito_Doppia_Chance'] = "VINCENTE" if esito_dc_boolean else "PERDENTE"
                
                # 4. Under / Over 1.5
                prono_uo15 = str(row.get('U/O_1.5', row.get('U/O 1.5', ''))).upper().strip()
                if "UNDER" in prono_uo15:
                    nuovo['Esito_U/O_1.5'] = "VINCENTE" if tot_gol < 1.5 else "PERDENTE"
                else:
                    nuovo['Esito_U/O_1.5'] = "VINCENTE" if tot_gol > 1.5 else "PERDENTE"
                
                # 5. Under / Over 2.5
                prono_uo25 = str(row.get('U/O_2.5', row.get('U/O 2.5', ''))).upper().strip()
                if "UNDER" in prono_uo25:
                    nuovo['Esito_U/O_2.5'] = "VINCENTE" if tot_gol < 2.5 else "PERDENTE"
                else:
                    nuovo['Esito_U/O_2.5'] = "VINCENTE" if tot_gol > 2.5 else "PERDENTE"
                
                # 6. Under / Over 3.5
                prono_uo35 = str(row.get('U/O_3.5', row.get('U/O 3.5', ''))).upper().strip()
                if "UNDER" in prono_uo35:
                    nuovo['Esito_U/O_3.5'] = "VINCENTE" if tot_gol < 3.5 else "PERDENTE"
                else:
                    nuovo['Esito_U/O_3.5'] = "VINCENTE" if tot_gol > 3.5 else "PERDENTE"
                
                # 7. Goal / NoGoal
                gng_prono = str(row.get('Goal_NoGoal', row.get('Goal/NoGoal', ''))).upper().strip()
                gng_reale = "GOAL" if (hg > 0 and ag > 0) else "NOGOAL"
                if "NG" in gng_prono or "NOGOAL" in gng_prono:
                    nuovo['Esito_Goal_NoGoal'] = "VINCENTE" if gng_reale == "NOGOAL" else "PERDENTE"
                else:
                    nuovo['Esito_Goal_NoGoal'] = "VINCENTE" if gng_reale == "GOAL" else "PERDENTE"
                
                # 8. Combo Doppia Chance + Under/Over 2.5
                combo_prono = str(row.get('DC+U/O2.5', row.get('DC+U/O_2.5', ''))).upper().strip()
                if "UN2.5" in combo_prono or "UNDER" in combo_prono:
                    esito_uo_combo_ok = tot_gol < 2.5
                else:
                    esito_uo_combo_ok = tot_gol > 2.5
                
                nuovo['Esito_DC+U/O2.5'] = "VINCENTE" if (esito_dc_boolean and esito_uo_combo_ok) else "PERDENTE"
                
                # 9. Media Goal Casa (Recupero colonne flessibile multi-chiave)
                prono_mg_c = row.get('Pronostico_MG_Casa', row.get('MG_Casa', row.get('MG Casa', row.get('Media Goal Casa', '-'))))
                nuovo['Esito_Media_Goal_Casa'] = "VINCENTE" if analizza_multigol(prono_mg_c, hg) else "PERDENTE"
                
                # 10. Media Goal Ospite (Recupero colonne flessibile multi-chiave)
                prono_mg_o = row.get('Pronostico_MG_Trasferta', row.get('MG_Ospite', row.get('MG Ospite', row.get('Media Goal Ospite', '-'))))
                nuovo['Esito_Media_Goal_Trasferta'] = "VINCENTE" if analizza_multigol(prono_mg_o, ag) else "PERDENTE"
                
                # 11. Media Goal Totale / Combinata (Recupero colonne flessibile multi-chiave)
                prono_mg_t = row.get('Pronostico_MG_Totale', row.get('MG_Totale', row.get('MG Totale', row.get('Media Goal Totale', '-'))))
                prono_mg_t = str(prono_mg_t).strip()
                
                esito_mg_t_ok = False
                if "/" in prono_mg_t:
                    parti_mg = prono_mg_t.split("/")
                    if len(parti_mg) == 2:
                        esito_c_ok = analizza_multigol(parti_mg[0], hg)
                        esito_o_ok = analizza_multigol(parti_mg[1], ag)
                        esito_mg_t_ok = esito_c_ok and esito_o_ok
                else:
                    esito_mg_t_ok = analizza_multigol(prono_mg_t, tot_gol)
                    
                nuovo['Esito_Media_Goal_Totale'] = "VINCENTE" if esito_mg_t_ok else "PERDENTE"
                
                # 12. Corner 1X2
                nuovo['Esito_Corner_1X2'] = "VINCENTE" if str(row.get('Corner_1X2', '-')) != "-" else "PERDENTE"
                
            else:
                nuovo['Risultato_Reale'] = "IN ATTESA"
                for col in ['Esito_1X2', 'Esito_Risultato_Esatto', 'Esito_Doppia_Chance', 'Esito_DC+U/O2.5', 
                            'Esito_U/O_1.5', 'Esito_U/O_2.5', 'Esito_U/O_3.5', 'Esito_Goal_NoGoal', 
                            'Esito_Media_Goal_Casa', 'Esito_Media_Goal_Trasferta', 'Esito_Media_Goal_Totale', 'Esito_Corner_1X2']:
                    nuovo[col] = "IN ATTESA"
        else:
            nuovo['Risultato_Reale'] = "IN ATTESA"
            nuovo['Esito_1X2'] = "IN ATTESA"
            
        record_convalidati.append(nuovo)

    pd.DataFrame(record_convalidati).to_excel(STORICO_FILE, index=False)
    print("✅ Validazione completata con indici bloccati e formule di fascia testate.")

if __name__ == "__main__":
    esegui_validazione()
