import sys
import os
import pandas as pd

# PROGRESSIVO CHAT: #160 | Data: 30 Giugno 2026 | Ora: 22:30:15
# Versione Progetto: 6.44 (Fix Dtype Float64 su Fusione Stringhe Combinate MultiGoal)

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
            
        # Elenco completo delle colonne dei mercati e pronostici testuali per forzare il tipo stringa
        colonne_mercati_testo = [
            "1X2", "Risultato_Esatto", "Doppia_Chance", "DC+U/O2.5", 
            "U/O_1.5", "U/O_2.5", "U/O_3.5", "Goal_NoGoal", "Corner_1X2",
            "Pronostico_MG_Casa", "MG_Casa", "MG Casa",
            "Pronostico_MG_Trasferta", "MG_Ospite", "MG Ospite",
            "Pronostico_MG_Totale", "MG_Totale", "MG Totale",
            "Risultato_Reale", "Esito_1X2"
        ]

        # Forza il tipo stringa sul file da appendere per evitare il crash su valori tipo '2-4 / 2-4'
        for col in colonne_mercati_testo:
            if col in df_da_appendere.columns:
                df_da_appendere[col] = df_da_appendere[col].astype(str)
            
        # --- ALLINEAMENTO DI SICUREZZA DELLE COLONNE CRUCIALI ---
        mappa_repliche = {
            'Risultato_Reale': ['Risultato Reale', 'Risultato', 'Esito_Finale', 'Risultato_Finale'],
            'Esito_1X2': ['Esito 1X2', 'Esito', '1X2']
        }
        
        for col_target, varianti in mappa_repliche.items():
            if col_target not in df_da_appendere.columns:
                for v in varianti:
                    if v in df_da_appendere.columns:
                        df_da_appendere[col_target] = df_da_appendere[v].astype(str)
                        break
                if col_target not in df_da_appendere.columns:
                    df_da_appendere[col_target] = "Dato Non Rilevato"

        # Se esiste già un archivio globale, lo fondiamo controllando i duplicati
        if os.path.exists(DATABASE_STORICO_GLOBALE):
            df_storico_esistente = pd.read_excel(DATABASE_STORICO_GLOBALE)
            
            if not df_storico_esistente.empty:
                # Forza il tipo stringa anche sul database storico globale per uniformare i tipi di dato
                for col in colonne_mercati_testo:
                    if col in df_storico_esistente.columns:
                        df_storico_esistente[col] = df_storico_esistente[col].astype(str)
                    elif col in df_da_appendere.columns:
                        df_storico_esistente[col] = "-"

                # Creiamo una mappatura indice -> chiave per aggiornare record esistenti
                mappa_chiavi_esistenti = {}
                for idx, riga in df_storico_esistente.iterrows():
                    chk_key = genera_chiave_univoca_local(riga)
                    mappa_chiavi_esistenti[chk_key] = idx
                
                nuovi_record = []
                for _, riga in df_da_appendere.iterrows():
                    chiave_nuova = genera_chiave_univoca_local(riga)
                    
                    if chiave_nuova in mappa_chiavi_esistenti:
                        # Il record esiste già: aggiorniamo i dati solo se lo stato precedente era instabile
                        idx_esistente = mappa_chiavi_esistenti[chiave_nuova]
                        stato_prec = str(df_storico_esistente.at[idx_esistente, 'Esito_1X2']).upper().strip()
                        
                        if "ATTESA" in stato_prec or "NON RILEVATO" in stato_prec or stato_prec == "-" or stato_prec == "NAN":
                            for col in df_da_appendere.columns:
                                if col in df_storico_esistente.columns:
                                    df_storico_esistente.at[idx_esistente, col] = str(riga[col])
                    else:
                        # È un match completamente info: lo inseriamo nella coda di inserimento
                        nuovi_record.append(riga)
                
                if nuovi_record:
                    df_nuovi = pd.DataFrame(nuovi_record)
                    # Sincronizzazione dei tipi prima del concat
                    for col in colonne_mercati_testo:
                        if col in df_nuovi.columns:
                            df_nuovi[col] = df_nuovi[col].astype(str)
                    
                    df_storico_aggiornato = pd.concat([df_storico_esistente, df_nuovi], ignore_index=True, sort=False)
                    df_storico_aggiornato.to_excel(DATABASE_STORICO_GLOBALE, index=False)
                    print("✅ Sincronizzazione completata: Nuovi record aggiunti in append.")
                else:
                    df_storico_esistente.to_excel(DATABASE_STORICO_GLOBALE, index=False)
                    print("✅ Sincronizzazione completata: Nessun nuovo match, aggiornati stati esistenti.")
            else:
                df_da_appendere.to_excel(DATABASE_STORICO_GLOBALE, index=False)
        else:
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
