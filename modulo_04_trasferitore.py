import pandas as pd
import os

STORICO_VALIDATO = "Storico_Validato_Betting.xlsx"
DATABASE_PERMANENTE = "Database_Storico_Completo.xlsx"

def esegui_allineamento():
    """
    Modulo 04: Trasferitore Permanente (Fase 3) - Versione 5.79
    Sposta i dati convalidati nel Database Permanente senza duplicati.
    """
    print("💾 Avvio Modulo 04: Archiviazione nel Database Permanente...")
    
    # Rilevamento automatico della cartella sul server cloud
    cartella_progetto = os.path.dirname(os.path.abspath(__file__))
    path_storico = os.path.join(cartella_progetto, STORICO_VALIDATO)
    path_database = os.path.join(cartella_progetto, DATABASE_PERMANENTE)

    if not os.path.exists(path_storico):
        print(f"⚠️ Errore: {STORICO_VALIDATO} non trovato.")
        return

    try:
        df_validato = pd.read_excel(path_storico)
    except Exception as e:
        print(f"❌ Errore lettura Storico: {e}")
        return

    if df_validato.empty:
        print("⚠️ Nessun dato presente nello Storico Validato da archiviare.")
        return

    if os.path.exists(path_database):
        try:
            df_permanente = pd.read_excel(path_database)
        except:
            df_permanente = pd.DataFrame()
    else:
        df_permanente = pd.DataFrame()

    # Controllo anti-duplicati geometrico
    chiavi_permanenti = set()
    if not df_permanente.empty and '3. Match' in df_permanente.columns and 'Data_Ora_Match' in df_permanente.columns:
        for _, r in df_permanente.iterrows():
            chiave = f"{str(r['Data_Ora_Match']).strip()}_{str(r['3. Match']).strip().upper()}"
            chiavi_permanenti.add(chiave)

    indici_da_tenere = []
    for idx, row in df_validato.iterrows():
        match_nome = str(row.get('3. Match', '')).strip()
        match_data = str(row.get('Data_Ora_Match', '')).strip()
        chiave_corrente = f"{match_data}_{match_nome.upper()}"

        if chiave_corrente in chiavi_permanenti:
            continue
        indici_da_tenere.append(idx)

    if not indici_da_tenere:
        print("💾 Tutti i match sono già archiviati. Zero righe aggiunte.")
        return

    df_nuovi_salvati = df_validato.loc[indici_da_tenere].copy()

    if not df_permanente.empty:
        df_database_aggiornato = pd.concat([df_permanente, df_nuovi_salvati], ignore_index=True, sort=False)
    else:
        df_database_aggiornato = df_nuovi_salvati

    df_database_aggiornato.to_excel(path_database, index=False)
    print(f"✅ Database Aggiornato! Record totali: {len(df_database_aggiornato)}")

if __name__ == "__main__":
    esegui_allineamento()