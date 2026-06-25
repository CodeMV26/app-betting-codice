import streamlit as st
import pandas as pd
import os

# Importazione dei moduli core del progetto
import modulo_01_estrattore as m1
import modulo_03_validatore as m3
import modulo_04_trasferitore as m4

# Configurazione standard e pulita
st.set_page_config(
    page_title="App Betting Pro",
    layout="centered"
)

st.title("🏆 SISTEMA BETTING")
st.write("### VERSIONE PROGETTO: 5.52")
st.markdown("---")

# --- PULSANTI OPERATIVI ---

if st.button("🚀 FASE 1: Estrai e Calcola Palinsesto"):
    try:
        m1.esegui_estrazione()
        st.success("Palinsesto aggiornato!")
    except Exception as e:
        st.error(f"Errore: {str(e)}")

if st.button("🏆 FASE 2: Convalida Risultati Reali"):
    try:
        m3.esegui_validazione()
        st.success("Risultati reali aggiornati!")
    except Exception as e:
        st.error(f"Errore: {str(e)}")

if st.button("💾 FASE 3: Sposta in Archivio Permanente"):
    try:
        m4.esegui_allineamento()
        st.success("Database permanente allineato!")
    except Exception as e:
        st.error(f"Errore: {str(e)}")

st.markdown("---")

# --- ISPEZIONE VELOCE DEI DATI ---
st.subheader("📊 Visualizzazione Tabelle")

file_scelto = st.radio("Scegli file:", [
    "Pronostici_App_Betting.xlsx",
    "Storico_Validato_Betting.xlsx",
    "Database_Storico_Completo.xlsx"
])

if os.path.exists(file_scelto):
    try:
        df = pd.read_excel(file_scelto)
        st.write(f"Righe totali: {len(df)}")
        st.dataframe(df.head(30))
    except Exception as e:
        st.warning("Se il file è aperto su Excel, chiudilo per vederlo qui.")
else:
    st.info("File non ancora generato.")
