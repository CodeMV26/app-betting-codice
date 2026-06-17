import pandas as pd
import os

print("🗄️ --- MODULO 04: ARCHIVIATORE CENTRALE ANTI-DOPPIONI COUPLER ---")

FILE_INPUT_VALIDATO = "Storico_Validato_Betting.xlsx"
PRONOSTICI_ORIGINALI = "Pronostici_App_Betting.xlsx"
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

    # REINTEGRAZIONE DI SICUREZZA: Esegue il merge dal file originario pre-match per recuperare i campi profondi delle API
    if os.path.exists(PRONOSTICI_ORIGINALI):
        try:
            df_orig = pd.read_excel(PRONOSTICI_ORIGINALI)
            if not df_orig.empty:
                df_orig['chiave_unione'] = df_orig.apply(genera_chiave_univoca, axis=1)
                df_nuovi_validi['chiave_unione'] = df_nuovi_validi.apply(genera_chiave_univoca, axis=1)
                
                # Identifica le colonne statistiche da preservare assolutamente
                colonne_da_recuperare = [c for c in df_orig.columns if c not in df_nuovi_validi.columns or c in ['Classifica_Casa', 'Classifica_Trasferta', 'Goal_Fatti_Casa', 'Goal_Subiti_Casa', 'Goal_Fatti_Trasferta', 'Goal_Subiti_Trasferta', 'Media_Corner_Casa', 'Media_Corner_Trasferta']]
                if colonne_da_recuperare:
                    colonne_da_recuperare.append('chiave_unione')
                    df_sub = df_orig[colonne_da_recuperare].drop_duplicates(subset=['chiave_unione'])
                    
                    # Rimuove le vecchie colonne sovrascritte prima di inserire i dati uniti corretti
                    col_sovrascrivere = [c for c in colonne_da_recuperare if c in df_nuovi_validi.columns and c != 'chiave_unione']
                    if col_sovrascrivere:
                        df_nuovi_validi.drop(columns=col_sovrascrivere, inplace=True)
                        
                    df_nuovi_validi = pd.merge(df_nuovi_validi, df_sub, on='chiave_unione', how='left')
                
                df_nuovi_validi.drop(columns=['chiave_unione'], errors='ignore')
        except Exception as e:
            print(f"⚠️ Errore durante il recupero di sicurezza dati pre-match: {e}")

    if 'chiave_unione' in df_nuovi_validi.columns:
        df_nuovi_validi.drop(columns=['chiave_unione'], inplace=True)

    if os.path.exists(DATABASE_STORICO_GLOBALE):
        df_storico = pd.read_excel(DATABASE_STORICO_GLOBALE)
        print(f"📈 Database storico caricato. Record attuali: {len(df_storico)}")
        
        # Allineamento automatico dei campi qualora vi fossero nuove colonne nel flusso dati
        for col in df_nuovi_validi.columns:
            if col not in df_storico.columns:
                df_storico[col] = None
    else:
        df_storico = pd.DataFrame(columns=df_nuovi_validi.columns)
        print("🆕 Nessun database storico trovato. Ne creo uno nuovo.")

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
        print(f"✅ Archiviazione completata. Aggiunti {record_aggiunti} nuovi match con statistiche integrate.")
        
        try:
            df_nuovi_vuoto = df_nuovi[df_nuovi['Risultato_Reale'] == 'NON ANCORA REALE/DA VALIDARE']
            df_nuovi_vuoto.to_excel(FILE_INPUT_VALIDATO, index=False)
        except Exception as e:
            print(f"⚠️ Nota pulizia temporaneo: {e}")
    else:
        print("📋 Nessun nuovo inserimento effettuato.")

if __name__ == "__main__":
    esegui_archiviazione()
