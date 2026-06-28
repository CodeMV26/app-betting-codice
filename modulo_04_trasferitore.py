import sys
import os
import pandas as pd

# PROGRESSIVO CHAT: #094 | Data: 28 Giugno 2026 | Ora: 16:55:40
# Versione Modulo: 5.94 (Fix Sintattico Totale)

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
            
        varianti_risultato = ['Risultato_Reale', 'Risultato Reale', 'Risultato', 'Esito_Finale', 'Gol_Fatti_Totali']
        varianti_esito = ['Esito 1X2', 'Esito_1X2', 'Esito', '1X2']
        
        for idx, row in df_da_appendere.iterrows():
            valore_risultato = None
            for var in varianti_risultato:
                if var in df_da_appendere.columns and pd.notna(row[var]) and str(row[var]).strip() != "":
                    valore_risultato = row[var]
                    break
            
            valore_esito = None
            for var in varianti_esito:
                if var in df_da_appendere.columns and pd.notna(row[var]) and str(row[var]).strip() != "":
                    valore_esito = row[var]
                    break
                    
            if valore_risultato is not None:
                for var in varianti_risultato:
                    df_da_appendere.at[idx, var] = valore_risultato
            if valore_esito is not None:
                for var in varianti_esito:
                    df_da_appendere.at[idx, var] = valore_esito

        if os.path.exists(DATABASE_STORICO_GLOBALE):
            try:
                os.remove(DATABASE_STORICO_GLOBALE)
            except:
                pass
                
        df_da_appendere.to_excel(DATABASE_STORICO_GLOBALE, index=False)
            
    except Exception as e:
        raise e

def esegui_allineamento():
    _logica_core_trasferimento()

def esegui_trasferimento():
    _logica_core_trasferimento()

sys.modules[__name__].esegui_allineamento = esegui_allineamento
sys.modules[__name__].esegui_trasferimento = esegui_trasferimento
