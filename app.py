import streamlit as st
import pandas as pd
import os

# Importazione dei moduli del progetto
import modulo_01_estrattore as m1
import modulo_03_validatore as m3
import modulo_04_trasferitore as m4

# Configurazione Geometrica Rigida per Target Mobile (Layout Corretto)
st.set_page_config(
    page_title="App Betting Pro",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Stile CSS per azzerare scroll laterali, troncamenti e ottimizzare layout verticale su display 5.8 e 6.1 pollici
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; padding-left: 0.5rem; padding-right: 0.5rem; }
    h1, h2, h3 { font-size: 1.4rem !important; text-align: center; }
    .stButton>button { width: 100%; margin-bottom: 10px; padding: 12px; font-size: 1rem; }
    th, td { font-size: 0.85rem !important; }
    </style>
""", unsafe_allow_html=True)

# Intestazione Fissa di Controllo
st.title("🏆 SISTEMA BETTING AUTOMATIZZATO")
st.write("<p style='text-align:center; color:grey;'><b>VERSIONE PROGETTO: 5.51</b></p>", unsafe_allow_html=True)
st.write(f"<p style='text-align:center; font-size:0.8rem;'>Data Sistema: 26/06/2026</p>", unsafe_allow_html=True)
st.markdown("---")

# ------------------------------------------------------------------------
# PANNELLO DI CONTROLLO DIRETTORE (LAYOUT VERTICALE MOBILE)
# ------------------------------------------------------------------------

st.subheader("🎛️ Pannello di Controllo Fasi")

if st.button("🚀 FASE 1: Estrai e Calcola Palinsesto"):
    with st.spinner("Estrazione dati e calcolo pronostici in corso..."):
        try:
            m1.esegui_estrazione()
            st.success("✅ Palinsesto congelato creato con successo!")
        except Exception as e:
            st.error(f"Errore Fase 1: {str(e)}")

if st.button("🏆 FASE 2: Convalida Risultati Reali (API)"):
    with st.spinner("Verifica match conclusi su server Football-Data..."):
        try:
            m3.esegui_validazione()
            st.success("✅ Risultati reali agganciati nello Storico Validato!")
        except Exception as e:
            st.error(f"Errore Fase 2: {str(e)}")

if st.button("💾 FASE 3: Sposta in Archivio Permanente"):
    with st.spinner("Trasferimento record anti-doppione..."):
        try:
            m4.esegui_allineamento()
            st.success("✅ Database Storico Permanente aggiornato con successo!")
        except Exception as e:
            st.error(f"Errore Fase 3: {str(e)}")

st.markdown("---")

# ------------------------------------------------------------------------
# VISUALIZZAZIONE DATI (FINESTRA DI ISPEZIONE COMPATTA)
# ------------------------------------------------------------------------
st.subheader("📊 Ispezione File Correnti")

opzione_file = st.selectbox("Seleziona l'archivio da monitorare:", [
    "Pronostici_App_Betting.xlsx (Palinsesto)",
    "Storico_Validato_Betting.xlsx (Storico Recente)",
    "Database_Storico_Completo.xlsx (Archivio Totale)"
])

file_mappa = {
    "Pronostici_App_Betting.xlsx (Palinsesto)": "Pronostici_App_Betting.xlsx",
    "Storico_Validato_Betting.xlsx (Storico Recente)": "Storico_Validato_Betting.xlsx",
    "Database_Storico_Completo.xlsx (Archivio Totale)": "Database_Storico_Completo.xlsx"
}

file_selezionato = file_mappa[opzione_file]

if os.path.exists(file_selezionato):
    try:
        df_view = pd.read_excel(file_selezionato)
        st.write(f"Righe presenti: **{len(df_view)}**")
        colonne_visibili = [c for c in ['Data_Ora_Match', '3. Match', '1X2', 'Risultato_Reale', 'Esito_1X2'] if c in df_view.columns]
        if colonne_visibili:
            st.dataframe(df_view[colonne_visibili].head(20), use_container_width=True)
        else:
            st.dataframe(df_view.head(5), use_container_width=True)
    except:
        st.warning("Impossibile leggere il file in questo momento (file vuoto o corrotto).")
else:
    st.info(f"File '{file_selezionato}' non ancora generato dal pannello feriale.")
