import pandas as pd
import os

print("🗄️ --- MODULO 04: ARCHIVIATORE CENTRALE CON FILE INPUT CORRETTO ---")

FILE_INPUT_VALIDATO = "Storico_Validato_Betting.xlsx"
# CORREZIONE CRITICA: Puntiamo al file reale del Modulo 01 che contiene le statistiche API
PRONOSTICI_ORIGINALI = "Database_App_Betting.xlsx" 
DATABASE_STORICO_GLOBALE = "Database_Storico_Completo.xlsx"

def genera_chiave_univoca(row):
    data = str(row.get('Data_Ora_Match', '')).strip()
    match_str = str(row.get('3. Match', '')).strip()
    return f"{data}_{match_str}".lower().replace(" ", "")

def esegui_archiviazione():
    if not os.path.exists(FILE_INPUT_VALIDATO):
        print(f"⚠️ Nessun file {FILE_INPUT_VALIDATO} trovato.")
        return

    df_nuovi = pd.read_excel(FILE_INPUT_VALIDATO)
    if df_nuovi.empty:
        print("⚠️ Il file dei match convalidati è vuoto.")
        return

    df_nuovi_validi = df_nuovi[df_nuovi['Risultato_Reale'] != 'NON ANCORA REALE/DA VALIDARE'].copy()
    
    if df_nuovi_validi.empty:
        print("⏳ Nessun match completato e convalidato trovato.")
        return

    # FUSIONE DINAMICA CON IL VERO FILE DELLE STATISTICHE API
    if os.path.exists(PRONOSTICI_ORIGINALI):
        try:
            df_orig = pd.read_excel(PRONOSTICI_ORIGINALI)
            if not df_orig.empty:
                df_orig['chiave_unione'] = df_orig.apply(genera_chiave_univoca, axis=1)
                df_nuovi_validi['chiave_unione'] = df_nuovi_validi.apply(genera_chiave_univoca, axis=1)
                
                # Identifichiamo le colonne degli esiti reali (generate dal validatore)
                colonne_esiti = [c for c in df_nuovi_validi.columns if str(c).startswith('Esito_') or c == 'Risultato_Reale']
                
                # Prendiamo tutte le colonne dal file originale (comprese Pt, Pt_Casa, Medie, ecc.)
                colonne_da_conservare = [c for c in df_orig.columns if c not in colonne_esiti or c == 'chiave_unione']
                df_sub = df_orig[colonne_da_conservare].drop_duplicates(subset=['chiave_unione'])
                
                # Rimuoviamo dal foglio validato le colonne temporanee prima del merge
                col_da_rimuovere = [c for c in df_sub.columns if c in df_nuovi_validi.columns and c != 'chiave_unione']
                if col_da_rimuovere:
                    df_nuovi_validi.drop(columns=col_da_rimuovere, errors='ignore', inplace=True)
                
                # Unione totale delle colonne statistiche
                df_nuovi_validi = pd.merge(df_nuovi_validi, df_sub, on='chiave_unione', how='left')
                print("📊 Sincronizzazione colonne effettuata dal file delle statistiche reali.")
        except Exception as e:
            print(f"⚠️ Errore durante il riallineamento delle colonne: {e}")

    if 'chiave_unione' in df_nuovi_validi.columns:
        df_nuovi_validi.drop(columns=['chiave_unione'], inplace=True)

    # Caricamento o creazione del Database Storico Globale
    if os.path.exists(DATABASE_STORICO_GLOBALE):
        df_storico = pd.read_excel(DATABASE_STORICO_GLOBALE)
        print(f"📈 Database storico caricato. Record attuali: {len(df_storico)}")
        
        # Allineamento dinamico per assicurarsi che lo storico riceva TUTTE le colonne statistiche
        for col in df_nuovi_validi.columns:
            if col not in df_storico.columns:
                df_storico[col] = None
    else:
        df_storico = pd.DataFrame(columns=df_nuovi_validi.columns)
        print("🆕 Nessun database storico trovato. Creazione nuovo archivio.")

    if not df_storico.empty:
        chiavi_esistenti = set(df_storico.apply(genera_chiave_univoca, axis=1))
    else:
        chiavi_esistenti = set()

    record_aggiunti = 0
    righe_da_appendere = []

    for idx, row in df_nuovi_validi.iterrows():
        chiave_match = genera_chiave_univoca(row)
        
        if chiave_match in chiavi_esistenti:
            print(f"🚫 Match già presente in archivio: {row.get('3. Match', 'Match')}")
        else:
            righe_da_appendere.append(row)
            chiavi_esistenti.add(chiave_match)
            record_aggiunti += 1

    if righe_da_appendere:
        df_da_appendere = pd.DataFrame(righe_da_appendere)
        df_storico_aggiornato = pd.concat([df_storico, df_da_appendere], ignore_index=True)
        df_storico_aggiornato.to_excel(DATABASE_STORICO_GLOBALE, index=False)
        print(f"✅ Successo! Archiviati {record_aggiunti} match con l'intero set di colonne delle classifiche.")
        
        try:
            df_nuovi_vuoto = df_nuovi[df_nuovi['Risultato_Reale'] == 'NON ANCORA REALE/DA VALIDARE']
            df_nuovi_vuoto.to_excel(FILE_INPUT_VALIDATO, index=False)
        except Exception as e:
            print(f"⚠️ Nota pulizia temporaneo: {e}")
    else:
        print("📋 Nessun nuovo inserimento effettuato.")

if __name__ == "__main__":
    esegui_archiviazione()
