import os
import pandas as pd

# PROGRESSIVO CHAT: #152 | Data: 06 Luglio 2026 | Ora: 12:35:48
# Versione Progetto: 6.99 | MODULO 06: ENGINE AUTOMATICO CON PERCORSO NATIVO MAC OS

def carica_eureka_file():
    """
    Carica il database EUREKA_RECORDS.xlsx puntando direttamente al percorso
    assoluto nativo definito su ambiente macOS.
    """
    # Percorso assoluto fornito dall'utente
    cartella_target = "/Users/michelevagnino/Documents/Analisi_Scommesse_Professional"
    nome_file = "EUREKA_RECORDS.xlsx"
    percorso_completo = os.path.join(cartella_target, nome_file)
    
    print(f"[MODULO 06] Tentativo di lettura in corso su: {percorso_completo}")
    
    if not os.path.exists(percorso_completo):
        print(f"[MODULO 06] ERRORE CRITICO: Il file non esiste in {percorso_completo}")
        print("[MODULO 06] Genero un DataFrame vuoto di sicurezza per evitare il crash.")
        # Struttura coerente minima con l'interfaccia dell'archivio storico
        colonne_default = [
            'Campionato', 'Squadra_Casa', 'Squadra_Ospite', 
            'Media_Goal_Casa_Orig', 'Media_Goal_Trasferta_Orig', 'Risultato_Reale'
        ]
        return pd.DataFrame(columns=colonne_default)
        
    try:
        # Lettura nativa del file Excel
        df = pd.read_excel(percorso_completo)
        print(f"[MODULO 06] Connessione riuscita! Record rilevati: {len(df)}")
        return df
    except Exception as e:
        print(f"[MODULO 06] Errore imprevisto durante l'apertura del file Excel: {str(e)}")
        return pd.DataFrame()

def elabora_input_eureka():
    """
    Funzione di interfaccia principale chiamata dai moduli esterni.
    Pulisce gli spazi bianchi e normalizza le stringhe caricate.
    """
    df_eureka = carica_eureka_file()
    
    if df_eureka.empty:
        return df_eureka

    # Sanificazione automatica stringhe per prevenire errori di tipo nel simulatore
    for col in df_eureka.columns:
        if df_eureka[col].dtype == object:
            df_eureka[col] = df_eureka[col].fillna("-").astype(str).str.strip()
            
    return df_eureka
