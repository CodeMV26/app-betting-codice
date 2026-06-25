import pandas as pd
import os

STORICO_VALIDATO = "Storico_Validato_Betting.xlsx"
DATABASE_PERMANENTE = "Database_Storico_Completo.xlsx"

def esegui_allineamento():
    """
    Modulo 04: Trasferitore Permanente (Fase 3) - Versione 5.38
    Accoda i match convalidati nel Database Storico Completo eliminando i duplicati.
    Funzione rinominata in 'esegui_allineamento' per compatibilità nativa con app.py.
    """
    print("💾 Avvio Modulo 04: Trasferimento nel Database Permanente (Scudo Anti-Doppione)...")

    # 1. Verifica presenza dei dati convalidati dal Modulo 3
    if not os.path.exists(STORICO_VALIDATO):
        print(f"⚠️ Errore: {STORICO_VALIDATO} non trovato. Esegui prima la convalida (Fase 2).")
        return

    df_validato = pd.read_excel(STORICO_VALIDATO)
    if df_validato.empty:
        print("⚠️ Nessun dato presente nello Storico Validato da trasferire.")
        return

    # 2. Caricamento del Database Permanente Esistente o creazione se rimosso
    if os.path.exists(DATABASE_PERMANENTE):
        try:
            df_permanente = pd.read_excel(DATABASE_PERMANENTE)
        except:
            df_permanente = pd.DataFrame()
    else:
        df_permanente = pd.DataFrame()

    # Creazione del set di chiavi univoche già storicizzate nel tempo (Data + Nome Match)
    chiavi_permanenti = set()
    if not df_permanente.empty and '3. Match' in df_permanente.columns and 'Data_Ora_Match' in df_permanente.columns:
        for _, r in df_permanente.iterrows():
            chiave = f"{str(r['Data_Ora_Match']).strip()}_{str(r['3. Match']).strip().upper()}"
            chiavi_permanenti.add(chiave)

    record_da_accodare = []

    # 3. Filtraggio dei record per evitare tassativamente i doppioni storici
    for idx, row in df_validato.iterrows():
        match_nome = str(row.get('3. Match', '')).strip()
        match_data = str(row.get('Data_Ora_Match', '')).strip()
        chiave_corrente = f"{match_data}_{match_nome.upper()}"

        # Scudo Anti-Doppione: Se la partita è già dentro l'archivio storico completo, non viene inserita di nuovo
        if chiave_corrente in chiavi_permanenti:
            continue

        record_da_accodare.append(row)

    if not record_da_accodare:
        print("💾 Tutti i match convalidati sono già presenti nel Database Storico Completo. Zero righe aggiunte.")
        return

    df_nuovi_salvati = pd.DataFrame(record_da_accodare)

    # 4. Scrittura finale in modalità APPEND (unione e riscrittura sicura)
    if not df_permanente.empty:
        df_database_aggiornato = pd.concat([df_permanente, df_nuovi_salvati], ignore_index=True)
    else:
        df_database_aggiornato = df_nuovi_salvati

    df_database_aggiornato.to_excel(DATABASE_PERMANENTE, index=False)
    print(f"✅ Database Storico Permanente aggiornato! Aggiunti {len(df_nuovi_salvati)} nuovi match. Totale record in archivio: {len(df_database_aggiornato)}")

if __name__ == "__main__":
    esegui_allineamento()
