import streamlit as st
import pandas as pd
import os
import subprocess

st.set_page_config(page_title="App Betting Cloud v5.0", layout="wide")

st.title("⚽ APP BETTING CLOUD - PANNELLO CONTROLLO")
st.write("Sincronizzazione dati live e calcolo predittivo Dixon-Coles.")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🚀 Avvia Fase 1 (Estrattore)", use_container_width=True):
        with st.spinner("Estrazione dati reali in corso..."):
            try:
                result = subprocess.run(["python", "modulo_01_estrattore.py"], capture_output=True, text=True)
                st.success("Fase 1 completata con successo!")
                st.text(result.stdout)
            except Exception as e:
                st.error(f"Errore esecuzione: {e}")

with col2:
    if st.button("🧠 Avvia Fase 2 (Motore)", use_container_width=True):
        with st.spinner("Elaborazione formule Poisson e Dixon-Coles..."):
            try:
                result = subprocess.run(["python", "modulo_02_motore.py"], capture_output=True, text=True)
                st.success("Fase 2 completata! Pronostici pronti.")
                st.text(result.stdout)
            except Exception as e:
                st.error(f"Errore esecuzione: {e}")

with col3:
    if st.button("✅ Avvia Fase 3 (Validatore)", use_container_width=True):
        with st.spinner("Validazione risultati passati..."):
            try:
                result = subprocess.run(["python", "modulo_03_validatore.py"], capture_output=True, text=True)
                st.success("Storicizzazione completata!")
                st.text(result.stdout)
            except Exception as e:
                st.error(f"Errore esecuzione: {e}")

st.markdown("---")
st.subheader("📋 Tabellone Analisi e Pronostici Real-Time")

PRONOSTICI_FILE = "Pronostici_App_Betting.xlsx"

if os.path.exists(PRONOSTICI_FILE):
    df_visualizzazione = pd.read_excel(PRONOSTICI_FILE)
    
    if not df_visualizzazione.empty:
        colonne_selezionate = [
            "Campionato", 
            "Data_Ora_Match", 
            "3. Match", 
            "Punti_Casa", 
            "Punti_Trasferta", 
            "1X2", 
            "Risultato_Esatto", 
            "DC+U/O2.5", 
            "Media_Goal_Casa", 
            "Media_Goal_Trasferta", 
            "Corner_1X2", 
            "Odds_1X2"
        ]
        
        colonne_presenti = [col for col in colonne_selezionate if col in df_visualizzazione.columns]
        df_pulito = df_visualizzazione[colonne_presenti]
        
        df_rinominato = df_pulito.rename(columns={
            "Data_Ora_Match": "Data & Ora (ITA)",
            "3. Match": "Partita",
            "Punti_Casa": "PT Casa",
            "Punti_Trasferta": "PT Trasf",
            "DC+U/O2.5": "Combo DC + U/O 2.5",
            "Media_Goal_Casa": "Range Goal Casa (xG)",
            "Media_Goal_Trasferta": "Range Goal Trasf (xG)",
            "Corner_1X2": "Corner (1X2)",
            "Odds_1X2": "Quota 1X2"
        })
        
        st.dataframe(df_rinominato, use_container_width=True, hide_index=True)
    else:
        st.info("Il database dei pronostici è vuoto. Esegui la Fase 1 e la Fase 2.")
else:
    st.warning(f"File {PRONOSTICI_FILE} non ancora generato. Clicca sui pulsanti sopra.")
