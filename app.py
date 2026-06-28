import streamlit as st
import pandas as pd
import os
import datetime
from zoneinfo import ZoneInfo

# PROGRESSIVO CHAT: #104 | Data: 28 Giugno 2026 | Ora: 17:29:15
# Versione Progetto: 6.04 (Ripristino F-String Tab Storico & Integrità Totale)

st.set_page_config(page_title="⚽ Betting Pro Mobile", page_icon="⚽", layout="centered")

FUSO_ROMA = ZoneInfo("Europe/Rome")

if "log_fase1" not in st.session_state: st.session_state.log_fase1 = "Mai eseguito"
if "log_fase2" not in st.session_state: st.session_state.log_fase2 = "Mai eseguito"
if "log_fase3" not in st.session_state: st.session_state.log_fase3 = "Mai eseguito"
if "tab_selezionata" not in st.session_state: st.session_state.tab_selezionata = "PALINSESTO"

DB_FILE = "Database_Storico_Completo.xlsx"
STORICO_FILE = "Storico_Validato_Betting.xlsx"
PALINSESTO_FILE = "Pronostici_App_Betting.xlsx"

@st.cache_data(ttl=2)
def carica_dati(path):
    if os.path.exists(path):
        try:
            df = pd.read_excel(path)
            if not df.empty and '3. Match' in df.columns:
                df = df[df['3. Match'].astype(str).str.upper().str.strip() != 'NONE VS NONE']
                df = df.dropna(subset=['3. Match'])
            return df.reset_index(drop=True)
        except: return pd.DataFrame()
    return pd.DataFrame()

df_palinsesto = carica_dati(PALINSESTO_FILE)
df_storico = carica_dati(STORICO_FILE)
df_database = carica_dati(DB_FILE)

st.markdown("""
    <style>
    .block-container { padding-top: 2rem !important; padding-bottom: 1rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
    .brand-box { text-align: center; margin-bottom: 12px; padding: 2px; }
    .main-title { font-size: 22px; font-weight: 800; color: #1c1c1e; margin: 0; }
    .version-label { font-size: 10px; font-weight: 700; color: #007aff; margin-top: 1px; text-transform: uppercase; letter-spacing: 0.5px; }
    div.stButton > button { border-radius: 8px !important; font-weight: 700 !important; font-size: 11px !important; padding: 6px 10px !important; height: auto !important; width: 100% !important; border: none !important; box-shadow: 0 2px 5px rgba(0,0,0,0.03) !important; margin-bottom: -4px !important; }
    div.stButton > button[id*="fase_1"] { background-color: #2cd158 !important; color: white !important; }
    div.stButton > button[id*="fase_2"] { background-color: #6a5acd !important; color: white !important; }
    div.stButton > button[id*="fase_3"] { background-color: #ffd700 !important; color: #1c1c1e !important; }
    .tab-click-col div.stButton > button { font-size: 10px !important; padding: 6px 2px !important; border-radius: 6px !important; border: 1px solid #d1d1d6 !important; text-transform: uppercase; }
    .match-card { background-color: #ffffff !important; padding: 12px; border-radius: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); margin-bottom: 10px; border: 1px solid #e5e5ea !important; }
    .meta-label { color: #007aff; font-size: 9px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 2px; }
    .team-text { font-size: 15px; font-weight: 700; color: #1c1c1e; margin: 2px 0 6px 0; letter-spacing: -0.3px; }
    .score-badge { background-color: rgba(240,240,245,1); color: #1c1c1e; font-size: 11px; font-weight: 700; padding: 4px 8px; border-radius: 6px; display: inline-block; margin-bottom: 6px; border: 1px solid #e5e5ea; }
    .block-header { font-size: 10px; font-weight: 800; color: #007aff; text-transform: uppercase; margin: 2px 0 8px 0; letter-spacing: 0.4px; display: flex; align-items: center; }
    .block-header.stats { color: #ff9500; }
    .market-box { display: grid; grid-template-columns: repeat(2, 1fr); gap: 5px; }
    .market-cell { background: rgba(248, 249, 250, 1); padding: 6px; border-radius: 6px; font-size: 11px; display: flex; flex-direction: column; justify-content: center; border: 1px solid #e5e5ea; }
    .market-cell b { color: #8e8e93; font-size: 9px; text-transform: uppercase; margin-bottom: 1px; }
    .market-val-row { display: flex; justify-content: space-between; align-items: center; font-weight: 600; color: #1c1c1e; }
    .win-badge { color: #34c759; font-weight: bold; font-size: 9px; background: #e8f9ee; padding: 2px 5px; border-radius: 4px; text-transform: uppercase; }
    .lose-badge { color: #ff3b30; font-weight: bold; font-size: 9px; background: #ffebeb; padding: 2px 5px; border-radius: 4px; text-transform: uppercase; }
    .wait-badge { color: #ff9500; font-weight: bold; font-size: 9px; background: #fff5e6; padding: 2px 5px; border-radius: 4px; text-transform: uppercase; }
    .match-separator { margin-bottom: 18px; border-bottom: 2px dotted #e5e5ea; height: 1px; width: 100%; }
    .accuracy-container { background: #ffffff; padding: 12px; border-radius: 14px; margin-top: 12px; margin-bottom: 14px; box-shadow: 0 3px 10px rgba(0,0,0,0.03); border: 1px solid #d1d1d6; }
    .accuracy-title { font-size: 11px; font-weight: 800; color: #1c1c1e; text-transform: uppercase; margin-bottom: 8px; text-align: center; letter-spacing: 0.5px; }
    .accuracy-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; }
    .accuracy-item { background: #f8f9fa; padding: 6px 8px; border-radius: 8px; font-size: 11px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #e5e5ea; }
    .accuracy-item span { color: #48484a; font-weight: 600; }
    .accuracy-val { color: #007aff; font-weight: 800; font-size: 11px; }
    </style>
""", unsafe_allow_html=True)

def calcola_accuratezza_globale():
    frames = []
    if not df_storico.empty: frames.append(df_storico)
    if not df_database.empty: frames.append(df_database)
    if not frames: return {}
    df_totale = pd.concat(frames, ignore_index=True)
    mappa_esiti = {
        "1X2": "Esito_1X2", "Ris. Esatto": "Esito_Risultato_Esatto", "Doppia Chance": "Esito_Doppia_Chance",
        "U/O 1.5": "Esito_U/O_1.5", "U/O 2.5": "Esito_U/O_2.5", "U/O 3.5": "Esito_U/O_3.5", 
        "Goal/NoGoal": "Esito_Goal_NoGoal", "Combo DC + U/O": "Esito_DC+U/O2.5",
        "MG Casa": "Esito_Media_Goal_Casa", "MG Ospite": "Esito_Media_Goal_Trasferta",
        "MG Totale": "Esito_Media_Goal_Totale", "Corner 1X2": "Esito_Corner_1X2"
    }
    accuratezza = {}
    for nome_m, col in mappa_esiti.items():
        if col in df_totale.columns:
            validi = df_totale[df_totale[col].isin(['VINCENTE', 'PERDENTE'])]
            if len(validi) > 0:
                vincenti = len(validi[validi[col] == 'VINCENTE'])
                accuratezza[nome_m] = f"{(vincenti / len(validi)) * 100:.1f}% ({vincenti}/{len(validi)})"
            else: accuratezza[nome_m] = "0.0% (0)"
        else: accuratezza[nome_m] = "N.D."
    return accuratezza

def get_badge(esito):
    val = str(esito).upper().strip()
    if "VINCENTE" in val: return '<span class="win-badge">VINCENTE</span>'
    if "PERDENTE" in val: return '<span class="lose-badge">PERDENTE</span>'
    return '<span class="wait-badge">IN ATTESA</span>'

def safe_get(row, keys_list):
    for k in keys_list:
        if k in row: return row[k]
        for prefix in ["1. ", "2. ", "3. ", "4. ", "5. ", "6. ", "7. ", "8. "]:
            if f"{prefix}{k}" in row: return row[f"{prefix}{k}"]
    return "-"

st.markdown("""
<div class="brand-box">
    <div class="main-title">⚽ Betting Pro Mobile</div>
    <div class="version-label">Versione Progetto: 6.04</div>
</div>
""", unsafe_allow_html=True)

# --- PULSANTI AZIONE INTERFACCIA ---
testo_p1 = f"🚀 F
