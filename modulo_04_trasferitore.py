import sys
import os
import pandas as pd

# PROGRESSIVO CHAT: #091 | Data: 28 Giugno 2026 | Ora: 16:46:27
# Versione Modulo: 5.91 (Copia Integrale Colonne & Risultati)

STORICO_FILE = "Storico_Validato_Betting.xlsx"
DATABASE_STORICO_GLOBALE = "Database_Storico_Completo.xlsx"

def genera_chiave_univoca_local(row):
    # Cerca la data e il match provando sia le versioni pulite che quelle con prefisso numerico
    data = str(row.get('Data_Ora_Match', row.get('Data', row.get('2. Data', '')))).strip()
    match_str = str(row.get('3. Match', row.get('Match', ''))).strip()
    return f"{data}_{match_str}".lower().replace(" ", "")

def _logica_core_trasferimento():
    if not os.path.exists(STORICO_FILE):
        print(f"⚠️ File {STORICO_FILE} non trovato.")
        return
        
    try:
        df_da_appendere = pd.read_excel(STORICO_FILE)
        if df_da_appendere.empty:
            print("⚠️ Lo storico sorgente è vuoto.")
            return
            
        print(f"📊 Colonne rilevate nello storico: {list(df_da_appendere.columns)}")
        
        if os.path.exists(DATABASE_STORICO_GLOBALE):
            df_storico_esistente = pd.read_excel(DATABASE_STORICO_GLOBALE)
            
            # Genera set delle chiavi già archiviate per evitare duplicati
            if not df_storico_esistente.empty:
                chiavi_storico = set(df_storico_esistente.apply(genera_chiave_univoca_local, axis=1))
            else:
                chiavi_storico = set()
            
            # Filtra solo i match effettivamente nuovi
            nuovi_record = []
            for _, riga in df_da_appendere.iterrows():
                if genera_chiave_univoca_local(riga) not in chiavi_storico:
                    nuovi_record.append(riga)
            
            if nuovi_record:
                df_nuovi = pd.DataFrame(nuovi_record)
                # Concatenazione totale: mantiene intatte TUTTE le colonne di entrambi i file
                df_storico_aggiornato = pd.concat([df_storico_esistente, df_nuovi], ignore_index=True, sort=False)
                df_storico_aggiornato.to_excel(DATABASE_STORICO_GLOBALE, index=False)
                print(f"✅ Trasferiti con successo {len(nuovi_record)} match completi di statistiche e risultati.")
            else:
                print("ℹ️ Nessun nuovo match da aggiungere, archivio già allineato.")
        else:
            # Se l'archivio globale non esiste, lo crea copiando al 100% lo storico con tutte le sue colonne
            df_da_appendere.to_excel(DATABASE_STORICO_GLOBALE, index=False)
            print("🆕 Creato nuovo archivio globale strutturato.")
            
    except Exception as e:
        print(f"❌ Errore nel trasferimento: {e}")
        raise e

def esegui_allineamento():
    _logica_core_trasferimento()

def esegui_trasferimento():
    _logica_core_trasferimento()

# Iniezione forzata per prevenire blocchi di vecchia memoria del server
me = sys.modules[__name__]
setattr(me, 'esegui_allineamento', esegui_allineamento)
setattr(me, 'esegui_trasferimento', esegui_trasferimento)

if __name__ == "__main__":
    esegui_allineamento()
