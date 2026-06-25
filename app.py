import streamlit as st
import pandas as pd
import os

# Configurazione pulita e nativa adatta a display iPhone X / 13
st.set_page_config(
    page_title="App Betting Pro - Emergenza",
    layout="centered"
)

st.title("🏆 SISTEMA BETTING (MODO EMERGENZA)")
st.write("### VERSIONE PROGETTO: 5.53")
st.write("⚙️ *Interfaccia isolata per bypassare blocchi dei moduli esterni.*")
st.markdown("---")

# --- PANNELLO OPERATIVO COMPATTO ---
st.subheader("🎛️ Pannello di Controllo File Diretti")

st.info("I pulsanti sottostanti leggono direttamente i file Excel nel Finder per verificare lo stato attuale dei dati senza rischiare blocchi software.")

# --- ISPEZIONE DI SICUREZZA ---
st.subheader("📊 Ispezione Archivi Correnti")

file_scelto = st.selectbox("Seleziona il file da caricare a schermo:", [
    "Pronostici_App_Betting.xlsx",
    "Storico_Validato_Betting.xlsx",
    "Database_Storico_Completo.xlsx"
])

if os.path.exists(file_scelto):
    try:
        df = pd.read_excel(file_scelto)
        st.success(f"✅ File caricato con successo! Righe totali: {len(df)}")
        
        # Filtro colonne visualizzabili su mobile per evitare scroll laterali distruttivi
        colonne_visibili = [c for c in ['Data_Ora_Match', '3. Match', '1X2', 'Risultato_Reale', 'Esito_1X2'] if c in df.columns]
        
        if colonne_visibili:
            st.dataframe(df[colonne_visibili].head(50), use_container_width=True)
        else:
            st.dataframe(df.head(20), use_container_width=True)
            
    except Exception as e:
        st.error(f"Impossibile leggere il file Excel: {str(e)}. Assicurati che non sia aperto in questo momento su Microsoft Excel.")
else:
    st.warning(f"⚠️ Il file '{file_scelto}' non esiste nella cartella corrente del progetto.")
