import os
import sys

def scopri_percorso():
    print("\n==================================================")
    print("🔍 ISPEZIONE PERCORSI MACBOOK - BETTING PRO MOBILE")
    print("==================================================")
    
    # Rileva la cartella esatta di questo script
    cartella_corrente = os.path.dirname(os.path.abspath(__file__))
    print(f"📍 La cartella esatta di questo modulo sul tuo Mac è:\n   {cartella_corrente}\n")
    
    # Rileva dove Python sta cercando e salvando i file in questo momento
    working_dir = os.getcwd()
    print(f"📂 I file Excel vengono cercati/salvati in questa cartella:\n   {working_dir}\n")
    
    # Elenca i file presenti nella cartella per verifica
    print("🗂️ Elenco file trovati in questa cartella:")
    try:
        file_presenti = os.listdir(working_dir)
        for f in sorted(file_presenti):
            if f.endswith(".py") or f.endswith(".xlsx"):
                print(f"   • {f}")
    except Exception as e:
        print(f"❌ Impossibile leggere i file: {e}")
    print("==================================================\n")

if __name__ == "__main__":
    scopri_percorso()
