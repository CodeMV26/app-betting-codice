import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime
import pytz
import re

# Forziamo il layout nativo centrato, ideale per la larghezza di uno smartphone
st.set_page_config(page_title="⚽ Betting Pro Mobile", page_icon="⚽", layout="centered")

# Iniezione di CSS protetto per bloccare la geometria su iPhone X (5.8") e iPhone 13 (6.1")
st.markdown("""
    <style>
    /* Reset dei margini per ottimizzare lo spazio su display mobile */
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; padding-left: 0.8rem !important; padding-right: 0.8rem !important; }
    
    /* Card dei match ottimizzate per lo scorrimento verticale puro */
    .match-card {
        background-color: #ffffff;
        padding: 12px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-bottom: 12px;
        border-left: 5px solid #007aff;
    }
    .card-storico { border-left-color: #34c759; }
    .card-database { border-left-color: #ff9500; }
    
    .meta-label { color: #8e8e93; font-size: 11px; font-weight: bold; text-transform: uppercase; }
    .team-text { font-size: 15px; font-weight: bold; color: #1c1c1e; margin: 4px 0; }
    .score-badge { background-color: #e5e5ea; color: #1c1c1e; font-size: 12px; font-weight: bold; padding: 3px 8px; border-radius: 5px; display: inline-block; margin: 4px 0; }
    
    /* Griglia a due colonne fisse senza scroll laterale: scansionabile perfettamente su iPhone */
    .market-box {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 6px;
        margin-top: 8px;
    }
    .market-cell {
        background: #f8f9fa;
        padding: 6px;
        border-radius: 6px;
        border: 1px solid #efeff4;
        font-size: 12px;
    }
    .market-cell b { color: #48484a; }
    
    /* Badge degli esiti */
    .win-text { color: #34c759; font-weight: bold; font-size: 11px; }
    .lose-text { color: #ff3b30; font-weight: bold; font-size: 11px; }
    .wait-text { color: #ff9500; font-weight: bold; font-size: 11px; }
    
    /* Separatori sezioni statistiche interni alla card */
    .sub-title { font-size: 10px; font-weight: bold; color: #007aff; text-transform: uppercase; grid-column: span 2; margin-top: 4px; border-bottom: 1px solid #e5e5ea; }
    </style>
""", unsafe_allow_html=True)

# File Excel definiti e blindati nella cronologia del progetto
DB_FILE = "Database_Storico_Completo.xlsx"
STORICO_FILE = "Storico_Validato_Betting.xlsx"
PALINSESTO_FILE = "Pronostici_App_Betting.xlsx"

@st.cache_data(ttl=2)
def carica_dati(path):
    if os.path.exists(path):
        try: return pd.read_excel(path)
        except: return pd.DataFrame()
    return pd.DataFrame()

df_palinsesto = carica_dati(PALINSESTO_FILE)
df_storico = carica_dati(STORICO_FILE)
df_database = carica_dati(DB_FILE)

st.title("⚽ Betting Pro Mobile")

# Pulsante di aggiornamento manuale dell'interfaccia grafica
if st.button("🔄 Ricarica Schermata", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# Navigazione a Tab Singola (ottimale in verticale per smartphone)
opzione_tab = st.selectbox("📂 Vai alla sezione:", [
    f"🎯 Palinsesto Attivo ({len(df_palinsesto)})", 
    f"📊 Storico Convalidato ({len(df_storico)})", 
    f"🗄️ Database Totale ({len(df_database)})"
])

# ----------------- TAB 1: PALINSESTO -----------------
if "🎯 Palinsesto" in opzione_tab:
    if not df_palinsesto.empty:
        for idx, row in df_palinsesto.iterrows():
            st.markdown(f"""
            <div class="match-card">
                <div class="meta-label">🏆 {row.get('Campionato', '-')} | {row.get('Data_Ora_Match', '-')}</div>
                <div class="team-text"> {row.get('3. Match', 'Match')}</div>
                <div class="market-box">
                    <div class="market-cell"><b>1X2:</b> {row.get('1X2', '-')}</div>
                    <div class="market-cell"><b>Esatto:</b> {row.get('Risultato_Esatto', '-')}</div>
                    <div class="market-cell"><b>Doppia:</b> {row.get('Doppia_Chance', '-')}</div>
                    <div class="market-cell"><b>Combo:</b> {row.get('DC+U/O2.5', '-')}</div>
                    <div class="market-cell"><b>U/O 1.5:</b> {row.get('U/O_1.5', '-')}</div>
                    <div class="market-cell"><b>U/O 2.5:</b> {row.get('U/O_2.5', '-')}</div>
                    <div class="market-cell"><b>U/O 3.5:</b> {row.get('U/O_3.5', '-')}</div>
                    <div class="market-cell"><b>G/NG:</b> {row.get('Goal_NoGoal', '-')}</div>
                    <div class="market-cell"><b>MG Casa:</b> {row.get('Pronostico_MG_Casa', '-')}</div>
                    <div class="market-cell"><b>MG Ospite:</b> {row.get('Pronostico_MG_Trasferta', '-')}</div>
                    <div class="market-cell"><b>Corner:</b> {row.get('Corner_1X2', '-')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nessun match presente in palinsesto.")

# ----------------- TAB 2: STORICO RECENTE -----------------
elif "📊 Storico" in opzione_tab:
    if not df_storico.empty:
        for idx, row in df_storico.iterrows():
            res_reale = str(row.get('Risultato_Reale', '-')).strip()
            
            def badge_esito(colonna):
                val = str(row.get(colonna, '-')).strip().upper()
                if "VINCENTE" in val: return "<div class='win-text'>✅ VINCENTE</div>"
                if "PERDENTE" in val: return "<div class='lose-text'>❌ PERDENTE</div>"
                return "<div class='wait-text'>⏳ In attesa</div>"

            st.markdown(f"""
            <div class="match-card card-storico">
                <div class="meta-label">🏆 {row.get('Campionato', '-')} | {row.get('Data_Ora_Match', '-')}</div>
                <div class="team-text">{row.get('3. Match', 'Match')}</div>
                <div class="score-badge">⚽ Finale: {res_reale}</div>
                <div class="market-box">
                    <div class="market-cell"><b>1X2:</b> {row.get('1X2', '-')} {badge_esito('Esito_1X2')}</div>
                    <div class="market-cell"><b>Esatto:</b> {row.get('Risultato_Esatto', '-')} {badge_esito('Esito_Risultato_Esatto')}</div>
                    <div class="market-cell"><b>Doppia:</b> {row.get('Doppia_Chance', '-')} {badge_esito('Esito_Doppia_Chance')}</div>
                    <div class="market-cell"><b>Combo:</b> {row.get('DC+U/O2.5', '-')} {badge_esito('Esito_DC+U/O2.5')}</div>
                    <div class="market-cell"><b>U/O 1.5:</b> {row.get('U/O_1.5', '-')} {badge_esito('Esito_U/O_1.5')}</div>
                    <div class="market-cell"><b>U/O 2.5:</b> {row.get('U/O_2.5', '-')} {badge_esito('Esito_U/O_2.5')}</div>
                    <div class="market-cell"><b>U/O 3.5:</b> {row.get('U/O_3.5', '-')} {badge_esito('Esito_U/O_3.5')}</div>
                    <div class="market-cell"><b>G/NG:</b> {row.get('Goal_NoGoal', '-')} {badge_esito('Esito_Goal_NoGoal')}</div>
                    <div class="market-cell"><b>MG Casa:</b> {row.get('Pronostico_MG_Casa', '-')} {badge_esito('Esito_Media_Goal_Casa')}</div>
                    <div class="market-cell"><b>MG Ospite:</b> {row.get('Pronostico_MG_Trasferta', '-')} {badge_esito('Esito_Media_Goal_Trasferta')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nessun match convalidato di recente nello storico.")

# ----------------- TAB 3: DATABASE TOTALE -----------------
elif "🗄️ Database Totale" in opzione_tab:
    if not df_database.empty:
        st.caption(f"Partite totali registrate nell'archivio: {len(df_database)}")
        for idx, row in df_database.iterrows():
            st.markdown(f"""
            <div class="match-card card-database">
                <div class="meta-label">🏆 {row.get('Campionato', '-')} | {row.get('Data_Ora_Match', '-')}</div>
                <div class="team-text">{row.get('3. Match', 'Match')}</div>
                <div class="score-badge">⚽ Risultato: {row.get('Risultato_Reale', '-')}</div>
                <div class="market-box">
                    <div class="sub-title">Statistiche Storiche di Input</div>
                    <div class="market-cell"><b>Pti Casa:</b> {row.get('Punti_Casa', '-')}</div>
                    <div class="market-cell"><b>Pti Ospite:</b> {row.get('Punti_Trasferta', '-')}</div>
                    <div class="market-cell"><b>Media GF Casa:</b> {row.get('Media_Goal_Casa_Orig', row.get('Media_Goal_Casa', '-'))}</div>
                    <div class="market-cell"><b>Media GF Ospite:</b> {row.get('Media_Goal_Trasferta_Orig', row.get('Media_Goal_Trasferta', '-'))}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Il database storico complessivo è vuoto.")
