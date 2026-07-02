import sys
import os
import pandas as pd

# PROGRESSIVO CHAT: #150 | Data: 02 Luglio 2026 | Ora: 16:16:45
# Versione Modulo: 6.87 (Modulo 04 - Corretto Refuso 'esegui_transferimento' in esegui_trasferimento)

STORICO_FILE = "Storico_Validato_Betting.xlsx"
DATABASE_STORICO_GLOBALE = "Database_Storico_Completo.xlsx"

def genera_chiave_univoca_local(row):
    data = str(row.get('Data_Ora_Match', row.get('Data', row.get('2. Data', '')))).strip()
    match_str = str(row.get('3. Match', row.get('Match', ''))).strip()
    return f"{data}_{match_str}".lower().replace(" ", "")

def _logica_core_trasferimento():
    if not os.path.exists(STORICO_FILE):
        print("⚠️ File storico sorgente non trovato.")
        return
        
    try:
        df_storico_corrente = pd.read_excel(STORICO_FILE)
        if df_storico_corrente.empty:
            print("⚠️ Lo storico sorgente è vuoto. Nessun dato da trasferire.")
            return
            
        # Elenco completo ed esteso di tutte le colonne dei mercati, pronostici ed ESITI da preservare
        colonne_mercati_testo = [
            "1X2", "Risultato_Esatto", "Doppia_Chance", "DC+U/O2.5", 
            "U/O_1.5", "U/O_2.5", "U/O_3.5", "Goal_NoGoal", "Corner_1X2",
            "Pronostico_MG_Casa", "MG_Casa", "MG Casa", "Esito_MG_Casa", "Esito_MG_Casa_Calcolato",
            "Pronostico_MG_Trasferta", "MG_Ospite", "MG Ospite", "Esito_MG_Trasferta", "Esito_MG_Ospite", "Esito_Pronostico_MG_Trasferta", "Esito_Pronostico_MG_Ospite",
            "Pronostico_MG_Totale", "MG_Totale", "MG Totale", "MG_Casa+MG_Ospite", "Esito_MG_Totale", "Esito_MG_Casa+MG_Ospite", "Esito_MG_Casa_MG_Ospite",
            "Risultato_Reale", "Esito_1X2", "Esito_Risultato_Esatto", "Esito_Doppia_Chance", 
            "Esito_DC+U/O2.5", "Esito_U/O_1.5", "Esito_U/O_2.5", "Esito_
