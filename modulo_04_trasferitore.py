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
    # Verifichiamo l'esistenza dei due file fondamentali
    if not os.path.exists(FILE_INPUT_VALIDATO):
        print(f"⚠️ Nessun file {FILE_INPUT_VALIDATO} trovato. Fase 2 non necessaria.")
        return

    if not os.path.exists(DATABASE_STORICO_GLOBALE):
        print(f"❌ Errore Critico: Il file {DATABASE_STORICO_GLOBALE} non esiste. Impossibile aggiornare i risultati.")
        return

    # Lettura dei dati reali convalidati dal Modulo 03
    df_nuovi = pd.read_excel(FILE_INPUT_VALIDATO)
    if df_nuovi.empty:
        print("⚠️ Il file dei match convalidati è vuoto.")
        return

    # BLINDAGGIO MOBILE (iPhone X/13): Uniformiamo il tipo dato in stringa per evitare fallimenti nel filtro
    df_nuovi['Risultato_Reale'] = df_nuovi['Risultato_Reale'].astype(str).str.strip()

    # Isoliamo solo i match che hanno un risultato reale campionato e pronto
    df_nuovi_validi = df_nuovi[df_nuovi['Risultato_Reale'] != 'NON ANCORA REALE/DA VALIDARE'].copy()
    
    if df_nuovi_validi.empty:
        print("⏳ Nessun match completato e validato da incrociare in questo momento.")
        return

    # Carichiamo l'archivio storico completo pre-match (generato e protetto dal Modulo 02)
    df_storico = pd.read_excel(DATABASE_STORICO_GLOBALE)
    print(f"📈 Database storico caricato. Record totali registrati: {len(df_storico)}")

    # Creiamo le chiavi univoche per l'incrocio millimetrico (MUST 2)
    df_storico['chiave_incrocio'] = df_storico.apply(genera_chiave_univoca, axis=1)
    df_nuovi_validi['chiave_incrocio'] = df_nuovi_validi.apply(genera_chiave_univoca, axis=1)

    # Identifichiamo quali colonne contengono gli esiti e i risultati calcolati dal Modulo 03
    colonne_da_aggiornare = [c for c in df_nuovi_validi.columns if str(c).startswith('Esito_') or c == 'Risultato_Reale']
    
    # Assicuriamo che lo storico sia strutturato per accogliere le colonne esito se non esistono ancora (MUST 7)
    for col in colonne_da_aggiornare:
        if col not in df_storico.columns:
            df_storico[col] = None

    # Trasformiamo i match convalidati in un dizionario indicizzato sulla chiave per l'update diretto
    diz_nuovi_dati = df_nuovi_validi.set_index('chiave_incrocio')[colonne_da_aggiornare].to_dict(orient='index')

    match_aggiornati_conteggio = 0

    # Ciclo di aggiornamento nello storico: andiamo a sovrascrivere solo i campi del risultato finale (MUST 3)
    for idx, row in df_storico.iterrows():
        chiave = row['chiave_incrocio']
        if chiave in diz_nuovi_dati:
            for col in colonne_da_aggiornare:
                df_storico.at[idx, col] = diz_nuovi_dati[chiave][col]
            match_aggiornati_conteggio += 1

    # Pulizia delle colonne di servizio temporanee
    df_storico.drop(columns=['chiave_incrocio'], errors='ignore', inplace=True)

    if match_aggiornati_conteggio > 0:
        # Salviamo lo storico definitivo aggiornato
        df_storico.to_excel(DATABASE_STORICO_GLOBALE, index=False)
        print(f"✅ Successo! Aggiornati {match_aggiornati_conteggio} match nell'archivio storico con i risultati reali.")
        
        # Pulizia del file temporaneo: lasciamo dentro solo i match ancora da giocare/validare (MUST 6)
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
