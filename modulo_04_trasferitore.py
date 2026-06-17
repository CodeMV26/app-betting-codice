import pandas as pd
import os

print("🗄️ --- MODULO 04: ARCHIVIATORE CENTRALE ANTI-DOPPIONI ---")

FILE_INPUT_VALIDATO = "Storico_Validato_Betting.xlsx"
DATABASE_STORICO_GLOBALE = "Database_Storico_Completo.xlsx"

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

    if os.path.exists(DATABASE_STORICO_GLOBALE):
        df_storico = pd.read_excel(DATABASE_STORICO_GLOBALE)
        print(f"📈 Database storico caricato. Record attuali: {len(df_storico)}")
    else:
        df_storico = pd.DataFrame(columns=df_nuovi_validi.columns)
        print("🆕 Nessun database storico trovato. Ne creo uno nuovo.")

    def genera_chiave_univoca(row):
        data = str(row.get('Data_Ora_Match', '')).strip()
        match_str = str(row.get('3. Match', '')).strip()
        return f"{data}_{match_str}".lower().replace(" ", "")

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
        print(f"✅ Archiviazione completata. Aggiunti {record_aggiunti} nuovi match.")
        
        try:
            df_nuovi_vuoto = df_nuovi[df_nuovi['Risultato_Reale'] == 'NON ANCORA REALE/DA VALIDARE']
            df_nuovi_vuoto.to_excel(FILE_INPUT_VALIDATO, index=False)
        except Exception as e:
            print(f"⚠️ Nota pulizia temporaneo: {e}")
    else:
        print("📋 Nessun nuovo inserimento effettuato.")

if __name__ == "__main__":
    esegui_archiviazione()
