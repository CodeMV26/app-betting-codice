import streamlit as st
import pandas as pd
import os
import requests

st.set_page_config(page_title="Pannello Betting", page_icon="⚽", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f2f2f7; }
    .card, .card-storico, .card-accuratezza { 
        background-color: white; padding: 12px; border-radius: 10px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 12px; 
    }
    .card { border-left: 5px solid #007aff; }
    .card-storico { border-left: 5px solid #34c759; }
    .card-accuratezza { border-left: 5px solid #ff9500; }
    .time-label { color: #8e8e93; font-size: 11px; font-weight: bold; }
    .result-label { color: #1c1c1e; font-size: 14px; font-weight: bold; margin: 4px 0; background: #e5e5ea; padding: 4px 8px; border-radius: 5px; display: inline-block; }
    .market-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; margin-top: 8px; font-size: 13px; }
    .market-item { background: #f8f9fa; padding: 4px 8px; border-radius: 4px; }
    .esito-vincente { color: #34c759; font-weight: bold; }
    .esito-perdente { color: #ff3b30; font-weight: bold; }
    
    /* Stile Tabella HTML Custom per iPhone X */
    .custom-table { width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 13px; }
    .custom-table th { text-align: left; padding: 6px 8px; background-color: #f2f2f7; color: #8e8e93; font-weight: bold; font-size: 11px; text-transform: uppercase; }
    .custom-table td { padding: 8px; border-bottom: 1px solid #f2f2f7; color: #1c1c1e; }
    .custom-table tr:last-child td { border-bottom: none; }
    .badge-acc { background: #ff9500; color: white; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 12px; }
    .badge-nd { background: #8e8e93; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; }
    </style>
""", unsafe_allow_html=True)

TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO = st.secrets.get("GITHUB_REPO", "")

st.title("⚽ Controllo Betting Pro")
col1, col2 = st.columns(2)
with col1:
    if st.button("🚀 Avvia Fase 1 (Pre-Match)"):
        if TOKEN and REPO: requests.post(f"https://api.github.com/repos/{REPO}/actions/workflows/pre-match.yml/dispatches", headers={"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}, json={"ref": "main"})
with col2:
    if st.button("📊 Avvia Fase 2 (Post-Match)"):
        if TOKEN and REPO: requests.post(f"https://api.github.com/repos/{REPO}/actions/workflows/validazione_storico.yml/dispatches", headers={"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}, json={"ref": "main"})

tabs = st.tabs(["🎯 Palinsesto & Pronostici", "📊 Storico Validato"])

with tabs[0]:
    if os.path.exists("Pronostici_App_Betting.xlsx"):
        df = pd.read_excel("Pronostici_App_Betting.xlsx")
        for idx, row in df.iterrows():
            st.markdown(f"""
            <div class="card">
                <div class="time-label">🏆 {row.get('Campionato', '-')} | {row.get('Data_Ora_Match', '-')}</div>
                <h4 style="margin: 4px 0;">{row.get('3. Match', 'Match')}</h4>
                <div class="market-grid">
                    <div class="market-item"><b>1X2:</b> {row.get('1X2', '-')}</div>
                    <div class="market-item"><b>Esatto:</b> {row.get('Risultato_Esatto', '-')}</div>
                    <div class="market-item"><b>Doppia:</b> {row.get('Doppia_Chance', '-')}</div>
                    <div class="market-item"><b>Combo:</b> {row.get('DC+U/O2.5', '-')}</div>
                    <div class="market-item"><b>U/O 1.5:</b> {row.get('U/O_1.5', '-')}</div>
                    <div class="market-item"><b>U/O 2.5:</b> {row.get('U/O_2.5', '-')}</div>
                    <div class="market-item"><b>U/O 3.5:</b> {row.get('U/O_3.5', '-')}</div>
                    <div class="market-item"><b>G/NG:</b> {row.get('Goal_NoGoal', '-')}</div>
                    <div class="market-item"><b>MG Casa:</b> {row.get('Media_Goal_Casa', '-')}</div>
                    <div class="market-item"><b>MG Ospite:</b> {row.get('Media_Goal_Trasferta', '-')}</div>
                    <div class="market-item"><b>Corner 1X2:</b> {row.get('Corner_1X2', '-')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

with tabs[1]:
    if os.path.exists("Storico_Validato_Betting.xlsx"):
        df_storico = pd.read_excel("Storico_Validato_Betting.xlsx")
        if not df_storico.empty:
            match_validi = df_storico[df_storico['Risultato_Reale'] != 'NON ANCORA REALE/DA VALIDARE']
            tot = len(match_validi)
            
            # Funzione per estrarre la percentuale o la label ND
            def get_acc_val(col, is_corner=False):
                if is_corner: return "<span class='badge-nd'>N.D. (Mancante)</span>"
                if tot == 0 or col not in match_validi.columns: return "<span class='badge-acc'>0.0%</span>"
                vincenti = len(match_validi[match_validi[col] == 'VINCENTE'])
                return f"<span class='badge-acc'>{(vincenti / tot * 100):.1f}%</span>"

            # Renderizzazione Tabella Custom in HTML perfettamente fusa con il design dell'App
            st.markdown(f"""
            <div class="card-accuratezza">
                <div class="time-label">📈 METRICHE GLOBALI</div>
                <h4 style="margin: 4px 0 8px 0;">Resoconto Accuratezza ({tot} Match)</h4>
                <table class="custom-table">
                    <tr><th>Mercato</th><th>Precisione</th></tr>
                    <tr><td>🎯 Esito 1X2</td><td>{get_acc_val('Esito_1X2')}</td></tr>
                    <tr><td>🔢 Risultato Esatto</td><td>{get_acc_val('Esito_Risultato_Esatto')}</td></tr>
                    <tr><td>🛡️ Doppia Chance</td><td>{get_acc_val('Esito_Doppia_Chance')}</td></tr>
                    <tr><td>💥 Combo DC+U/O 2.5</td><td>{get_acc_val('Esito_DC+U/O2.5')}</td></tr>
                    <tr><td>⚽ Under/Over 1.5</td><td>{get_acc_val('Esito_U/O_1.5')}</td></tr>
                    <tr><td>⚽ Under/Over 2.5</td><td>{get_acc_val('Esito_U/O_2.5')}</td></tr>
                    <tr><td>⚽ Under/Over 3.5</td><td>{get_acc_val('Esito_U/O_3.5')}</td></tr>
                    <tr><td>🔥 Goal/NoGoal</td><td>{get_acc_val('Esito_Goal_NoGoal')}</td></tr>
                    <tr><td>🏠 MG Casa (MultiGoal)</td><td>{get_acc_val('Esito_Media_Goal_Casa')}</td></tr>
                    <tr><td>🚌 MG Ospite (MultiGoal)</td><td>{get_acc_val('Esito_Media_Goal_Trasferta')}</td></tr>
                    <tr><td>📐 Corner 1X2</td><td>{get_acc_val('Esito_Corner_1X2', True)}</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
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
                    <div class="time-label">🏆 {row.get('Campionato', '-')} | {row.get('Data_Ora_Match', '-')}</div>
                    <h4 style="margin: 4px 0;">{row.get('3. Match', 'Match')}</h4>
                    <div class="result-label">⚽ Finale: {res_reale}</div>
                    <div class="market-grid">
                        <div class="market-item"><b>1X2:</b> {row.get('1X2', '-')} <br> {get_badge('Esito_1X2')}</div>
                        <div class="market-item"><b>Esatto:</b> {row.get('Risultato_Esatto', '-')} <br> {get_badge('Esito_Risultato_Esatto')}</div>
                        <div class="market-item"><b>Doppia:</b> {row.get('Doppia_Chance', '-')} <br> {get_badge('Esito_Doppia_Chance')}</div>
                        <div class="market-item"><b>Combo:</b> {row.get('DC+U/O2.5', '-')} <br> {get_badge('Esito_DC+U/O2.5')}</div>
                        <div class="market-item"><b>U/O 1.5:</b> {row.get('U/O_1.5', '-')} <br> {get_badge('Esito_U/O_1.5')}</div>
                        <div class="market-item"><b>U/O 2.5:</b> {row.get('U/O_2.5', '-')} <br> {get_badge('Esito_U/O_2.5')}</div>
                        <div class="market-item"><b>U/O 3.5:</b> {row.get('U/O_3.5', '-')} <br> {get_badge('Esito_U/O_3.5')}</div>
                        <div class="market-item"><b>G/NG:</b> {row.get('Goal_NoGoal', '-')} <br> {get_badge('Esito_Goal_NoGoal')}</div>
                        <div class="market-item"><b>MG Casa:</b> {row.get('Media_Goal_Casa', '-')} <br> {get_badge('Esito_Media_Goal_Casa')}</div>
                        <div class="market-item"><b>MG Ospite:</b> {row.get('Media_Goal_Trasferta', '-')} <br> {get_badge('Esito_Media_Goal_Trasferta')}</div>
                        <div class="market-item"><b>Corner 1X2:</b> {row.get('Corner_1X2', '-')} <br> {get_badge('Esito_Corner_1X2')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
