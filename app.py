import streamlit as st
import pandas as pd
import os
from datetime import datetime
import zoneinfo
import requests

# 1. Configurazione rigida per fuso orario italiano
FUSO_ORARIO = zoneinfo.ZoneInfo("Europe/Rome")

st.set_page_config(page_title="Pannello Betting", page_icon="⚽", layout="centered")

# Stile CSS ottimizzato per iPhone X (Card verticali e badge esiti)
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
    .card-storico {
        background-color: white;
        padding: 12px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 12px;
        border-left: 5px solid #34c759;
    }
    .time-label { color: #8e8e93; font-size: 11px; font-weight: bold; }
    .standing-label { color: #ff9500; font-size: 11px; font-weight: bold; margin-top: 2px; }
    .result-label { color: #1c1c1e; font-size: 14px; font-weight: bold; margin: 4px 0; background: #e5e5ea; padding: 4px 8px; border-radius: 5px; display: inline-block; }
    .market-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 6px;
        margin-top: 8px;
        font-size: 13px;
    }
    .market-item { background: #f8f9fa; padding: 4px 8px; border-radius: 4px; }
    .esito-vincente { color: #34c759; font-weight: bold; }
    .esito-perdente { color: #ff3b30; font-weight: bold; }
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
                headers = {
                    "Authorization": f"token {TOKEN}",
                    "Accept": "application/vnd.github.v3+json",
                    "Content-Type": "application/json"
                }
                response = requests.post(url, headers=headers, json={"ref": "main"})
                if response.status_code == 204:
                    st.success("🔄 Fase 1 partita! Attendi 30-40 secondi e aggiorna.")
                else:
                    st.error(f"❌ Errore server Fase 1: {response.status_code}")

# PULSANTE REALE FASE 2
with col2:
    if st.button("📊 Avvia Fase 2 (Post-Match: Moduli 03+04+05)"):
        if not TOKEN or not REPO:
            st.error("❌ Chiavi di connessione mancanti nei Secrets di Streamlit.")
        else:
            with st.spinner("Attivazione Fase 2..."):
                url = f"https://api.github.com/repos/{REPO}/actions/workflows/validazione_storico.yml/dispatches"
                headers = {
                    "Authorization": f"token {TOKEN}",
                    "Accept": "application/vnd.github.v3+json",
                    "Content-Type": "application/json"
                }
                response = requests.post(url, headers=headers, json={"ref": "main"})
                if response.status_code == 204:
                    st.success("🔄 Fase 2 partita! Elaborazione post-match in corso.")
                else:
                    st.error(f"❌ Errore server Fase 2: {response.status_code}")

# Lettura dell'orario di aggiornamento file
if os.path.exists("Pronostici_App_Betting.xlsx"):
    mtime = os.path.getmtime("Pronostici_App_Betting.xlsx")
    data_ora = datetime.fromtimestamp(mtime, tz=FUSO_ORARIO).strftime('%d/%m/%Y %H:%M:%S')
    st.caption(f"⏱️ **Ultima Live Eseguita il:** {data_ora}")
else:
    st.caption("⏱️ **Ultima Live Eseguita il:** Nessun dato in memoria")

# Navigazione principale
tabs = st.tabs(["🎯 Palinsesto & Pronostici", "📊 Storico Validato"])

# --- TAB 1: PALINSESTO ---
with tabs[0]:
    if os.path.exists("Pronostici_App_Betting.xlsx"):
        try:
            df = pd.read_excel("Pronostici_App_Betting.xlsx")
            if df.empty:
                st.info("Nessun match presente in palinsesto.")
            else:
                for idx, row in df.iterrows():
                    st.markdown(f"""
                    <div class="card">
                        <div class="time-label">📅 {row.get('Data_Ora_Match', '-')} | 🏆 {row.get('Campionato', '-')}</div>
                        <div class="standing-label">📊 Punti in Classifica: Casa {row.get('Punti_Casa', 0)} PT | Ospite {row.get('Punti_Trasferta', 0)} PT</div>
                        <h4 style="margin: 6px 0; color: #1c1c1e;">{row.get('3. Match', 'Match')}</h4>
                        <div class="market-grid">
                            <div class="market-item"><b>1X2:</b> {row.get('1X2', '-')}</div>
                            <div class="market-item"><b>Esatto:</b> {row.get('Risultato_Esatto', '-')}</div>
                            <div class="market-item"><b>Doppia:</b> {row.get('Doppia_Chance', '-')}</div>
                            <div class="market-item"><b>Combo:</b> {row.get('DC+U/O2.5', '-')}</div>
                            <div class="market-item"><b>U/O 1.5:</b> {row.get('U/O_1.5', '-')}</div>
                            <div class="market-item"><b>U/O 2.5:</b> {row.get('U/O_2.5', '-')}</div>
                            <div class="market-item"><b>U/O 3.5:</b> {row.get('U/O_3.5', '-')}</div>
                            <div class="market-item"><b>G/NG:</b> {row.get('Goal_NoGoal', '-')}</div>
                            <div class="market-item"><b>xG Casa:</b> {row.get('Media_Goal_Casa', '-')}</div>
                            <div class="market-item"><b>xG Ospite:</b> {row.get('Media_Goal_Trasferta', '-')}</div>
                            <div class="market-item"><b>Corner 1X2:</b> {row.get('Corner_1X2', '-')}</div>
                            <div class="market-item"><b>Quota 1X2:</b> {row.get('Odds_1X2', '-')}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Errore lettura palinsesto: {e}")
    else:
        st.info("Nessun dato attivo.")

# --- TAB 2: STORICO VALIDATO CON COMPLETO ALLINEAMENTO COLORI ---
with tabs[1]:
    if os.path.exists("Storico_Validato_Betting.xlsx"):
        try:
            df_storico = pd.read_excel("Storico_Validato_Betting.xlsx")
            
            if df_storico.empty:
                st.info("L'archivio storico è vuoto.")
            else:
                match_validi = df_storico[df_storico['Risultato_Reale'] != 'NON ANCORA REALE/DA VALIDARE']
                tot_validi = len(match_validi)
                
                acc_1x2 = 0.0
                acc_uo = 0.0
                acc_esatto = 0.0
                
                if tot_validi > 0:
                    vinte_1x2 = len(match_validi[match_validi['Esito_1X2'] == 'VINCENTE'])
                    vinte_uo = len(match_validi[match_validi['Esito_U/O_2.5'] == 'VINCENTE'])
                    vinte_esatto = len(match_validi[match_validi['Esito_Risultato_Esatto'] == 'VINCENTE'])
                    
                    acc_1x2 = (vinte_1x2 / tot_validi) * 100
                    acc_uo = (vinte_uo / tot_validi) * 100
                    acc_esatto = (vinte_esatto / tot_validi) * 100

                st.markdown(f"📈 **Accuratezza Archivio ({tot_validi} Match Elaborati):**")
                c1, c2, c3 = st.columns(3)
                c1.metric(label="🎯 Esito 1X2", value=f"{acc_1x2:.1f}%")
                c2.metric(label="📊 Under/Over", value=f"{acc_uo:.1f}%")
                c3.metric(label="🔢 Ris. Esatto", value=f"{acc_esatto:.1f}%")
                st.markdown("---")
                
                for idx, row in df_storico.iterrows():
                    res_reale = row.get('Risultato_Reale', 'NON ANCORA REALE/DA VALIDARE')
                    
                    # Generazione icone dinamiche per tutti i mercati
                    icona_1x2 = "✅" if row.get('Esito_1X2') == "VINCENTE" else ("❌" if row.get('Esito_1X2') == "PERDENTE" else "⏳")
                    icona_uo = "✅" if row.get('Esito_U/O_2.5') == "VINCENTE" else ("❌" if row.get('Esito_U/O_2.5') == "PERDENTE" else "⏳")
                    icona_esatto = "✅" if row.get('Esito_Risultato_Esatto') == "VINCENTE" else ("❌" if row.get('Esito_Risultato_Esatto') == "PERDENTE" else "⏳")
                    
                    # ALLINEATA ANCHE LA COMBO ALLA LOGICA DEL DIZIONARIO REALE
                    esito_combo_raw = row.get('Esito DC+U/O2.5', '-')
                    icona_combo = "✅" if esito_combo_raw == "VINCENTE" else ("❌" if esito_combo_raw == "PERDENTE" else "⏳")
                    
                    st.markdown(f"""
                    <div class="card-storico">
                        <div class="time-label">📅 {row.get('Data_Ora_Match', '-')} | 🏆 {row.get('Campionato', '-')}</div>
                        <h4 style="margin: 4px 0; color: #1c1c1e;">{row.get('3. Match', 'Match')}</h4>
                        <div class="result-label">⚽ Finale Reale: <b>{res_reale}</b></div>
                        <div class="market-grid">
                            <div class="market-item"><b>Prono 1X2:</b> {row.get('1X2', '-')} <br> {icona_1x2} <span class="{"esito-vincente" if icona_1x2 == "✅" else "esito-perdente"}">{row.get('Esito_1X2', '-')}</span></div>
                            <div class="market-item"><b>Prono Esatto:</b> {row.get('Risultato_Esatto', '-')} <br> {icona_esatto} <span class="{"esito-vincente" if icona_esatto == "✅" else "esito-perdente"}">{row.get('Esito_Risultato_Esatto', '-')}</span></div>
                            <div class="market-item"><b>Prono U/O 2.5:</b> {row.get('U/O_2.5', '-')} <br> {icona_uo} <span class="{"esito-vincente" if icona_uo == "✅" else "esito-perdente"}">{row.get('Esito_U/O_2.5', '-')}</span></div>
                            <div class="market-item"><b>Prono Combo:</b> {row.get('DC+U/O2.5', '-')} <br> {icona_combo} <span class="{"esito-vincente" if icona_combo == "✅" else "esito-perdente"}">{esito_combo_raw}</span></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Errore lettura storico: {e}")
    else:
        st.info("L'archivio storico reale apparirà dopo la prima validazione.")
