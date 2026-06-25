import requests
import pandas as pd
import os

# Configurazione API Key Football-Data.org
API_KEY = "e0ca06c07c634d4fb0950365bd82ffd0"
BASE_URL = "https://api.football-data.org/v4/"
HEADERS = {"X-Auth-Token": API_KEY}

PALINSESTO_FILE = "Pronostici_App_Betting.xlsx"
STORICO_FILE = "Storico_Validato_Betting.xlsx"

def esegui_validazione():
    """
    Modulo 03: Validatore Real-Time ID Specifico - Versione 5.47
    Elimina i match None-None all'origine.
    Interroga l'API direttamente sull'ID del singolo match per forzare la validazione automatica.
    """
    print("🏆 [FASE 2] Avvio Validatore Real-Time Automatico...")
    
    if not os.path.exists(PALINSESTO_FILE):
        print(f"⚠️ Errore critico: {PALINSESTO_FILE} non trovato.")
        return
    
    df_palinsesto = pd.read_excel(PALINSESTO_FILE)
    if df_palinsesto.empty:
        print("⚠️ Palinsesto vuoto. Nessun dato da elaborare.")
        return

    # 1. ELIMINAZIONE TASSATIVA DEI RECORD CORROTTI "NONE VS NONE"
    if '3. Match' in df_palinsesto.columns:
        df_palinsesto = df_palinsesto[df_palinsesto['3. Match'].astype(str).str.upper() != 'NONE VS NONE']
        df_palinsesto = df_palinsesto[df_palinsesto['3. Match'].astype(str).str.upper() != 'NAN']
        df_palinsesto = df_palinsesto.dropna(subset=['3. Match'])

    record_finali = []

    # 2. SCANSIONE DIRETTA MATCH PER MATCH SU API
    for idx, row in df_palinsesto.iterrows():
        nuovo_record = row.copy()
        
        try:
            m_id = int(row.get('Match_ID', 0))
        except:
            m_id = 0

        if m_id == 0:
            continue

        # Chiamata diretta per verificare lo stato di QUESTO specifico match sul server
        url_singolo_match = f"{BASE_URL}matches/{m_id}"
        try:
            res = requests.get(url_singolo_match, headers=HEADERS, timeout=8)
            if res.status_code == 200:
                match_data = res.json()
                stato_reale = str(match_data.get("status", "")).upper()
                
                if stato_reale == "FINISHED":
                    score = match_data.get("score", {})
                    full_time = score.get("fullTime", {})
                    h_g = full_time.get("home")
                    a_g = full_time.get("away")
                    
                    if h_g is not None and a_g is not None:
                        nuovo_record['Risultato_Reale'] = f"{h_g}-{a_g}"
                        
                        # Calcolo esito 1X2 reale
                        segno_reale = "1" if h_g > a_g else ("X" if h_g == a_g else "2")
                        pronostico_1x2 = str(row.get('1X2', ''))
                        nuovo_record['Esito_1X2'] = "VINCENTE" if segno_reale in pronostico_1x2 else "PERDENTE"
                    else:
                        nuovo_record['Risultato_Reale'] = "NON ANCORA REALE/DA VALIDARE"
                        nuovo_record['Esito_1X2'] = "IN ATTESA"
                else:
                    # Match programmato o in corso
                    nuovo_record['Risultato_Reale'] = "NON ANCORA REALE/DA VALIDARE"
                    nuovo_record['Esito_1X2'] = "IN ATTESA"
            else:
                # Se l'API non risponde, preserviamo lo stato precedente senza perdere il match
                if pd.isna(row.get('Risultato_Reale')) or "NON ANCORA" in str(row.get('Risultato_Reale')).upper():
                    nuovo_record['Risultato_Reale'] = "NON ANCORA REALE/DA VALIDARE"
                    nuovo_record['Esito_1X2'] = "IN ATTESA"
        except Exception as e:
            print(f"⚠️ Errore di rete su match {m_id}: {str(e)}")

        record_finali.append(nuovo_record)

    # 3. SCRITTURA FINALE DELLO STORICO VALIDATO COMPLETAMENTE AUTOMATIZZATO
    df_nuovo_storico = pd.DataFrame(record_finali)
    df_nuovo_storico.to_excel(STORICO_FILE, index=False)
    print(f"✅ Archivio {STORICO_FILE} rigenerato. Righe pulite scritte: {len(df_nuovo_storico)}")

if __name__ == "__main__":
    esegui_validazione()
