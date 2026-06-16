import streamlit as st
import pandas as pd
import os
import subprocess

st.set_page_config(page_title="App Betting Cloud v5.0", layout="wide")

st.title("⚽ APP BETTING CLOUD")
st.write("Predizioni Dixon-Coles ottimizzate per iPhone")

# Pulsanti di comando compatti per esecuzione sul server Cloud
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🚀 Fase 1", use_container_width=True):
        with st.spinner("Estrazione..."):
            try:
                subprocess.run(["python", "modulo_01_estrattore.py"], capture_output=True, text=True)
                st.success("Fase 1 OK")
            except Exception as e:
                st.error(f"Errore: {e}")

with col2:
    if st.button("🧠 Fase 2", use_container_width=True):
        with st.spinner("Calcolo..."):
            try:
                subprocess.run(["python", "modulo_02_motore.py"], capture_output=True, text=True)
                st.success("Fase 2 OK")
            except Exception as e:
                st.error(f"Errore: {e}")

with col3:
    if st.button("✅ Fase 3", use_container_width=True):
        with st.spinner("Validazione..."):
            try:
                subprocess.run(["python", "modulo_03_validatore.py"], capture_output=True, text=True)
                st.success("Fase 3 OK")
            except Exception as e:
                st.error(f"Errore: {e}")

st.markdown("---")

PRONOSTICI_FILE = "Pronostici_App_Betting.xlsx"

if os.path.exists(PRONOSTICI_FILE):
    df_visualizzazione = pd.read_excel(PRONOSTICI_FILE)
    
    if not df_visualizzazione.empty:
        # STRUTTURA CONSERVATA: Manteniamo l'ordine originale e compattiamo i nuovi dati richiesti
        colonne_selezionate = [
            "Campionato", 
            "Data_Ora_Match", 
            "3. Match",            # Conservato nella sua posizione nativa
            "Punti_Casa", 
            "Punti_Trasferta", 
            "1X2", 
            "Risultato_Esatto", 
            "DC+U/O2.5",           # Nuova richiesta inserita a centro tabella
            "Media_Goal_Casa",     # Nuova richiesta (Range xG Casa)
            "Media_Goal_Trasferta",# Nuova richiesta (Range xG Trasf)
            "Corner_1X2",          # Nuova richiesta
            "Odds_1X2"             # Nuova richiesta
        ]
        
        colonne_presenti = [col for col in colonne_selezionate if col in df_visualizzazione.columns]
        df_pulito = df_visualizzazione[colonne_presenti]
        
        # ABBREVIAZIONI CHIRURGICHE PER EVITARE LO SCROLL ORIZZONTALE SU IPHONE X
        df_rinominato = df_pulito.rename(columns={
            "Campionato": "Camp.",
            "Data_Ora_Match": "Ora (ITA)",
            "3. Match": "Match",
            "Punti_Casa": "Pt.C",
            "Punti_Trasferta": "Pt.T",
            "Risultato_Esatto": "Ris.Es.",
            "DC+U/O2.5": "Combo DC+U/O",
            "Media_Goal_Casa": "xG Casa",
            "Media_Goal_Trasferta": "xG Trasf",
            "Corner_1X2": "Corn",
            "Odds_1X2": "Quota"
        })
        
        # Mostra la tabella responsive adatta allo schermo mobile
        st.dataframe(df_rinominato, use_container_width=True, hide_index=True)
    else:
        st.info("Database vuoto. Esegui Fase 1 e Fase 2.")
else:
    st.warning("Nessun dato. Clicca sui pulsanti sopra.")
