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
    Modulo 03: Validatore Resiliente Totale - Versione 5.48
    Garantisce che il file non sia mai vuoto. Copia tutto il palinsesto pulito.
    Interroga in tempo reale solo i match con ID valido.
    """
    print("🏆 [FASE 2] Avvio Validazione di Sicurezza...")
    
    if not os.path.exists(PALINSESTO_FILE):
        print(f"⚠️ Errore critico: {PALINSESTO_FILE} non trovato.")
        return
    
    df_palinsesto = pd.read_excel(PALINSESTO_FILE)
    if df_palinsesto.empty:
        print("⚠️ Palinsesto vuoto originariamente. Nessun dato.")
        return

    # 1. PURIFAZIONE IMMEDIATA MA INCLUSIVA (Tagliamo solo i None vs None veri)
    if '3. Match' in df_palinsesto.columns:
        df_palinsesto = df_palinsesto[df_palinsesto['3. Match'].astype(str).str.upper() != 'NONE VS NONE']
        df_palinsesto = df_palinsesto[df_palinsesto['3. Match'].astype(str).str.upper() != 'NAN']

    record_finali = []

    # 2. SCANSIONE PROTETTA
    for idx, row in df_palinsesto.iterrows():
        nuovo_record = row.copy()
        
        # Estrazione sicura dell'ID
        m_id_raw = row.get('Match_ID')
        try:
            m_id = int(float(m_id_raw)) if pd.notna(m_id_raw) else 0
        except:
            m_id = 0

        # Se non c'è ID valido, manteniamo la riga nello storico senza distruggerla
        if m_id == 0:
            if pd.isna(nuovo_record.get('Risultato_Reale')) or str(nuovo_record.get('Risultato_Reale')).strip() == "":
                nuovo_record['Risultato_Reale'] = "NON ANCORA REALE/DA VALIDARE"
                nuovo_record['Esito_1X2'] = "IN ATTESA"
            record_finali.append(nuovo_record)
            continue

        # Chiamata API mirata ad automazione totale
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
                        segno_reale = "1" if h_g > a_g else ("X" if h_g == a_g else "2")
                        pronostico_1x2 = str(row.get('1X2', ''))
                        nuovo_record['Esito_1X2'] = "VINCENTE" if segno_reale in pronostico_1x2 else "PERDENTE"
                    else:
                        nuovo_record['Risultato_Reale'] = "NON ANCORA REALE/DA VALIDARE"
                        nuovo_record['Esito_1X2'] = "IN ATTESA"
                else:
                    nuovo_record['Risultato_Reale'] = "NON ANCORA REALE/DA VALIDARE"
                    nuovo_record['Esito_1X2'] = "IN ATTESA"
            else:
                # Caso di fallback se l'API non risponde (mantiene il dato corrente)
                if pd.isna(nuovo_record.get('Risultato_Reale')) or "NON ANCORA" in str(nuovo_record.get('Risultato_Reale')).upper():
                    nuovo_record['Risultato_Reale'] = "NON ANCORA REALE/DA VALIDARE"
                    nuovo_record['Esito_1X2'] = "IN ATTESA"
        except Exception:
            if pd.isna(nuovo_record.get('Risultato_Reale')) or "NON ANCORA" in str(nuovo_record.get('Risultato_Reale')).upper():
                nuovo_record['Risultato_Reale'] = "NON ANCORA REALE/DA VALIDARE"
                nuovo_record['Esito_1X2'] = "IN ATTESA"

        record_finali.append(nuovo_record)

    # 3. SCRITTURA DI SICUREZZA INCONDIZIONATA
    df_nuovo_storico = pd.DataFrame(record_finali)
    df_nuovo_storico.to_excel(STORICO_FILE, index=False)
    print(f"✅ Archivio {STORICO_FILE} salvato con {len(df_nuovo_storico)} righe presenti.")

if __name__ == "__main__":
    esegui_validazione()
