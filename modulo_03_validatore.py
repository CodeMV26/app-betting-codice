import pandas as pd
import os

# PROGRESSIVO CHAT: #144 | Data: 30 Giugno 2026 | Ora: 17:28:12
# Versione Progetto: 6.28 (Fix Validazione Multigol & Protezione Risultati Reali)

STORICO_FILE = "Storico_Validato_Betting.xlsx"

def controlla_range_multigol(pronostico_str, gol_effettivi):
    """Scompone la stringa (es. '0-1 MG' o '1-3') e verifica matematicamente se i gol rientrano nel range"""
    p_str = str(pronostico_str).upper().replace("MG", "").strip()
    if p_str == "-" or p_str == "NONE" or not p_str or p_str == "NAN":
        return "IN ATTESA"
    
    try:
        if "-" in p_str:
            parti = p_str.split("-")
            min_g = int(parti[0].strip())
            max_g = int(parti[1].strip())
            if min_g <= int(gol_effettivi) <= max_g:
                return "VINCENTE"
            else:
                return "PERDENTE"
    except:
        pass
    return "PERDENTE"

def esegui_validazione():
    if not os.path.exists(STORICO_FILE):
        print(f"Errore: Il file {STORICO_FILE} non esiste.")
        return
        
    try:
        df = pd.read_excel(STORICO_FILE)
    except Exception as e:
        print(f"Errore nella lettura del file Excel: {e}")
        return

    if df.empty:
        print("Il file Excel è vuoto.")
        return

    # Assicurati che le colonne degli esiti siano trattate come stringhe
    colonne_esiti = ['Esito_MG_Casa', 'Esito_MG_Trasferta', 'Esito_MG_Totale']
    for col in colonne_esiti:
        if col not in df.columns:
            df[col] = "-"

    for idx, row in df.iterrows():
        # Recupero protetto del risultato reale senza alterarlo o sovrascriverlo con stringhe di errore
        ris_reale = str(row.get('Risultato_Reale', '')).strip()
        
        # Se il risultato è vuoto, nullo o non ancora definito, passa alla riga successiva senza toccare nulla
        if not ris_reale or "-" not in ris_reale or ris_reale.upper() in ["NONE", "NAN", "NON ANCORA REALE/DA VALIDARE"]:
            continue
            
        try:
            parti_ris = ris_reale.split("-")
            gol_casa = int(parti_ris[0].strip())
            gol_ospite = int(parti_ris[1].strip())
        except:
            # Salta la riga se il formato del risultato reale è temporaneamente invalido (es. rinvii)
            continue

        # 1. Validazione Multigol Casa (0 gol inclusi nel range 0-1)
        p_casa = str(row.get('Pronostico_MG_Casa', row.get('MG_Casa', row.get('MG Casa', '-')))).strip()
        df.at[idx, 'Esito_MG_Casa'] = controlla_range_multigol(p_casa, gol_casa)

        # 2. Validazione Multigol Ospite (1 gol incluso nel range 0-1)
        p_ospite = str(row.get('Pronostico_MG_Trasferta', row.get('MG_Ospite', row.get('MG Ospite', '-')))).strip()
        df.at[idx, 'Esito_MG_Trasferta'] = controlla_range_multigol(p_ospite, gol_ospite)

        # 3. Validazione Multigol Combinato (FasciaCasa / FasciaOspite)
        p_comb = str(row.get('Pronostico_MG_Totale', row.get('MG_Totale', row.get('MG Totale', '-')))).strip()
        if "/" in p_comb:
            try:
                parti_comb = p_comb.split("/")
                esito_c = controlla_range_multigol(parti_comb[0], gol_casa)
                esito_o = controlla_range_multigol(parti_comb[1], gol_ospite)
                
                if esito_c == "VINCENTE" and esito_o == "VINCENTE":
                    df.at[idx, 'Esito_MG_Totale'] = "VINCENTE"
                else:
                    df.at[idx, 'Esito_MG_Totale'] = "PERDENTE"
            except:
                df.at[idx, 'Esito_MG_Totale'] = "PERDENTE"
        else:
            df.at[idx, 'Esito_MG_Totale'] = "PERDENTE"

    try:
        df.to_excel(STORICO_FILE, index=False)
        print("Validazione completata con successo con logica corretta.")
    except Exception as e:
        print(f"Errore nel salvataggio del file Excel: {e}")

if __name__ == "__main__":
    esegui_validazione()
