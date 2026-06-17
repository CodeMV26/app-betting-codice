import pandas as pd
import os

print("🗄️ --- MODULO 04: ARCHIVIATORE CENTRALE CON SCANSIONE INTEGRALE DINAMICA ---")

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

    # PARACADUTE DINAMICO TOTALE: Recuperiamo TUTTI i dati statistici possibili
    if os.path.exists(PRONOSTICI_ORIGINALI):
        try:
            df_orig = pd.read_excel(PRONOSTICI_ORIGINALI)
            if not df_orig.empty:
                # Creiamo la chiave di unione su entrambi i dataframe
                df_orig['chiave_unione'] = df_orig.apply(genera_chiave_univoca, axis=1)
                df_nuovi_validi['chiave_unione'] = df_nuovi_validi.apply(genera_chiave_univoca, axis=1)
                
                # Identifichiamo quali colonne sono esiti (generate dal modulo 03) per non sovrascriverle malamente
                colonne_esiti = [c for c in df_nuovi_validi.columns if str(c).startswith('Esito_') or c == 'Risultato_Reale']
                
                # Prendiamo TUTTE le colonne del file originale pre-match che NON sono esiti
                colonne_da_conservare = [c for c in df_orig.columns if c not in colonne_esiti or c == 'chiave_unione']
                
                # Rimuoviamo i duplicati basandoci sulla chiave
                df_sub = df_orig[colonne_da_conservare].drop_duplicates(subset=['chiave_unione'])
                
                # Rimuoviamo le colonne dal file convalidato che stanno per essere iniettate fresche dall'originale
                col_da_rimuovere = [c for c in df_sub.columns if c in df_nuovi_validi.columns and c != 'chiave_unione']
                if col_da_rimuovere:
                    df_nuovi_validi.drop(columns=col_colpito, errors='ignore', inplace=True)
                
                # FUSIONE COMPLETA DI TUTTE LE COLONNE (Pt, G, V, N, P, Medie, ecc.)
                df_nuovi_validi = pd.merge(df_nuovi_validi, df_sub, on='chiave_unione', how='left')
                print("📊 Sincronizzazione dinamica eseguita. Tutte le colonne statistiche sono state preservate.")
        except Exception as e:
            print(f"⚠️ Nota recupero dinamico: {e}")

    # Pulizia chiave temporanea
    if 'chiave_unione' in df_nuovi_validi.columns:
        df_nuovi_validi.drop(columns=['chiave_unione'], inplace=True)

    # Caricamento o creazione del Database Storico Globale
    if os.path.exists(DATABASE_STORICO_GLOBALE):
        df_storico = pd.read_excel(DATABASE_STORICO_GLOBALE)
        print(f"📈 Database storico caricato. Record attuali: {len(df_storico)}")
        
        # Allineamento strutturale automatico per ospitare ogni nuova colonna immessa dalle API
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
        print(f"✅ Archiviazione completata. Aggiunti {record_aggiunti} nuovi match con l'intero set di colonne API.")
        
        try:
            df_nuovi_vuoto = df_nuovi[df_nuovi['Risultato_Reale'] == 'NON ANCORA REALE/DA VALIDARE']
            df_nuovi_vuoto.to_excel(FILE_INPUT_VALIDATO, index=False)
        except Exception as e:
            print(f"⚠️ Nota pulizia temporaneo: {e}")
    else:
        print("📋 Nessun nuovo inserimento effettuato.")

if __name__ == "__main__":
    esegui_archiviazione()
