import streamlit as st
import pandas as pd
import os
from datetime import datetime
import zoneinfo
import requests

# 1. Configurazione rigida per fuso orario italiano (Must 2)
FUSO_ORARIO = zoneinfo.ZoneInfo("Europe/Rome")

st.set_page_config(page_title="Pannello Betting", page_icon="⚽", layout="centered")

# Stile CSS per iPhone (Ottimizzazione Spazi e Visibilità delle Colonne)
st.markdown("""
    <style>
    .main { background-color: #f2f2f7; }
    .card {
        background-color: white;
        padding: 12px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 12px;
        border-left: 5px solid #007aff;
    }
    .time-label { color: #8e8e93; font-size: 11px; font-weight: bold; }
    .market-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 6px;
        margin-top: 8px;
        font-size: 13px;
    }
    .market-item { background: #f8f9fa; padding: 4px 8px; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

# Recupero delle chiavi di attivazione reali inserite nei Secrets
TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO = st.secrets.get("GITHUB_REPO", "")

st.title("⚽ Controllo Betting Pro")
st.subheader("🛠️ Console Operativa Moduli")

col1, col2 = st.columns(2)

# PULSANTE REALE FASE 1
with col1:
    if st.button("🚀 Avvia Fase 1 (Pre-Match: Moduli 01+02)"):
        if not TOKEN or not REPO:
            st.error("❌ Chiavi di connessione mancanti nei Secrets di Streamlit.")
        else:
            with st.spinner("Azzeramento e attivazione Fase 1..."):
                url = f"https://api.github.com/repos/{REPO}/actions/workflows/pre-match.yml/dispatches"
                headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
                response = requests.post(url, headers=headers, json={"ref": "main"})
                if response.status_code == 204:
                    st.success("🔄 Fase 1 partita sul server! Attendi 30-40 secondi e aggiorna la pagina.")
                else:
                    st.error(f"❌ Errore server Fase 1: {response.status_code}")

# PULSANTE REALE FASE 2
with col2:
    if st.button("📊 Avvia Fase 2 (Post-Match: Moduli 03+04+05)"):
        if not TOKEN or not REPO:
            st.error("❌ Chiavi di connessione mancanti nei Secrets di Streamlit.")
        else:
            with st.spinner("Attivazione Fase 2..."):
                # Qui si collega al file del workflow post-match (es. post-match.yml)
                url = f"https://api.github.com/repos/{REPO}/actions/workflows/post-match.yml/dispatches"
                headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
                response = requests.post(url, headers=headers, json={"ref": "main"})
                if response.status_code == 204:
                    st.success("🔄 Fase 2 partita sul server! Elaborazione post-match in corso.")
                else:
                    st.error(f"❌ Errore server Fase 2: {response.status_code}")

# Lettura e visualizzazione dell'orario con fuso orario italiano corretto (Must 2)
if os.path.exists("Pronostici_App_Betting.xlsx"):
    mtime = os.path.getmtime("Pronostici_App_Betting.xlsx")
    data_ora = datetime.fromtimestamp(mtime, tz=FUSO_ORARIO).strftime('%d/%m/%Y %H:%M:%S')
    st.caption(f"⏱️ **Ultima elaborazione dati reale eseguita il:** {data_ora}")
else:
    st.caption("⏱️ **Ultima elaborazione dati reale eseguita il:** Nessun dato in memoria (Pronto per nuova estrazione)")

# Visualizzazione tabellare dei mercati reali strutturati (Must 3 e Must 4)
tabs = st.tabs(["🎯 Palinsesto & Pronostici", "📊 Storico Validato"])

with tabs[0]:
    if os.path.exists("Pronostici_App_Betting.xlsx"):
        try:
            df = pd.read_excel("Pronostici_App_Betting.xlsx")
            if df.empty:
                st.info("Nessun match presente in palinsesto dal provider reale.")
            else:
                for idx, row in df.iterrows():
                    st.markdown(f"""
                    <div class="card">
                        <div class="time-label">📅 {row.get('Data_Ora_Match', 'Data/Ora Non Disponibile')} | 🏆 {row.get('Campionato', 'Competizione')}</div>
                        <h4 style="margin: 4px 0; color: #1c1c1e;">{row.get('3. Match', 'Match')}</h4>
                        <div class="market-grid">
                            <div class="market-item"><b>1X2:</b> {row.get('1X2', '-')}</div>
                            <div class="market-item"><b>Esatto:</b> {row.get('Risultato_Esatto', '-')}</div>
                            <div class="market-item"><b>Doppia:</b> {row.get('Doppia_Chance', '-')}</div>
                            <div class="market-item"><b>U/O 1.5:</b> {row.get('U/O_1.5', '-')}</div>
                            <div class="market-item"><b>U/O 2.5:</b> {row.get('U/O_2.5', '-')}</div>
                            <div class="market-item"><b>U/O 3.5:</b> {row.get('U/O_3.5', '-')}</div>
                            <div class="market-item"><b>G/NG:</b> {row.get('Goal_NoGoal', '-')}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Errore tecnico di lettura: {e}")
    else:
        st.info("Nessun dato attivo. Premi il pulsante sopra per avviare l'estrazione reale.")

with tabs[1]:
    if os.path.exists("Storico_Validato_Betting.xlsx"):
        try:
            df_storico = pd.read_excel("Storico_Validato_Betting.xlsx")
            st.metric(label="Match Reali Archiviati", value=len(df_storico))
            st.dataframe(df_storico, use_container_width=True)
        except Exception as e:
            st.error(f"Errore lettura storico: {e}")
    else:
        st.info("L'archivio storico reale apparirà dopo la prima validazione post-match (Fase 2).")
