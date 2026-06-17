import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime

st.set_page_config(page_title="Pannello Betting", page_icon="⚽", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f2f2f7; }
    .card, .card-storico, .card-database { background-color: white; padding: 14px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); margin-bottom: 14px; }
    .card { border-left: 5px solid #007aff; }
    .card-storico { border-left: 5px solid #34c759; }
    .card-database { border-left: 5px solid #ff9500; }
    .time-label { color: #8e8e93; font-size: 11px; font-weight: bold; }
    .update-label { color: #8e8e93; font-size: 13px; margin-bottom: 15px; font-style: italic; }
    .result-label { color: #1c1c1e; font-size: 14px; font-weight: bold; margin: 6px 0; background: #e5e5ea; padding: 4px 8px; border-radius: 6px; display: inline-block; }
    .market-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-top: 10px; font-size: 13px; }
    .market-item { background: #f8f9fa; padding: 6px 10px; border-radius: 6px; border: 1px solid #efeff4; }
    .esito-vincente { color: #34c759; font-weight: bold; }
    .esito-perdente { color: #ff3b30; font-weight: bold; }
    
    /* Design Moderno Griglia Badge per Accuratezza */
    .accuracy-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 12px; }
    .accuracy-card { background: #ffffff; border: 1px solid #e5e5ea; padding: 10px 12px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); display: flex; justify-content: space-between; align-items: center; }
    .accuracy-market { font-weight: 600; color: #1c1c1e; font-size: 13px; }
    .accuracy-value { background: #007aff; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; }
    .accuracy-value-nd { background: #8e8e93; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO = st.secrets.get("GITHUB_REPO", "")

st.title("⚽ Controllo Betting Pro")

# Ripristino Data e Ora Ultimo Aggiornamento file
if os.path.exists("Pronostici_App_Betting.xlsx"):
    mtime = os.path.getmtime("Pronostici_App_Betting.xlsx")
    data_ora = datetime.fromtimestamp(mtime).strftime('%d/%m/%Y %H:%M:%S')
    st.markdown(f"<div class='update-label'>🔄 Ultimo aggiornamento dati: {data_ora}</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='update-label'>🔄 Ultimo aggiornamento dati: Non disponibile</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("🚀 Avvia Fase 1 (Pre-Match)"):
        if TOKEN and REPO: requests.post(f"https://api.github.com/repos/{REPO}/actions/workflows/pre-match.yml/dispatches", headers={"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}, json={"ref": "main"})
with col2:
    if st.button("📊 Avvia Fase 2 (Post-Match)"):
        if TOKEN and REPO: requests.post(f"https://api.github.com/repos/{REPO}/actions/workflows/validazione_storico.yml/dispatches", headers={"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}, json={"ref": "main"})

# CREAZIONE DEI TRE TABS (Aggiunto il Tab 3 per consultare l'archivio globale Modulo 04)
tabs = st.tabs(["🎯 Palinsesto & Pronostici", "📊 Storico Validato", "🗄️ Archivio Globale Completo"])

# Funzione di pulizia/fallback per correggere i vecchi dati "xG" residui nel file Excel
def pulisci_multigoal(valore_excel):
    val_str = str(valore_excel).strip()
    if "xG" in val_str:
        try:
            num = float(val_str.replace("xG", "").strip())
            return "1-2 MG" if num <= 2.0 else "3+ MG"
        except:
            return "1-2 MG"
    return val_str

# TAB 1: PALINSESTO E PRONOSTICI
with tabs[0]:
    if os.path.exists("Pronostici_App_Betting.xlsx"):
        df = pd.read_excel("Pronostici_App_Betting.xlsx")
        for idx, row in df.iterrows():
            mg_casa_pulito = pulisci_multigoal(row.get('Media_Goal_Casa', '-'))
            mg_ospite_pulito = pulisci_multigoal(row.get('Media_Goal_Trasferta', '-'))
            
            st.markdown(f"""
            <div class="card">
                <div class="time-label">🏆 {row.get('Campionato', '-')} | {row.get('Data_Ora_Match', '-')}</div>
                <h4 style="margin: 4px 0;">{row.get('3. Match', 'Match')}</h4>
                <div class="market-grid">
                    <div class="market-item"><b>1X2:</b> {row.get('1X2', '-')}</div>
                    <div class="market-item"><b>Esatto:</b> {row.get('Risultato_Esatto', '-')}</div>
                    <div class="market-item"><b>Doppia:</b> {row.get('Doppia_Chance', '-')}</div>
                    <div class="market-item"><b>Combo DC+U/O2.5:</b> {row.get('DC+U/O2.5', '-')}</div>
                    <div class="market-item"><b>U/O 1.5:</b> {row.get('U/O_1.5', '-')}</div>
                    <div class="market-item"><b>U/O 2.5:</b> {row.get('U/O_2.5', '-')}</div>
                    <div class="market-item"><b>U/O 3.5:</b> {row.get('U/O_3.5', '-')}</div>
                    <div class="market-item"><b>G/NG:</b> {row.get('Goal_NoGoal', '-')}</div>
                    <div class="market-item"><b>MG Casa:</b> {mg_casa_pulito}</div>
                    <div class="market-item"><b>MG Ospite:</b> {mg_ospite_pulito}</div>
                    <div class="market-item"><b>Corner 1X2:</b> {row.get('Corner_1X2', '-')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# TAB 2: STORICO VALIDATO
with tabs[1]:
    if os.path.exists("Storico_Validato_Betting.xlsx"):
        df_storico = pd.read_excel("Storico_Validato_Betting.xlsx")
        if not df_storico.empty:
            match_validi = df_storico[df_storico['Risultato_Reale'] != 'NON ANCORA REALE/DA VALIDARE']
            tot = len(match_validi)
            
            def calc_acc(col, is_corner=False):
                if is_corner: return "<span class='accuracy-value-nd'>N.D.</span>"
                val = f"{(len(match_validi[match_validi[col] == 'VINCENTE']) / tot * 100):.1f}%" if tot > 0 and col in match_validi.columns else "0.0%"
                return f"<span class='accuracy-value'>{val}</span>"

            st.write(f"📊 **Resoconto Accuratezza globale su {tot} Match Storici:**")
            
            st.markdown(f"""
            <div class="accuracy-grid">
                <div class="accuracy-card"><span class="accuracy-market">1X2</span> {calc_acc('Esito_1X2')}</div>
                <div class="accuracy-card"><span class="accuracy-market">Risultato Esatto</span> {calc_acc('Esito_Risultato_Esatto')}</div>
                <div class="accuracy-card"><span class="accuracy-market">Doppia Chance</span> {calc_acc('Esito_Doppia_Chance')}</div>
                <div class="accuracy-card"><span class="accuracy-market">Combo DC+U/O2.5</span> {calc_acc('Esito_DC+U/O2.5')}</div>
                <div class="accuracy-card"><span class="accuracy-market">Under/Over 1.5</span> {calc_acc('Esito_U/O_1.5')}</div>
                <div class="accuracy-card"><span class="accuracy-market">Under/Over 2.5</span> {calc_acc('Esito_U/O_2.5')}</div>
                <div class="accuracy-card"><span class="accuracy-market">Under/Over 3.5</span> {calc_acc('Esito_U/O_3.5')}</div>
                <div class="accuracy-card"><span class="accuracy-market">Goal/NoGoal</span> {calc_acc('Esito_Goal_NoGoal')}</div>
                <div class="accuracy-card"><span class="accuracy-market">MG Casa</span> {calc_acc('Esito_Media_Goal_Casa')}</div>
                <div class="accuracy-card"><span class="accuracy-market">MG Ospite</span> {calc_acc('Esito_Media_Goal_Trasferta')}</div>
                <div class="accuracy-card"><span class="accuracy-market">Corner 1X2</span> {calc_acc('Esito_Corner_1X2', True)}</div>
            </div>
            """, unsafe_allow_html=True)
                
            st.markdown("<br><hr>", unsafe_allow_html=True)
            
            for idx, row in df_storico.iterrows():
                res_reale = row.get('Risultato_Reale', 'NON ANCORA REALE/DA VALIDARE')
                mg_casa_pulito = pulisci_multigoal(row.get('Media_Goal_Casa', '-'))
                mg_ospite_pulito = pulisci_multigoal(row.get('Media_Goal_Trasferta', '-'))
                
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
                        <div class="market-item"><b>Combo DC+U/O2.5:</b> {row.get('DC+U/O2.5', '-')} <br> {get_badge('Esito_DC+U/O2.5')}</div>
                        <div class="market-item"><b>U/O 1.5:</b> {row.get('U/O_1.5', '-')} <br> {get_badge('Esito_U/O_1.5')}</div>
                        <div class="market-item"><b>U/O 2.5:</b> {row.get('U/O_2.5', '-')} <br> {get_badge('Esito_U/O_2.5')}</div>
                        <div class="market-item"><b>U/O 3.5:</b> {row.get('U/O_3.5', '-')} <br> {get_badge('Esito_U/O_3.5')}</div>
                        <div class="market-item"><b>G/NG:</b> {row.get('Goal_NoGoal', '-')} <br> {get_badge('Esito_Goal_NoGoal')}</div>
                        <div class="market-item"><b>MG Casa:</b> {mg_casa_pulito} <br> {get_badge('Esito_Media_Goal_Casa')}</div>
                        <div class="market-item"><b>MG Ospite:</b> {mg_ospite_pulito} <br> {get_badge('Esito_Media_Goal_Trasferta')}</div>
                        <div class="market-item"><b>Corner 1X2:</b> {row.get('Corner_1X2', '-')} <br> {get_badge('Esito_Corner_1X2')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# TAB 3: NUOVO ARCHIVIO GLOBALE COMPLETO (Database_Storico_Completo.xlsx)
with tabs[2]:
    st.subheader("🗄️ Database Storico Incrementale (Modulo 04)")
    
    DATABASE_STORICO_GLOBALE = "Database_Storico_Completo.xlsx"
    
    if os.path.exists(DATABASE_STORICO_GLOBALE):
        try:
            df_global_storico = pd.read_excel(DATABASE_STORICO_GLOBALE)
            
            if not df_global_storico.empty:
                st.success(f"📈 Connessione riuscita! Il database contiene **{len(df_global_storico)}** partite uniche registrate.")
                
                # Selettore di ricerca rapida per Campionato
                lista_camp = ["TUTTI"] + list(df_global_storico['Campionato'].unique())
                scelta_filtro_camp = st.selectbox("Filtra per competizione:", lista_camp, key="filtro_global_tab3")
                
                df_mostra_global = df_global_storico if scelta_filtro_camp == "TUTTI" else df_global_storico[df_global_storico['Campionato'] == scelta_filtro_camp]
                
                # Colonne essenziali ordinate e pulite per lo schermo dell'iPhone X
                colonne_target = [
                    'Data_Ora_Match', 'Campionato', '3. Match', 
                    'Risultato_Reale', '1X2', 'Esito_1X2', 
                    'Media_Goal_Casa', 'Esito_Media_Goal_Casa',
                    'Media_Goal_Trasferta', 'Esito_Media_Goal_Trasferta'
                ]
                
                colonne_disponibili_global = [c for c in colonne_target if c in df_mostra_global.columns]
                
                # Rendering tabella interattiva nativa di Streamlit ottimizzata
                st.dataframe(df_mostra_global[colonne_disponibili_global], use_container_width=True)
                
            else:
                st.warning("📋 Il file `Database_Storico_Completo.xlsx` è presente, ma non contiene ancora righe stabili.")
        except Exception as e:
            st.error(f"⚠️ Errore di lettura del Database Storico: {e}")
    else:
        st.info("ℹ️ Il file `Database_Storico_Completo.xlsx` non è ancora stato creato nel repository. Verrà generato automaticamente dalla Fase 2 non appena il workflow su GitHub Actions andrà a buon fine (Verde).")
