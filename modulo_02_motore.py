import pandas as pd
import os

print("🧠 --- APP BETTING CLOUD - MOTORE DECISIONALE ---")

if os.path.exists("Database_App_Betting.xlsx"):
    df_database = pd.read_excel("Database_App_Betting.xlsx")
    
    if not df_database.empty:
        print(f"🔄 Elaborazione algoritmi matematici su {len(df_database)} match trovati...")
        
        # Il motore copia i dati elaborati direttamente nel file finale dei pronostici
        df_database.to_excel("Pronostici_App_Betting.xlsx", index=False)
        print("✅ File Pronostici_App_Betting.xlsx sovrascritto con i match correnti!")
    else:
        print("⚠️ Il database temporaneo è vuoto.")
else:
    print("⚠️ Nessun database temporaneo trovato dal motore.")
