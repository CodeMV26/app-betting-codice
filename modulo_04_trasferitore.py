import pandas as pd
import os

print("🗄️ --- MODULO 04: AGGIORNATORE STORICO POST-MATCH (LOGICA AD ALTO ALLINEAMENTO) ---")

FILE_INPUT_VALIDATO = "Storico_Validato_Betting.xlsx"
DATABASE_STORICO_GLOBALE = "Database_Storico_Completo.xlsx"

def genera_chiave_univoca(row):
    data = str(row.get('Data_Ora_Match', '')).strip()
    match_str = str(row.get('3. Match', '')).strip()
    return f"{data}_{match_str}".lower().replace(" ", "")

def esegui_archiviazione():
    if not os.path.exists(FILE_INPUT_VALIDATO):
        print(f"⚠️ Nessun file {FILE_INPUT_VALIDATO} trovato. Fase 2 non necessaria.")
        return

    if not os.path.exists(DATABASE_STORICO_GLOBALE):
        print(f"❌ Errore Critico: Il file {DATABASE_STORICO_GLOBALE} non esiste. Impossibile aggiornare i risultati.")
        return

    df_nuovi = pd.read_excel(FILE_INPUT_VALIDATO)
    if df_nuovi.empty:
        print("⚠️ Il file dei match convalidati è vuoto.")
        return

    df_nuovi['Risultato_Reale'] = df_nuovi['Risultato_Reale'].astype(str).str.strip()

    df_nuovi_validi = df_nuovi[df_nuovi['Risultato_Reale'] != 'NON ANCORA REALE/DA VALIDARE'].copy()
    
    if df_nuovi_validi.empty:
        print("⏳ Nessun match completato e validato da incrociare in questo momento.")
        return

    df_storico = pd.read_excel(DATABASE_STORICO_GLOBALE)
    print(f"📈 Database storico caricato. Record totali registrati: {len(df_storico)}")

    df_storico['chiave_incrocio'] = df_storico.apply(genera_chiave_univoca, axis=1)
    df_nuovi_validi['chiave_incrocio'] = df_nuovi_validi.apply(genera_chiave_univoca, axis=1)

    colonne_da_aggiornare = [c for c in df_nuovi_validi.columns if str(c).startswith('Esito_') or c == 'Risultato_Reale']
    
    for col in colonne_da_aggiornare:
        if col not in df_storico.columns:
            df_storico[col] = None

    diz_nuovi_dati = df_nuovi_validi.set_index('chiave_incrocio')[colonne_da_aggiornare].to_dict(orient='index')

    match_aggiornati_conteggio = 0

    for idx, row in df_storico.iterrows():
        chiave = row['chiave_incrocio']
        if chiave in diz_nuovi_dati:
            for col in colonne_da_aggiornare:
                df_storico.at[idx, col] = diz_nuovi_dati[chiave][col]
            match_aggiornati_conteggio += 1

    df_storico.drop(columns=['chiave_incrocio'], errors='ignore', inplace=True)

    if match_aggiornati_conteggio > 0:
        df_storico.to_excel(DATABASE_STORICO_GLOBALE, index=False)
        print(f"✅ Successo! Aggiornati {match_aggiornati_conteggio} match nell'archivio storico con i risultati reali.")
        
        try:
            df_nuovi_rimasti = df_nuovi[df_nuovi['Risultato_Reale'] == 'NON ANCORA REALE/DA VALIDARE']
            df_nuovi_rimasti.to_excel(FILE_INPUT_VALIDATO, index=False)
            print("🧹 Pulizia file temporaneo eseguita. Rimossi i match conclusi.")
        except Exception as e:
            print(f"⚠️ Nota pulizia file temporaneo: {e}")
    else:
        print("📋 Nessun incrocio eseguito. I match validati non hanno trovato corrispondenza nello storico.")

if __name__ == "__main__":
    esegui_archiviazione()
