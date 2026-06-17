import pandas as pd
import os

print("🗄️ --- MODULO 04: ARCHIVIATORE CENTRALE ANTI-DOPPIONI ---")

# File di input (generato dal Modulo 03) e file di database storico globale
FILE_INPUT_VALIDATO = "Storico_Validato_Betting.xlsx"
DATABASE_STORICO_GLOBALE = "Database_Storico_Completo.xlsx"

def esegui_archiviazione():
    # 1. Verifica se esiste il file dei match appena convalidati
    if not os.path.exists(FILE_INPUT_VALIDATO):
        print(f"⚠️ Nessun file {FILE_INPUT_VALIDATO} trovato. Fase 2 non ancora eseguita?")
        return

    df_nuovi = pd.read_excel(FILE_INPUT_VALIDATO)
    if df_nuovi.empty:
        print("⚠️ Il file dei match convalidati è vuoto. Nulla da archiviare.")
        return

    # Filtra tenendo solo i match che sono stati effettivamente convalidati (risultato reale presente)
    df_nuovi_validi = df_nuovi[df_nuovi['Risultato_Reale'] != 'NON ANCORA REALE/DA VALIDARE'].copy()
    
    if df_nuovi_validi.empty:
        print("⏳ Nessun match completato e convalidato trovato in questa sessione.")
        return

    # 2. Carica il database storico globale esistente o ne crea uno nuovo se è la prima esecuzione
    if os.path.exists(DATABASE_STORICO_GLOBALE):
        df_storico = pd.read_excel(DATABASE_STORICO_GLOBALE)
        print(f"📈 Database storico globale caricato. Record attuali: {len(df_storico)}")
    else:
        df_storico = pd.DataFrame(columns=df_nuovi_validi.columns)
        print("🆕 Nessun database storico trovato. Ne creo uno nuovo adesso.")

    # 3. Funzione di supporto per generare la chiave univoca: Data + Casa + Ospite
    def genera_chiave_univoca(row):
        data = str(row.get('Data_Ora_Match', '')).strip()
        # Estrae i nomi delle squadre dal campo '3. Match' (es. "Milan - Inter")
        match_str = str(row.get('3. Match', '')).strip()
        return f"{data}_{match_str}".lower().replace(" ", "")

    # Creiamo una lista o set delle chiavi già presenti nell'archivio storico per un controllo fulmineo
    if not df_storico.empty:
        chiavi_esistenti = set(df_storico.apply(genera_chiave_univoca, axis=1))
    else:
        chiavi_esistenti = set()

     record_aggiunti = 0
    righe_da_appendere = []

    # 4. Scansione dei nuovi match convalidati ed eliminazione dei doppioni
    for idx, row in df_nuovi_validi.iterrows():
        chiave_match = genera_chiave_univoca(row)
        
        if chiave_match in chiavi_esistenti:
            print(f"🚫 Match già presente in archivio (Doppione evitato): {row.get('3. Match', 'Match')} del {row.get('Data_Ora_Match', '')}")
        else:
            # Se la chiave è unica, memorizza l'intero record (statistiche API, 11 mercati ed esiti)
            righe_da_appendere.append(row)
            chiavi_esistenti.add(chiave_match) # Evita doppioni anche all'interno dello stesso blocco di input
            record_aggiunti += 1

    # 5. Salva i dati consolidati se ci sono aggiornamenti
    if righe_da_appendere:
        df_da_appendere = pd.DataFrame(righe_da_appendere)
        df_storico_aggiornato = pd.concat([df_storico, df_da_appendere], ignore_index=True)
        
        # Scrittura fisica sul file Excel dell'archivio permanente
        df_storico_aggiornato.to_excel(DATABASE_STORICO_GLOBALE, index=False)
        print(f"✅ Archiviazione completata con successo! Aggiunti {record_aggiunti} nuovi match unici.")
        print(f"📊 Totale record ora presenti nel Database Storico: {len(df_storico_aggiornato)}")
        
        # Opzionale: pulizia file temporaneo post-match per liberare spazio all'esecuzione successiva
        try:
            # Svuota il file temporaneo o lo rigenera vuoto per evitare ricicli infiniti
            df_nuovi_vuoto = df_nuovi[df_nuovi['Risultato_Reale'] == 'NON ANCORA REALE/DA VALIDARE']
            df_nuovi_vuoto.to_excel(FILE_INPUT_VALIDATO, index=False)
        except Exception as e:
            print(f"⚠️ Nota: Impossibile ripulire il file temporaneo: {e}")
    else:
        print("📋 Tutti i match analizzati erano già presenti nel database. Nessun nuovo inserimento effettuato.")

if __name__ == "__main__":
    esegui_archiviazione()
