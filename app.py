import streamlit as st
import pandas as pd
import os
from datetime import datetime
import zoneinfo
import requests

FUSO_ORARIO = zoneinfo.ZoneInfo("Europe/Rome")
st.set_page_config(page_title="Pannello Betting", page_icon="⚽", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f2f2f7; }
    .card, .card-storico {
        background-color: white; padding: 12px; border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 12px;
    }
    .card { border-left: 5px solid #007aff; }
    .card-storico { border-left: 5px solid #34c759; }
    .time-label { color: #8e8e93; font-size: 11px; font-weight: bold; }
    .standing-label { color: #ff9500; font-size: 11px; font-weight: bold; margin-top: 2px; }
    .result-label { color: #1c1c1e; font-size: 14px; font-weight: bold; margin: 4px 0; background: #e5e5ea; padding: 4px 8px; border-radius: 5px; display: inline-block; }
    .market-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; margin-top: 8px; font-size: 13px; }
    .market-item { background: #f8f9fa; padding: 4px 8px; border-radius: 4px; }
    .esito-vincente { color: #34c759; font-weight: bold; }
    .esito-perdente { color: #ff3b30; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO = st.secrets.get("GITHUB_REPO", "")

st.title("⚽ Controllo Betting Pro")
st.subheader("🛠️ Console Operativa Moduli")

col1, col2 = st.columns(2)
with col1:
    if st.button("🚀 Avvia Fase 1 (Pre-Match)"):
        if TOKEN and REPO:
            requests.post(f"https://api.github.com/repos/{REPO}/actions/workflows/pre-match.yml/dispatches", headers={"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json", "Content-Type": "application/json"}, json={"ref": "main"})
            st.success("🔄 Fase 1 partita!")
with col2:
    if st.button("📊 Avvia Fase 2 (Post-Match)"):
        if TOKEN and REPO:
            requests.post(f"https://api.github.com/repos/{REPO}/actions/workflows/validazione_storico.yml/dispatches", headers={"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json", "Content-Type": "application/json"}, json={"ref": "main"})
            st.success("🔄 Fase 2 partita!")

tabs = st.tabs(["🎯 Palinsesto & Pronostici", "📊 Storico Validato"])

with tabs[0]:
    if os.path.exists("Pronostici_App_Betting.xlsx"):
        df = pd.read_excel("Pronostici_App_Betting.xlsx")
        for idx, row in df.iterrows():
            st.markdown(f"""
            <div class="card">
                <div class="time-label">📅 {row.get('Data_Ora_Match', '-')} | 🏆 {row.get('Campionato', '-')}</div>
                <div class="standing-label">📊 Punti: Casa {row.get('Punti_Casa', 0)} | Ospite {row.get('Punti_Trasferta', 0)}</div>
                <h4 style="margin: 6px 0;">{row.get('3. Match', 'Match')}</h4>
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
                </div>
            </div>
            """, unsafe_allow_html=True)

with tabs[1]:
    if os.path.exists("Storico_Validato_Betting.xlsx"):
        df_storico = pd.read_excel("Storico_Validato_Betting.xlsx")
        if not df_storico.empty:
            match_validi = df_storico[df_storico['Risultato_Reale'] != 'NON ANCORA REALE/DA VALIDARE']
            tot_validi = len(match_validi)
            
            # Calcolo dinamico accuratezza complessiva dell'archivio
            acc_1x2 = (len(match_validi[match_validi['Esito_1X2'] == 'VINCENTE']) / tot_validi * 100) if tot_validi > 0 else 0
            acc_dc = (len(match_validi[match_validi['Esito_Doppia_Chance'] == 'VINCENTE']) / tot_validi * 100) if tot_validi > 0 else 0
            acc_gng = (len(match_validi[match_validi['Esito_Goal_NoGoal'] == 'VINCENTE']) / tot_validi * 100) if tot_validi > 0 else 0

            st.markdown(f"📈 **Accuratezza Global ({tot_validi} Match):**")
            c1, c2, c3 = st.columns(3)
            c1.metric(label="🎯 Esito 1X2", value=f"{acc_1x2:.1f}%")
            c2.metric(label="🛡️ Doppia Chance", value=f"{acc_dc:.1f}%")
            c3.metric(label="⚽ Goal/NoGoal", value=f"{acc_gng:.1f}%")
            st.markdown("---")
            
            for idx, row in df_storico.iterrows():
                res_reale = row.get('Risultato_Reale', 'NON ANCORA REALE/DA VALIDARE')
                
                def get_badge(col_name):
                    val = row.get(col_name, '-')
                    if val == "VINCENTE": return "✅ <span class='esito-vincente'>VINCENTE</span>"
                    if val == "PERDENTE": return "❌ <span class='esito-perdente'>PERDENTE</span>"
                    return "⏳ <span>In attesa</span>"

                st.markdown(f"""
                <div class="card-storico">
                    <div class="time-label">📅 {row.get('Data_Ora_Match', '-')} | 🏆 {row.get('Campionato', '-')}</div>
                    <h4 style="margin: 4px 0;">{row.get('3. Match', 'Match')}</h4>
                    <div class="result-label">⚽ Finale Reale: <b>{res_reale}</b></div>
                    <div class="market-grid">
                        <div class="market-item"><b>1X2:</b> {row.get('1X2', '-')} <br> {get_badge('Esito_1X2')}</div>
                        <div class="market-item"><b>Esatto:</b> {row.get('Risultato_Esatto', '-')} <br> {get_badge('Esito_Risultato_Esatto')}</div>
                        <div class="market-item"><b>Doppia:</b> {row.get('Doppia_Chance', '-')} <br> {get_badge('Esito_Doppia_Chance')}</div>
                        <div class="market-item"><b>Combo:</b> {row.get('DC+U/O2.5', '-')} <br> {get_badge('Esito DC+U/O2.5')}</div>
                        <div class="market-item"><b>U/O 1.5:</b> {row.get('U/O_1.5', '-')} <br> {get_badge('Esito_U/O_1.5')}</div>
                        <div class="market-item"><b>U/O 2.5:</b> {row.get('U/O_2.5', '-')} <br> {get_badge('Esito_U/O_2.5')}</div>
                        <div class="market-item"><b>U/O 3.5:</b> {row.get('U/O_3.5', '-')} <br> {get_badge('Esito_U/O_3.5')}</div>
                        <div class="market-item"><b>G/NG:</b> {row.get('Goal_NoGoal', '-')} <br> {get_badge('Esito_Goal_NoGoal')}</div>
                        <div class="market-item"><b>xG Casa:</b> {row.get('Media_Goal_Casa', '-')} <br> 🔢 {row.get('Esito_Media_Goal_Casa', '-')}</div>
                        <div class="market-item"><b>xG Ospite:</b> {row.get('Media_Goal_Trasferta', '-')} <br> 🔢 {row.get('Esito_Media_Goal_Trasferta', '-')}</div>
                        <div class="market-item"><b>Corner 1X2:</b> {row.get('Corner_1X2', '-')} <br> 📊 {row.get('Esito_Corner_1X2', '-')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
