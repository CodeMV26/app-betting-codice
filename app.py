import streamlit as st
import pandas as pd
import os
import datetime
from zoneinfo import ZoneInfo

# Configurazione geometrica blindata per iPhone X (5.8") e iPhone 13 (6.1")
st.set_page_config(page_title="⚽ Betting Pro Mobile", page_icon="⚽", layout="centered")

FUSO_ROMA = ZoneInfo("Europe/Rome")

# Inizializzazione dello stato per i log temporali e la tab attiva
if "log_fase1" not in st.session_state:
    st.session_state.log_fase1 = "Mai eseguito"
if "log_fase2" not in st.session_state:
    st.session_state.log_fase2 = "Mai eseguito"
if "log_fase3" not in st.session_state:
    st.session_state.log_fase3 = "Mai eseguito"
if "tab_selezionata" not in st.session_state:
    st.session_state.tab_selezionata = "PALINSESTO"

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

# --- RESTYLING GRAFICO ULTRA-OTTIMIZZATO ---
st.markdown("""
    <style>
    .block-container { 
        padding-top: 2rem !important; 
        padding-bottom: 1rem !important; 
        padding-left: 0.5rem !important; 
        padding-right: 0.5rem !important; 
    }
    .brand-box { text-align: center; margin-bottom: 12px; padding: 2px; }
    .main-title { font-size: 22px; font-weight: 800; color: #1c1c1e; margin: 0; }
    .version-label { font-size: 10px; font-weight: 700; color: #007aff; margin-top: 1px; text-transform: uppercase; letter-spacing: 0.5px; }
    div.stButton > button {
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 11px !important;
        padding: 6px 10px !important;
        height: auto !important;
        width: 100% !important;
        border: none !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03) !important;
        margin-bottom: -4px !important;
    }
    div.stButton > button[id*="fase_1"] { background-color: #2cd158 !important; color: white !important; }
    div.stButton > button[id*="fase_2"] { background-color: #6a5acd !important; color: white !important; }
    div.stButton > button[id*="fase_3"] { background-color: #ffd700 !important; color: #1c1c1e !important; }
    .tab-click-col div.stButton > button {
        font-size: 10px !important;
        padding: 6px 2px !important;
        border-radius: 6px !important;
        border: 1px solid #d1d1d6 !important;
        text-transform: uppercase;
    }
    .match-card { 
        background-color: #ffffff !important; 
        padding: 12px; 
        border-radius: 14px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.04); 
        margin-bottom: 10px; 
        border: 1px solid #e5e5ea !important; 
    }
    .meta-label { color: #007aff; font-size: 9px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 2px; }
    .team-text { font-size: 15px; font-weight: 700; color: #1c1c1e; margin: 2px 0 6px 0; letter-spacing: -0.3px; }
    .score-badge { background-color: rgba(240,240,245,1); color: #1c1c1e; font-size: 11px; font-weight: 700; padding: 4px 8px; border-radius: 6px; display: inline-block; margin-bottom: 6px; border: 1px solid #e5e5ea; }
    .block-header { font-size: 10px; font-weight: 800; color: #007aff; text-transform: uppercase; margin: 2px 0 8px 0; letter-spacing: 0.4px; display: flex; align-items: center; }
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
        "Goal/NoGoal": "Esito_Goal_NoGoal", "Combo DC + U/O": "Esito_DC+U/O2.5"
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
    return "-"

# Titolo Brand
st.markdown("""
<div class="brand-box">
    <div class="main-title">⚽ Betting Pro Mobile</div>
    <div class="version-label">Versione Progetto: 5.72</div>
</div>
""", unsafe_allow_html=True)

# PULSANTI FASE 1 e FASE 2
testo_p1 = f"🚀 FASE 1: Estrazione & Pronostici ({st.session_state.log_fase1})"
if st.button(testo_p1, key="fase_1_btn", use_container_width=True):
    with st.spinner("⏳ In corso..."):
        try:
            import modulo_01_estrattore as m1
            import modulo_02_motore as m2
            m1.esegui_estrazione()
            m2.esegui_calcolo_motore()
            st.session_state.log_fase1 = datetime.datetime.now(FUSO_ROMA).strftime("%H:%M:%S")
            st.rerun()
        except Exception as e: st.error(f"Errore: {str(e)}")

testo_p2 = f"🏆 FASE 2: Convalida Risultati ({st.session_state.log_fase2})"
if st.button(testo_p2, key="fase_2_btn", use_container_width=True):
    with st.spinner("⏳ In corso..."):
        try:
            import modulo_03_validatore as m3
            m3.esegui_validazione()
            st.session_state.log_fase2 = datetime.datetime.now(FUSO_ROMA).strftime("%H:%M:%S")
            st.rerun()
        except Exception as e: st.error(f"Errore: {str(e)}")

# --- FASE 3 INTEGRATA INTERNAMENTE (BYPASS MODULO ESTERNO) ---
testo_p3 = f"🗄️ FASE 3: Archiviazione Totale ({st.session_state.log_fase3})"
if st.button(testo_p3, key="fase_3_btn", use_container_width=True):
    with st.spinner("⏳ Archiviazione Cloud Diretta..."):
        try:
            if os.path.exists(STORICO_FILE):
                df_v = pd.read_excel(STORICO_FILE)
                if not df_v.empty:
                    df_p = pd.read_excel(DB_FILE) if os.path.exists(DB_FILE) else pd.DataFrame()
                    
                    # Unione con eliminazione doppioni nativa
                    if not df_p.empty:
                        df_abbi = pd.concat([df_p, df_v], ignore_index=True, sort=False)
                        df_abbi = df_abbi.drop_duplicates(subset=['Data_Ora_Match', '3. Match'], keep='last')
                    else:
                        df_abbi = df_v
                    
                    df_abbi.to_excel(DB_FILE, index=False)
                    st.session_state.log_fase3 = datetime.datetime.now(FUSO_ROMA).strftime("%H:%M:%S")
                    st.toast("🗄️ Database Sincronizzato con Successo!", icon="✅")
                    st.rerun()
                else: st.warning("Storico vuoto.")
            else: st.error("File storico non trovato.")
        except Exception as e: st.error(f"Blocco: {str(e)}")

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# TAB ORIZZONTALI
col_t1, col_t2, col_t3 = st.columns(3)
with col_t1:
    if st.button(f"🎯 Palinsesto ({len(df_palinsesto)})", key="btn_pal", use_container_width=True): st.session_state.tab_selezionata = "PALINSESTO"; st.rerun()
with col_t2:
    if st.button(f"📊 Storico ({len(df_storico)})", key="btn_sto", use_container_width=True): st.session_state.tab_selezionata = "STORICO"; st.rerun()
with col_t3:
    if st.button(f"🗄️ Database ({len(df_database)})", key="btn_db", use_container_width=True): st.session_state.tab_selezionata = "DATABASE"; st.rerun()

# BOX ACCURATEZZA
dict_acc = calcola_accuratezza_globale()
if dict_acc:
    st.markdown('<div class="accuracy-container"><div class="accuracy-title">📈 Performance Dixon-Coles</div><div class="accuracy-grid">', unsafe_allow_html=True)
    for m_name, m_val in dict_acc.items():
        st.markdown(f'<div class="accuracy-item"><span>{m_name}</span><span class="accuracy-val">{m_val}</span></div>', unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

# RENDERING DATI
if st.session_state.tab_selezionata == "PALINSESTO" and not df_palinsesto.empty:
    for idx, row in df_palinsesto.iterrows():
        st.markdown(f"""<div class="match-card"><div class="meta-label">🏆 {safe_get(row, ['Campionato'])}</div><div class="team-text">{safe_get(row, ['3. Match', 'Match'])}</div><div class="market-box"><div class="market-cell"><b>1X2</b><div>{safe_get(row, ['1X2'])}</div></div><div class="market-cell"><b>Ris. Esatto</b><div>{safe_get(row, ['Risultato_Esatto'])}</div></div></div></div>""", unsafe_allow_html=True)
elif st.session_state.tab_selezionata == "STORICO" and not df_storico.empty:
    for idx, row in df_storico.iterrows():
        st.markdown(f"""<div class="match-card"><div class="meta-label">🏆 {safe_get(row, ['Campionato'])}</div><div class="team-text">{safe_get(row, ['3. Match', 'Match'])}</div><div class="score-badge">⚽ Fin: {safe_get(row, ['Risultato_Reale'])}</div></div>""", unsafe_allow_html=True)
elif st.session_state.tab_selezionata == "DATABASE" and not df_database.empty:
    for idx, row in df_database.iterrows():
        st.markdown(f"""<div class="match-card"><div class="meta-label">📦 {safe_get(row, ['Campionato'])}</div><div class="team-text">{safe_get(row, ['3. Match', 'Match'])}</div><div>Risultato: {safe_get(row, ['Risultato_Reale'])}</div></div>""", unsafe_allow_html=True)
