import sys
import os
import pandas as pd

# PROGRESSIVO CHAT: #095 | Data: 28 Giugno 2026 | Ora: 16:58:12
# Versione Modulo: 5.95 (Fix Totale KeyError Anti-Crash)

STORICO_FILE = "Storico_Validato_Betting.xlsx"
DATABASE_STORICO_GLOBALE = "Database_Storico_Completo.xlsx"

def genera_chiave_univoca_local(row):
    data = str(row.get('Data_Ora_Match', row.get('Data', row.get('2. Data', '')))).strip()
    match_str = str(row.get('3. Match', row.get('Match', ''))).strip()
    return f"{data}_{match_str}".lower().replace(" ", "")

def _logica_core_trasferimento():
    if not os.path.exists(STORICO_FILE):
        print("⚠️ File storico non trovato.")
        return
        
    try:
        df_da_appendere = pd.read_excel(STORICO_FILE)
        if df_da_appendere.empty:
            print("⚠️ Lo storico sorgente è vuoto.")
            return
            
        # --- ALLINEAMENTO DI SICUREZZA DELLE COLONNE CRUCIALI ---
        # Se l'interfaccia cerca colonne specifiche, ci assicuriamo che esistano nel dataframe
        mappa_repliche = {
            'Risultato_Reale': ['Risultato Reale', 'Risultato', 'Esito_Finale', 'Risultato_Finale'],
            'Esito_1X2': ['Esito 1X2', 'Esito', '1X2']
        }
        
        for col_target, varianti in mappa_repliche.items():
            # Se la colonna principale non c'è, cerchiamo se c'è una variante
            if col_target not in df_da_appendere.columns:
                for v in varianti:
                    if v in df_da_appendere.columns:
                        df_da_appendere[col_target] = df_da_appendere[v]
                        break
                # Se non c'è nemmeno la variante, creiamo la colonna vuota per non far crashare l'app
                if col_target not in df_da_appendere.columns:
                    df_da_appendere[col_target] = "Dato Non Rilevato"

        # Se esiste già un archivio globale, lo fondiamo controllando i duplicati
        if os.path.exists(DATABASE_STORICO_GLOBALE):
            df_storico_esistente = pd.read_excel(DATABASE_STORICO_GLOBALE)
            
            if not df_storico_esistente.empty:
                chiavi_storico = set(df_storico_esistente.apply(genera_chiave_univoca_local, axis=1))
            else:
                chiavi_storico = set()
                
            nuovi_record = []
            for _, riga in df_da_appendere.iterrows():
                if genera_chiave_univoca_local(riga) not in chiavi_storico:
                    nuovi_record.append(riga)
            
            if nuovi_record:
                df_nuovi = pd.DataFrame(nuovi_record)
                df_storico_aggiornato = pd.concat([df_storico_esistente, df_nuovi], ignore_index=True, sort=False)
                df_storico_aggiornato.to_excel(DATABASE_STORICO_GLOBALE, index=False)
            else:
                # Forza comunque il salvataggio per aggiornare eventuali dati mancanti
                df_da_appendere.to_excel(DATABASE_STORICO_GLOBALE, index=False)
        else:
            # Se non esiste, creiamo il file direttamente
            df_da_appendere.to_excel(DATABASE_STORICO_GLOBALE, index=False)
            
        print("✅ Sincronizzazione completata con successo senza errori di chiave.")
            
    except Exception as e:
        print(f"❌ Errore controllato: {e}")
        raise e

def esegui_allineamento():
    _logica_core_trasferimento()

def esegui_trasferimento():
    _logica_core_trasferimento()

sys.modules[__name__].esegui_allineamento = esegui_allineamento
sys.modules[__name__].esegui_trasferimento = esegui_trasferimento
