import pandas as pd
import os

# PROGRESSIVO CHAT: #142 | Data: 30 Giugno 2026
# Modulo 03: Validatore con logica booleana corretta per il calcolo dei range Multigol (0 inclusivo)

STORICO_FILE = "Storico_Validato_Betting.xlsx"

def controlla_range_multigol(pronostico_str, gol_effettivi):
    """Scompone la stringa (es. '0-1 MG' o '1-3') e verifica se i gol effettivi rientrano nel range numerico"""
    p_str = str(pronostico_str).upper().replace("MG", "").strip()
    if p_str == "-" or p_str == "NONE" or not p_str:
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
        return
        
    try:
        df = pd.read_excel(STORICO_FILE)
    except:
        return

    if df.empty:
        return

    for idx, row in df.iterrows():
        ris_reale = str(row.get('Risultato_Reale', '')).strip()
        if not ris_reale or "-" not in ris_reale or ris_reale.upper() == "NONE":
            continue
            
        try:
            gol_casa = int(ris_reale.split("-")[0].strip())
            gol_ospite = int(ris_reale.split("-")[1].strip())
        except:
            continue

        # 1. Validazione Multigol Casa
        p_casa = row.get('Pronostico_MG_Casa', row.get('MG_Casa', row.get('MG Casa', '-')))
        df.at[idx, 'Esito_Media_Goal_Casa'] = controlla_range_multigol(p_casa, gol_casa)
        df.at[idx, 'Esito_MG_Casa'] = controlla_range_multigol(p_casa, gol_casa)

        # 2. Validazione Multigol Ospite
        p_ospite = row.get('Pronostico_MG_Trasferta', row.get('MG_Ospite', row.get('MG Ospite', '-')))
        df.at[idx, 'Esito_Media_Goal_Trasferta'] = controlla_range_multigol(p_ospite, gol_ospite)
        df.at[idx, 'Esito_MG_Trasferta'] = controlla_range_multigol(p_ospite, gol_ospite)

        # 3. Validazione Multigol Combinato (FasciaCasa / FasciaOspite)
        p_comb = str(row.get('Pronostico_MG_Totale', row.get('MG_Totale', row.get('MG Totale', '-')))).strip()
        if "/" in p_comb:
            try:
                parti_comb = p_comb.split("/")
                esito_c = controlla_range_multigol(parti_comb[0], gol_casa)
                esito_o = controlla_range_multigol(parti_comb[1], gol_ospite)
                
                if esito_c == "VINCENTE" and esito_o == "VINCENTE":
                    esito_finale = "VINCENTE"
                else:
                    esito_finale = "PERDENTE"
            except:
                esito_finale = "PERDENTE"
        else:
            esito_finale = "PERDENTE"
            
        df.at[idx, 'Esito_Media_Goal_Totale'] = esito_finale
        df.at[idx, 'Esito_MG_Totale'] = esito_finale

    df.to_excel(STORICO_FILE, index=False)

if __name__ == "__main__":
    esegui_validazione()
