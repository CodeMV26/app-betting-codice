import sys
import os
import pandas as pd

# PROGRESSIVO CHAT: #093 | Data: 28 Giugno 2026 | Ora: 16:52:39
# Versione Modulo: 5.93 (Mappatura Universale dei Risultati Reali)

STORICO_FILE = "Storico_Validato_Betting.xlsx"
DATABASE_STORICO_GLOBALE = "Database_Storico_Completo.xlsx"

def genera_chiave_univoca_local(row):
    data = str(row.get('Data_Ora_Match', row.get('Data', row.get('2. Data', '')))).strip()
    match_str = str(row.get('3. Match', row.get('Match', ''))).strip()
    return f"{data}_{match_str}".lower().replace(" ", "")

def _logica_core_trasferimento():
    if not os.path.exists(STORICO_FILE):
        return
        
    try:
        df_da_appendere = pd.read_excel(STORICO_FILE)
        if df_da_appendere.empty:
            return
            
        # --- NORMALIZZAZIONE E CLONAZIONE COLONNE CRUCIALI ---
        # Per ciascuna riga, cerchiamo il risultato reale ovunque sia memorizzato e lo copiamo in tutte le varianti note
        varianti_risultato = ['Risultato_Reale', 'Risultato Reale', 'Risultato', 'Esito_Finale', 'Gol_Fatti_Totali']
        varianti_esito = ['Esito 1X2', 'Esito_1X2', 'Esito', '1X2']
        
        for idx, row in df_da_appendere.iterrows():
            # Trova un valore valido per il Risultato Reale
            valore_risultato = None
            for var in varianti_risultato:
                if var in df_da_appendere.columns and pd.notna(row[var]) and str(row[var]).strip() != "":
                    valore_risultato = row[var]
                    break
            
            # Trova un valore valido per l'Esito
            valore_esito = None
            for var in varianti_esito:
                if var in df_da_appendere.columns and pd.notna(row[var]) and str(row[var]).strip() != "":
                    valore_esito = row[var]
                    break
                    
            # Se abbiamo trovato i dati, li iniettiamo in tutte le possibili colonne target per l'interfaccia
            if valore_risultato is not None:
                for var in varianti_risultato:
                    df_da_appendere.at[idx, var] = valore_risultato
            if valore_esito is not None:
                for var in varianti_esito:
                    df_da_appendere.at[idx, var] = valore_esito

        if os.path.exists(DATABASE_STORICO_GLOBALE):
            try:
                os.remove(DATABASE_STORICO_GLOBALE) # Eliminiamo il vecchio database fallato per rigenerarlo pulito
            except:
                pass
                
        # Scriviamo il file pulito contenente tutte le varianti di colonna
        df_da_appendere.to_excel(DATABASE_STORICO_GLOBALE, index=False)
        print("✅ Database Storico rigenerato con mappatura universale delle colonne.")
            
    except Exception as e:
        print(f"❌ Errore nel trasferimento: {e}")
        raise e

def esegui_allineamento():
    _logica_core_trasferimento()

def esegui_trasferimento():
    _logica_core_trasferimento()

me = sys.modules[__name__]
setattr(me, 'esegui_allineamento', esegui_allineamento)
setattr(me, 'esegui_trasferimento', esegui_trasferimento)

if __name__ == "__main__":
    esegui_allineamento()                chiavi_storico = set()
            
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
