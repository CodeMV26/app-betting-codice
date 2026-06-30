import pandas as pd
import numpy as np
import os

# PROGRESSIVO CHAT: #158 | Data: 30 Giugno 2026 | Ora: 21:46:15
# Versione Progetto: 6.42 (Fix Sintassi df.get su Assegnazione Colonne Stringa)

PALINSESTO_FILE = "Pronostici_App_Betting.xlsx"

def calcola_fascia_multigol(media_gol):
    """Genera la stringa di fascia multigol standard basata sulla media matematica"""
    try:
        val = float(media_gol)
    except:
        val = 1.2
    
    if val < 0.85:
        return "0-1 MG"
    elif val < 1.65:
        return "1-2 MG"
    elif val < 2.45:
        return "1-3 MG"
    else:
        return "2-4 MG"

def esegui_calcolo_motore():
    if not os.path.exists(PALINSESTO_FILE):
        return
    
    try:
        # Legge il file Excel generato dall'estrattore
        df = pd.read_excel(PALINSESTO_FILE)
    except:
        return

    if df.empty:
        return

    # Elenco delle colonne destinate a contenere i testi dei pronostici per la UI mobile
    colonne_testo = [
        'Pronostico_MG_Casa', 'MG_Casa', 'MG Casa',
        'Pronostico_MG_Trasferta', 'MG_Ospite', 'MG Ospite',
        'Pronostico_MG_Totale', 'MG_Totale', 'MG Totale'
    ]
    
    # Inizializzazione sicura e conversione a stringa nativa per evitare crash strutturali
    for col in colonne_testo:
        if col not in df.columns:
            df[col] = "-"
        else:
            df[col] = df[col].astype(str)

    for idx, row in df.iterrows():
        # Estrae il valore numerico puro senza alterare la colonna originale _Orig
        mg_casa_attesa = row.get('Media_Goal_Casa_Orig', 1.2)
        mg_ospite_attesa = row.get('Media_Goal_Trasferta_Orig', 1.1)
        
        # Calcolo protetto delle fasce stringa
        fascia_casa = calcola_fascia_multigol(mg_casa_attesa)
        fascia_ospite = calcola_fascia_multigol(mg_ospite_attesa)
        
        # Scrittura esclusiva nelle colonne destinate al testo dell'interfaccia UI
        df.at[idx, 'Pronostico_MG_Casa'] = fascia_casa
        df.at[idx, 'MG_Casa'] = fascia_casa
        df.at[idx, 'MG Casa'] = fascia_casa
        
        df.at[idx, 'Pronostico_MG_Trasferta'] = fascia_ospite
        df.at[idx, 'MG_Ospite'] = fascia_ospite
        df.at[idx, 'MG Ospite'] = fascia_ospite
        
        # Generazione mercato combinato nel formato richiesto "FasciaCasa / FasciaOspite"
        fascia_combinata = f"{fascia_casa.replace(' MG','')} / {fascia_ospite.replace(' MG','')}"
        df.at[idx, 'Pronostico_MG_Totale'] = fascia_combinata
        df.at[idx, 'MG_Totale'] = fascia_combinata
        df.at[idx, 'MG Totale'] = fascia_combinata

    # Sovrascrittura protetta del file Excel
    df.to_excel(PALINSESTO_FILE, index=False)

if __name__ == "__main__":
    esegui_calcolo_motore()
