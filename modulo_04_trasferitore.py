import pandas as pd
import os

STORICO_VALIDATO = "Storico_Validato_Betting.xlsx"
DATABASE_PERMANENTE = "Database_Storico_Completo.xlsx"

def esegui_allineamento():
    """
    Modulo 04: Archiviatore Permanente (Fase 3) - Versione 5.66
    Accoda i match convalidati nel Database Storico Completo eliminando i duplicati.
    Garantisce il trasferimento di tutte le colonne, mercati ed esiti senza perdite.
    """
    print("💾 Avvio Modulo 04: Archiviazione nel Database Permanente (Scudo Anti-Doppione Integrale)...")

    # 1. Verifica presenza dei dati convalidati dal Modulo 3
    if not os.path.exists(STORICO_VALIDATO):
        print(f"⚠️ Errore: {STORICO_VALIDATO} non trovato. Esegui prima la convalida (Fase 2).")
        return

    df_validato = pd.read_excel(STORICO_VALIDATO)
    if df_validato.empty:
        print("⚠️ Nessun dato presente nello Storico Validato da archiviare.")
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

    indici_da_tenere = []

    # 3. Filtraggio dei record tramite indici per preservare l'integrità strutturale di Pandas
    for idx, row in df_validato.iterrows():
        match_nome = str(row.get('3. Match', '')).strip()
        match_data = str(row.get('Data_Ora_Match', '')).strip()
        chiave_corrente = f"{match_data}_{match_nome.upper()}"

        # Scudo Anti-Doppione
        if chiave_corrente in chiavi_permanenti:
            continue

        indici_da_tenere.append(idx)

    if not indici_da_tenere:
        print("💾 Tutti i match convalidati sono già presenti nel Database Storico Completo. Zero righe aggiunte.")
        return

    # Estraiamo le righe mantenendo intatte tutte le colonne native del file sorgente
    df_nuovi_salvati = df_validato.loc[indici_da_tenere].copy()

    # 4. Scrittura finale in modalità APPEND (unione e riscrittura sicura con allineamento colonne)
    if not df_permanente.empty:
        df_database_aggiornato = pd.concat([df_permanente, df_nuovi_salvati], ignore_index=True, sort=False)
    else:
        df_database_aggiornato = df_nuovi_salvati

    # Salvataggio su file Excel a costo zero
    df_database_aggiornato.to_excel(DATABASE_PERMANENTE, index=False)
    print(f"✅ Database Storico Permanente aggiornato! Aggiunti {len(df_nuovi_salvati)} nuovi match con tracciamento integrale dei mercati. Totale record in archivio: {len(df_database_aggiornato)}")

if __name__ == "__main__":
    esegui_allineamento()
