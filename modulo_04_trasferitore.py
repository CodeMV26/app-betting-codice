import sys
import os
import pandas as pd

# PROGRESSIVO CHAT: #131 | Data: 30 Giugno 2026 | Ora: 10:18:52
# Versione Modulo: 6.21 (Fix Totale Append & Protezione Anti-Sovrascrittura)

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
        mappa_repliche = {
            'Risultato_Reale': ['Risultato Reale', 'Risultato', 'Esito_Finale', 'Risultato_Finale'],
            'Esito_1X2': ['Esito 1X2', 'Esito', '1X2']
        }
        
        for col_target, varianti in mappa_repliche.items():
            if col_target not in df_da_appendere.columns:
                for v in varianti:
                    if v in df_da_appendere.columns:
                        df_da_appendere[col_target] = df_da_appendere[v]
                        break
                if col_target not in df_da_appendere.columns:
                    df_da_appendere[col_target] = "Dato Non Rilevato"

        # Se esiste già un archivio globale, lo fondiamo controllando i duplicati in modo non distruttivo
        if os.path.exists(DATABASE_STORICO_GLOBALE):
            df_storico_esistente = pd.read_excel(DATABASE_STORICO_GLOBALE)
            
            if not df_storico_esistente.empty:
                # Creiamo una mappatura indice -> chiave per aggiornare record esistenti (es. da IN ATTESA a VINCENTE)
                mappa_chiavi_esistenti = {}
                for idx, riga in df_storico_esistente.iterrows():
                    chk_key = genera_chiave_univoca_local(riga)
                    mappa_chiavi_esistenti[chk_key] = idx
                
                nuovi_record = []
                for _, riga in df_da_appendere.iterrows():
                    chiave_nuova = genera_chiave_univoca_local(riga)
                    
                    if chiave_nuova in mappa_chiavi_esistenti:
                        # Il record esiste già: aggiorniamo i dati in modo intelligente solo se lo stato precedente era instabile
                        idx_esistente = mappa_chiavi_esistenti[chiave_nuova]
                        stato_prec = str(df_storico_esistente.at[idx_esistente, 'Esito_1X2']).upper().strip()
                        
                        if "ATTESA" in stato_prec or "NON RILEVATO" in stato_prec or stato_prec == "-":
                            for col in df_da_appendere.columns:
                                if col in df_storico_esistente.columns:
                                    df_storico_esistente.at[idx_esistente, col] = riga[col]
                    else:
                        # È un match completamente nuovo: lo inseriamo nella coda di inserimento
                        nuovi_record.append(riga)
                
                if nuovi_record:
                    df_nuovi = pd.DataFrame(nuovi_record)
                    df_storico_aggiornato = pd.concat([df_storico_esistente, df_nuovi], ignore_index=True, sort=False)
                    df_storico_aggiornato.to_excel(DATABASE_STORICO_GLOBALE, index=False)
                    print("✅ Sincronizzazione completata: Nuovi record aggiunti in append.")
                else:
                    # Se non ci sono nuovi record, risalviamo la matrice esistente (potenzialmente aggiornata negli stati)
                    df_storico_esistente.to_excel(DATABASE_STORICO_GLOBALE, index=False)
                    print("✅ Sincronizzazione completata: Nessun nuovo match, aggiornati stati esistenti.")
            else:
                # Se il file esiste ma è vuoto, lo scriviamo direttamente
                df_da_appendere.to_excel(DATABASE_STORICO_GLOBALE, index=False)
        else:
            # Se non esiste, creiamo il file direttamente
            df_da_appendere.to_excel(DATABASE_STORICO_GLOBALE, index=False)
            print("✅ Sincronizzazione completata: Creato nuovo database storico globale.")
            
    except Exception as e:
        print(f"❌ Errore controllato: {e}")
        raise e

def esegui_allineamento():
    _logica_core_trasferimento()

def esegui_trasferimento():
    _logica_core_trasferimento()

sys.modules[__name__].esegui_allineamento = esegui_allineamento
sys.modules[__name__].esegui_trasferimento = esegui_trasferimento
