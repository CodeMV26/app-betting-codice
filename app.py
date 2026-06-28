import streamlit as st
import pandas as pd
import os
import datetime
from zoneinfo import ZoneInfo

# PROGRESSIVO CHAT: #119 | Data: 28 Giugno 2026 | Ora: 21:24:12
# Versione Progetto: 6.13 (Integrazione Integrale Tab Simulatore iOS 4 Colonne)

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

len_pal = len(df_palinsesto) if not df_palinsesto.empty else 0
len_sto = len(df_storico) if not df_storico.empty else 0
len_db = len(df_database) if not df_database.empty else 0

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
    .tab-click-col div.stButton > button { font-size: 9px !important; padding: 6px 1px !important; border-radius: 6px !important; border: 1px solid #d1d1d6 !important; text-transform: uppercase; }
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
    
    /* Nuovi Stili per la sezione Backtest */
    .delta-win { color: #2cd158; font-weight: 800; font-size: 10px; background: #e8f9ee; padding: 1px 4px; border-radius: 3px; }
    .delta-lose { color: #ff3b30; font-weight: 800; font-size: 10px; background: #ffebeb; padding: 1px 4px; border-radius: 3px; }
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

def clean(val):
    if pd.isna(val) or str(val).strip().upper() == "NONE" or str(val).strip() == "-": return "-"
    try:
        f_val = float(val)
        return str(int(f_val)) if f_val.is_integer() else f"{f_val:.1f}"
    except: return str(val)

st.markdown("""
<div class="brand-box">
    <div class="main-title">⚽ Betting Pro Mobile</div>
    <div class="version-label">Versione Progetto: 6.13</div>
</div>
""", unsafe_allow_html=True)

# --- PULSANTI AZIONE INTERFACCIA ---
if st.button(f"🚀 FASE 1: Estrazione & Pronostici ({st.session_state.log_fase1})", key="fase_1_btn", use_container_width=True):
    with st.spinner("⏳ In corso..."):
        try:
            import modulo_01_estrattore as m1
            import modulo_02_motore as m2
            m1.esegui_estrazione()
            m2.esegui_calcolo_motore()
            st.session_state.log_fase1 = datetime.datetime.now(FUSO_ROMA).strftime("%H:%M:%S")
            st.toast("🚀 Palinsesto Estratto!", icon="✅")
            st.rerun()
        except Exception as e: st.error(f"Errore Fase 1: {str(e)}")

if st.button(f"🏆 FASE 2: Convalida Risultati ({st.session_state.log_fase2})", key="fase_2_btn", use_container_width=True):
    with st.spinner("⏳ In corso..."):
        try:
            import modulo_03_validatore as m3
            m3.esegui_validazione()
            st.session_state.log_fase2 = datetime.datetime.now(FUSO_ROMA).strftime("%H:%M:%S")
            st.toast("🏆 Storico Convalidato!", icon="✅")
            st.rerun()
        except Exception as e: st.error(f"Errore Fase 2: {str(e)}")

if st.button(f"🗄️ FASE 3: Archiviazione Totale ({st.session_state.log_fase3})", key="fase_3_btn", use_container_width=True):
    with st.spinner("⏳ In corso..."):
        try:
            import modulo_04_trasferitore as m4
            if hasattr(m4, 'esegui_allineamento'): m4.esegui_allineamento()
            elif hasattr(m4, 'esegui_trasferimento'): m4.esegui_trasferimento()
            st.session_state.log_fase3 = datetime.datetime.now(FUSO_ROMA).strftime("%H:%M:%S")
            st.toast("🗄️ Database Sincronizzato!", icon="✅")
            st.rerun()
        except Exception as e: st.error(f"Errore Fase 3: {str(e)}")

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# --- TAB NAVIGAZIONE IOS BLINDATA A 4 COLONNE ---
st.markdown("<div class='tab-click-col'>", unsafe_allow_html=True)
col_t1, col_t2, col_t3, col_t4 = st.columns(4)

label_p1 = f"🎯 Palin ({len_pal})"
label_p2 = f"📊 Stor ({len_sto})"
label_p3 = f"🗄️ DB ({len_db})"
label_p4 = f"🧪 Sim ({len_db})"

with col_t1:
    if st.session_state.tab_selezionata == "PALINSESTO": st.button(label_p1, key="btn_pal", use_container_width=True)
    else:
        if st.button(label_p1, key="btn_pal_off", use_container_width=True): st.session_state.tab_selezionata = "PALINSESTO"; st.rerun()

with col_t2:
    if st.session_state.tab_selezionata == "STORICO": st.button(label_p2, key="btn_sto", use_container_width=True)
    else:
        if st.button(label_p2, key="btn_sto_off", use_container_width=True): st.session_state.tab_selezionata = "STORICO"; st.rerun()

with col_t3:
    if st.session_state.tab_selezionata == "DATABASE": st.button(label_p3, key="btn_db", use_container_width=True)
    else:
        if st.button(label_p3, key="btn_db_off", use_container_width=True): st.session_state.tab_selezionata = "DATABASE"; st.rerun()

with col_t4:
    if st.session_state.tab_selezionata == "SIMULATORE": st.button(label_p4, key="btn_sim", use_container_width=True)
    else:
        if st.button(label_p4, key="btn_sim_off", use_container_width=True): st.session_state.tab_selezionata = "SIMULATORE"; st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

dict_acc = calcola_accuratezza_globale()
if dict_acc and st.session_state.tab_selezionata != "SIMULATORE":
    st.markdown('<div class="accuracy-container"><div class="accuracy-title">📈 Performance Reale Dixon-Cole (12 Mercati)</div><div class="accuracy-grid">', unsafe_allow_html=True)
    for m_name, m_val in dict_acc.items(): st.markdown(f'<div class="accuracy-item"><span>{m_name}</span><span class="accuracy-val">{m_val}</span></div>', unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

# --- VIEW RENDER PALINSESTO ---
if st.session_state.tab_selezionata == "PALINSESTO":
    if not df_palinsesto.empty:
        for idx, row in df_palinsesto.iterrows():
            st.markdown(f"""
            <div class="match-card">
                <div class="meta-label">🏆 {safe_get(row, ['Campionato'])} | {safe_get(row, ['Data_Ora_Match', 'Data'])}</div>
                <div class="team-text"> {safe_get(row, ['3. Match', 'Match'])}</div>
                <div class="block-header">🎲 Algoritmo & Probabilità</div>
                <div class="market-box">
                    <div class="market-cell"><b>1X2</b><div class="market-val-row">{safe_get(row, ['1X2'])}</div></div>
                    <div class="market-cell"><b>Ris. Esatto</b><div class="market-val-row">{safe_get(row, ['Risultato_Esatto'])}</div></div>
                    <div class="market-cell"><b>Doppia Chance</b><div class="market-val-row">{safe_get(row, ['Doppia_Chance'])}</div></div>
                    <div class="market-cell"><b>Combo DC+U/O2.5</b><div class="market-val-row">{safe_get(row, ['DC+U/O2.5', 'DC+U/O_2.5'])}</div></div>
                    <div class="market-cell"><b>U/O 1.5</b><div class="market-val-row">{safe_get(row, ['U/O_1.5'])}</div></div>
                    <div class="market-cell"><b>U/O 2.5</b><div class="market-val-row">{safe_get(row, ['U/O_2.5'])}</div></div>
                    <div class="market-cell"><b>U/O 3.5</b><div class="market-val-row">{safe_get(row, ['U/O_3.5'])}</div></div>
                    <div class="market-cell"><b>Goal/NoGoal</b><div class="market-val-row">{safe_get(row, ['Goal_NoGoal'])}</div></div>
                    <div class="market-cell"><b>MG Casa Expect.</b><div class="market-val-row">{safe_get(row, ['Pronostico_MG_Casa', 'MG_Casa'])}</div></div>
                    <div class="market-cell"><b>MG Ospite Expect.</b><div class="market-val-row">{safe_get(row, ['Pronostico_MG_Trasferta', 'MG_Ospite'])}</div></div>
                    <div class="market-cell"><b>MG Totale Expect.</b><div class="market-val-row">{safe_get(row, ['Pronostico_MG_Totale', 'MG_Totale'])}</div></div>
                    <div class="market-cell"><b>Corner 1X2</b><div class="market-val-row">{safe_get(row, ['Corner_1X2'])}</div></div>
                </div>
            </div>
            <div class="match-card">
                <div class="meta-label" style="color: #ff9500;">📊 STATISTICHE TEAM | LIVE DATA</div>
                <div class="team-text" style="font-size: 13px; color: #48484a;">{safe_get(row, ['3. Match', 'Match'])}</div>
                <div class="block-header stats">📊 Storico Stagionale</div>
                <div class="market-box">
                    <div class="market-cell"><b>Pos. Classifica</b><div class="market-val-row"><span>{clean(safe_get(row, ['PosClassifica_Casa']))}°</span><span>vs</span><span>{clean(safe_get(row, ['PosClassifica_Ospite']))}°</span></div></div>
                    <div class="market-cell"><b>Punti Totali</b><div class="market-val-row"><span>{clean(safe_get(row, ['Punti_Casa']))} pt</span><span>vs</span><span>{clean(safe_get(row, ['Punti_Trasferta']))} pt</span></div></div>
                    <div class="market-cell"><b>Partite Giocate</b><div class="market-val-row"><span>{clean(safe_get(row, ['Giocate_Casa']))} G</span><span>vs</span><span>{clean(safe_get(row, ['Giocate_Ospite']))} G</span></div></div>
                    <div class="market-cell"><b>V / P / S</b><div class="market-val-row"><span>{clean(safe_get(row, ['Vinte_Casa']))}-{clean(safe_get(row, ['Pareggi_Casa']))}-{clean(safe_get(row, ['Perse_Casa']))}</span><span>vs</span><span>{clean(safe_get(row, ['Vinte_Ospite']))}-{clean(safe_get(row, ['Pareggi_Ospite']))}-{clean(safe_get(row, ['Perse_Ospite']))}</span></div></div>
                    <div class="market-cell"><b>Gol Fatti Totali</b><div class="market-val-row"><span>{clean(safe_get(row, ['Media_Goal_Casa_Orig', 'Gol_Fatti_Casa', 'GolFatti_Casa']))} F</span><span>vs</span><span>{clean(safe_get(row, ['Media_Goal_Trasferta_Orig', 'Gol_Fatti_Ospite', 'GolFatti_Ospite']))} F</span></div></div>
                    <div class="market-cell"><b>Gol Subiti Totali</b><div class="market-val-row"><span>{clean(safe_get(row, ['Goal_Subiti_Casa', 'GolSubiti_Casa']))} S</span><span>vs</span><span>{clean(safe_get(row, ['Goal_Subiti_Ospite', 'GolSubiti_Ospite']))} S</span></div></div>
                </div>
            </div>
            <div class="match-separator"></div>
            """, unsafe_allow_html=True)
    else: st.info("Palinsesto vuoto.")

# --- VIEW RENDER STORICO ---
elif st.session_state.tab_selezionata == "STORICO":
    if not df_storico.empty:
        for idx, row in df_storico.iterrows():
            st.markdown(f"""
            <div class="match-card">
                <div class="meta-label">🏆 {safe_get(row, ['Campionato'])} | {safe_get(row, ['Data_Ora_Match', 'Data'])}</div>
                <div class="team-text">{safe_get(row, ['3. Match', 'Match'])}</div>
                <div class="score-badge">⚽ Risultato Finale: {safe_get(row, ['Risultato_Reale'])}</div>
                <div class="block-header">🎯 Esiti Pronostici Validati (12 Mercati)</div>
                <div class="market-box">
                    <div class="market-cell"><b>1X2 ({safe_get(row, ['1X2'])})</b><div class="market-val-row">{get_badge(safe_get(row, ['Esito_1X2']))}</div></div>
                    <div class="market-cell"><b>Ris. Esatto ({safe_get(row, ['Risultato_Esatto'])})</b><div class="market-val-row">{get_badge(safe_get(row, ['Esito_Risultato_Esatto']))}</div></div>
                    <div class="market-cell"><b>Doppia Ch. ({safe_get(row, ['Doppia_Chance'])})</b><div class="market-val-row">{get_badge(safe_get(row, ['Esito_Doppia_Chance']))}</div></div>
                    <div class="market-cell"><b>Combo DC+U/O ({safe_get(row, ['DC+U/O2.5', 'DC+U/O_2.5'])})</b><div class="market-val-row">{get_badge(safe_get(row, ['Esito_DC+U/O2.5']))}</div></div>
                    <div class="market-cell"><b>U/O 1.5 ({safe_get(row, ['U/O_1.5'])})</b><div class="market-val-row">{get_badge(safe_get(row, ['Esito_U/O_1.5']))}</div></div>
                    <div class="market-cell"><b>U/O 2.5 ({safe_get(row, ['U/O_2.5'])})</b><div class="market-val-row">{get_badge(safe_get(row, ['Esito_U/O_2.5']))}</div></div>
                    <div class="market-cell"><b>U/O 3.5 ({safe_get(row, ['U/O_3.5'])})</b><div class="market-val-row">{get_badge(safe_get(row, ['Esito_U/O_3.5']))}</div></div>
                    <div class="market-cell"><b>Goal/NG ({safe_get(row, ['Goal_NoGoal'])})</b><div class="market-val-row">{get_badge(safe_get(row, ['Esito_Goal_NoGoal']))}</div></div>
                    <div class="market-cell"><b>MG Casa ({safe_get(row, ['Pronostico_MG_Casa', 'MG_Casa'])})</b><div class="market-val-row">{get_badge(safe_get(row, ['Esito_Media_Goal_Casa']))}</div></div>
                    <div class="market-cell"><b>MG Ospite ({safe_get(row, ['Pronostico_MG_Trasferta', 'MG_Ospite'])})</b><div class="market-val-row">{get_badge(safe_get(row, ['Esito_Media_Goal_Trasferta']))}</div></div>
                    <div class="market-cell"><b>MG Totale ({safe_get(row, ['Pronostico_MG_Totale', 'MG_Totale'])})</b><div class="market-val-row">{get_badge(safe_get(row, ['Esito_Media_Goal_Totale']))}</div></div>
                    <div class="market-cell"><b>Corner 1X2 ({safe_get(row, ['Corner_1X2'])})</b><div class="market-val-row">{get_badge(safe_get(row, ['Esito_Corner_1X2']))}</div></div>
                </div>
            </div>
            <div class="match-separator"></div>
            """, unsafe_allow_html=True)
    else: st.info("Nessun match presente nello storico corrente.")

# --- VIEW RENDER DATABASE ---
elif st.session_state.tab_selezionata == "DATABASE":
    if not df_database.empty:
        st.markdown('<div class="block-header">🗄️ Archivio Generale Partite</div>', unsafe_allow_html=True)
        for idx, row in df_database.iterrows():
            st.markdown(f"""
            <div class="match-card">
                <div class="meta-label">📦 {safe_get(row, ['Campionato'])} | {safe_get(row, ['Data_Ora_Match', 'Data'])}</div>
                <div class="team-text">{safe_get(row, ['3. Match', 'Match'])}</div>
                <div class="market-box" style="grid-template-columns: 1fr 1fr; margin-bottom: 8px;">
                    <div class="market-cell"><b>Risultato Reale</b><div style="font-weight:700;">{safe_get(row, ['Risultato_Reale'])}</div></div>
                    <div class="market-cell"><b>Esito 1X2</b><div style="font-weight:700;">{safe_get(row, ['Esito_1X2'])}</div></div>
                </div>
                <div class="block-header stats" style="margin-top: 6px;">📊 Statistiche Storiche Branch</div>
                <div class="market-box">
                    <div class="market-cell"><b>Pos. Classifica</b><div class="market-val-row"><span>{clean(safe_get(row, ['PosClassifica_Casa']))}°</span><span>vs</span><span>{clean(safe_get(row, ['PosClassifica_Ospite']))}°</span></div></div>
                    <div class="market-cell"><b>Punti Totali</b><div class="market-val-row"><span>{clean(safe_get(row, ['Punti_Casa']))} pt</span><span>vs</span><span>{clean(safe_get(row, ['Punti_Trasferta']))} pt</span></div></div>
                    <div class="market-cell"><b>Partite Giocate</b><div class="market-val-row"><span>{clean(safe_get(row, ['Giocate_Casa']))} G</span><span>vs</span><span>{clean(safe_get(row, ['Giocate_Ospite']))} G</span></div></div>
                    <div class="market-cell"><b>V / P / S</b><div class="market-val-row"><span>{clean(safe_get(row, ['Vinte_Casa']))}-{clean(safe_get(row, ['Pareggi_Casa']))}-{clean(safe_get(row, ['Perse_Casa']))}</span><span>vs</span><span>{clean(safe_get(row, ['Vinte_Ospite']))}-{clean(safe_get(row, ['Pareggi_Ospite']))}-{clean(safe_get(row, ['Perse_Ospite']))}</span></div></div>
                    <div class="market-cell"><b>Gol Fatti Totali</b><div class="market-val-row"><span>{clean(safe_get(row, ['Media_Goal_Casa_Orig', 'Gol_Fatti_Casa', 'GolFatti_Casa']))} F</span><span>vs</span><span>{clean(safe_get(row, ['Media_Goal_Trasferta_Orig', 'Gol_Fatti_Ospite', 'GolFatti_Ospite']))} F</span></div></div>
                    <div class="market-cell"><b>Gol Subiti Totali</b><div class="market-val-row"><span>{clean(safe_get(row, ['Goal_Subiti_Casa', 'GoalSubiti_Casa']))} S</span><span>vs</span><span>{clean(safe_get(row, ['Goal_Subiti_Ospite', 'GoalSubiti_Ospite']))} S</span></div></div>
                </div>
            </div>
            <div class="match-separator"></div>
            """, unsafe_allow_html=True)
    else: st.info("Database di archiviazione vuoto.")

# =========================================================================
# 🧪 RIGA 290+: SEZIONE DIRETTA INTERFACCIA MODULO 05 (SIMULATORE)
# =========================================================================
elif st.session_state.tab_selezionata == "SIMULATORE":
    st.markdown('<div class="block-header" style="color:#6a5acd; font-size:12px; margin-bottom:12px;">🧪 SIMULATORE DI STRATEGIE & BACKTESTING</div>', unsafe_allow_html=True)
    
    if df_database.empty:
        st.warning("⚠️ L'archivio del Database è vuoto. Archivia le partite con la Fase 3 per abilitare il simulatore.")
    else:
        # 1. Configurazione Parametri Editabili (Stile Impostazioni iOS)
        with st.expander("⚙️ PARAMETRI DI CALIBRAZIONE ALGORITMO", expanded=True):
            st.markdown("<p style='font-size:11px; color:#8e8e93; margin-top:-5px;'>Modifica le soglie matematiche per ricalcolare all'istante le accuratezze dello storico.</p>", unsafe_allow_html=True)
            
            s_uo15 = st.slider("Soglia Probabilità Under/Over 1.5", 0.30, 0.80, 0.52, 0.01)
            s_uo25 = st.slider("Soglia Probabilità Under/Over 2.5", 0.30, 0.80, 0.49, 0.01)
            s_uo35 = st.slider("Soglia Probabilità Under/Over 3.5", 0.30, 0.80, 0.52, 0.01)
            s_gng  = st.slider("Soglia Probabilità Goal/NoGoal", 0.30, 0.80, 0.52, 0.01)
            
            col_w1, col_w2 = st.columns(2)
            with col_w1: p_casa = st.slider("Peso Medie Casa", 0.70, 1.30, 1.05, 0.05)
            with col_w2: p_trasf = st.slider("Peso Medie Trasferta", 0.70, 1.30, 0.95, 0.05)

        # 2. Pulsante di Attivazione Backtest Touch Native
        if st.button("🧪 AVVIA BACKTEST SU ARCHIVIO GENERALE", key="run_backtest_btn", use_container_width=True):
            with st.spinner("⏳ Ricalcolo matrici Dixon-Cole in corso..."):
                try:
                    import numpy as np
                    import math
                    
                    # Funzioni matematiche locali per isolamento totale delle variabili
                    def poisson_local(l, k):
                        if l <= 0: return 1 if k == 0 else 0
                        return (math.exp(-l) * pow(l, k)) / math.factorial(k)

                    def dc_adj_local(i, j, xg_c, xg_t):
                        rho = -0.09
                        if i == 0 and j == 0: return 1 - (xg_c * xg_t * rho)
                        if i == 1 and j == 0: return 1 + (xg_t * rho)
                        if i == 0 and j == 1: return 1 + (xg_c * rho)
                        if i == 1 and j == 1: return 1 - rho
                        return 1.0

                    def get_mg_local(prob_v):
                        r = {
                            "1-2 MG": sum(prob_v[1:3]), "1-3 MG": sum(prob_v[1:4]), "1-4 MG": sum(prob_v[1:5]),
                            "2-3 MG": sum(prob_v[2:4]), "2-4 MG": sum(prob_v[2:5]), "3+ MG": sum(prob_v[3:]), "0-1 MG": sum(prob_v[0:2])
                        }
                        return max(r, key=r.get)

                    df_valid = df_database[df_database['Risultato_Reale'].astype(str).str.contains("-")].copy()
                    df_valid = df_valid[~df_valid['Risultato_Reale'].astype(str).str.contains("NON ANCORA")]
                    
                    sim_vinti = {
                        "1X2": 0, "Ris. Esatto": 0, "Doppia Chance": 0, "Combo DC + U/O": 0,
                        "U/O 1.5": 0, "U/O 2.5": 0, "U/O 3.5": 0, "Goal/NoGoal": 0,
                        "MG Casa": 0, "MG Ospite": 0, "Corner 1X2": 0
                    }
                    
                    tot_sim_matches = len(df_valid)
                    
                    if tot_sim_matches > 0:
                        for _, row_s in df_valid.iterrows():
                            res_s = str(row_s.get('Risultato_Reale', '-')).strip()
                            g_c_s, g_t_s = map(int, res_s.split("-"))
                            tot_g_s = g_c_s + g_t_s
                            segno_s = '1' if g_c_s > g_t_s else ('2' if g_t_s > g_c_s else 'X')
                            
                            m_gf_c = float(row_s.get('Media_Goal_Casa_Orig', row_s.get('Media_Goal_Casa', 1.20)))
                            m_gf_t = float(row_s.get('Media_Goal_Trasferta_Orig', row_s.get('Media_Goal_Trasferta', 1.10)))
                            if math.isnan(m_gf_c): m_gf_c = 1.20
                            if math.isnan(m_gf_t): m_gf_t = 1.10
                            
                            m_h, m_a = 1.20, 1.10
                            sos_c = (m_gf_c / m_h) * p_casa
                            sos_t = (m_gf_t / m_a) * p_trasf
                            
                            xg_c = ((m_gf_c * 1.00) / m_h) * sos_c * 1.08
                            xg_t = ((m_gf_t * 1.00) / m_a) * sos_t
                            
                            matrix = [[0.0 for _ in range(6)] for _ in range(6)]
                            for i in range(6):
                                for j in range(6):
                                    matrix[i][j] = poisson_local(xg_c, i) * poisson_local(xg_t, j) * dc_adj_local(i, j, xg_c, xg_t) * (1.12 if i == j else 1.0)
                                    
                            p1, px, p2, pu15, pu25, pu35, pgoal = 0, 0, 0, 0, 0, 0, 0
                            tot_p = sum(sum(r) for r in matrix) if sum(sum(r) for r in matrix) > 0 else 1.0
                            prob_c, prob_t = [0.0] * 6, [0.0] * 6
                            
                            for i in range(6):
                                for j in range(6):
                                    p_cell = matrix[i][j] / tot_p
                                    prob_c[i] += p_cell
                                    prob_t[j] += p_cell
                                    if i > j: p1 += p_cell
                                    elif i == j: px += p_cell
                                    else: p2 += p_cell
                                    if (i+j) < 1.5: pu15 += p_cell
                                    if (i+j) < 2.5: pu25 += p_cell
                                    if (i+j) < 3.5: pu35 += p_cell
                                    if i > 0 and j > 0: pgoal += p_cell
                                    
                            s_1x2 = max({'1': p1, 'X': px, '2': p2}, key={'1': p1, 'X': px, '2': p2}.get)
                            s_ex = f"{np.unravel_index(np.argmax(matrix), (6,6))[0]}-{np.unravel_index(np.argmax(matrix), (6,6))[1]}"
                            s_dc = "1X" if (p1 + px) > (p2 + px) else "X2"
                            s_uo15 = "UNDER 1.5" if pu15 > s_uo15 else "OVER 1.5"
                            s_uo25 = "UNDER 2.5" if pu25 > s_uo25 else "OVER 2.5"
                            s_uo35 = "UNDER 3.5" if pu35 > s_uo35 else "OVER 3.5"
                            s_gng = "GOAL" if pgoal > s_gng else "NOGOAL"
                            s_combo = f"{s_dc}+{s_uo25.split(' ')[0]}"
                            
                            if s_1x2 == segno_s: sim_vinti["1X2"] += 1
                            if s_ex == res_s: sim_vinti["Ris. Esatto"] += 1
                            if (s_dc == "1X" and segno_s in ['1','X']) or (s_dc == "X2" and segno_s in ['X','2']): sim_vinti["Doppia Chance"] += 1
                            if (s_uo15 == "OVER 1.5" and tot_g_s > 1.5) or (s_uo15 == "UNDER 1.5" and tot_g_s <= 1.5): sim_vinti["U/O 1.5"] += 1
                            if (s_uo25 == "OVER 2.5" and tot_g_s > 2.5) or (s_uo25 == "UNDER 2.5" and tot_g_s <= 2.5): sim_vinti["U/O 2.5"] += 1
                            if (s_uo35 == "OVER 3.5" and tot_g_s > 3.5) or (s_uo35 == "UNDER 3.5" and tot_g_s <= 3.5): sim_vinti["U/O 3.5"] += 1
                            if (s_gng == "GOAL" and g_c_s > 0 and g_t_s > 0) or (s_gng == "NOGOAL" and (g_c_s == 0 or g_t_s == 0)): sim_vinti["Goal/NoGoal"] += 1
                            
                            def chk_mg_l(p_str, gol):
                                p = p_str.replace("MG","").strip()
                                if "-" in p:
                                    g_min, g_max = map(int, p.split("-"))
                                    return g_min <= gol <= g_max
                                return gol >= 3 if "3+" in p else False
                                
                            if chk_mg_l(get_mg_local(prob_c), g_c_s): sim_vinti["MG Casa"] += 1
                            if chk_mg_l(get_mg_local(prob_t), g_t_s): sim_vinti["MG Ospite"] += 1
                            if s_combo == row_s.get('DC+U/O2.5') and row_s.get('Esito_DC+U/O2.5') == 'VINCENTE': sim_vinti["Combo DC + U/O"] += 1
                            if ("1" in row_s.get('Esito_Corner_1X2', 'X') and xg_c > xg_t + 0.3) or ("2" in row_s.get('Esito_Corner_1X2', 'X') and xg_t > xg_c + 0.3): sim_vinti["Corner 1X2"] += 1
                        
                        st.session_state.backtest_results = {m: f"{(sim_vinti[m]/tot_sim_matches)*100:.1f}% ({sim_vinti[m]}/{tot_sim_matches})" for m in sim_vinti}
                        st.toast("🧪 Backtest Completato!", icon="✅")
                    else:
                        st.error("Nessun match terminato utilizzabile trovato nell'archivio storico.")
                except Exception as e:
                    st.error(f"Errore Backtest: {str(e)}")

        # 3. Render Comparativo Scostamento Performance Reale vs Simulata
        if "backtest_results" in st.session_state:
            st.markdown('<div class="accuracy-container"><div class="accuracy-title">📈 SCOSTAMENTO PERFORMANCE (REALE VS SIMULATO)</div><div class="accuracy-grid">', unsafe_allow_html=True)
            for m_name, r_val in dict_acc.items():
                s_val = st.session_state.backtest_results.get(m_name, "0.0% (0)")
                try:
                    r_num = float(r_val.split("%")[0])
                    s_num = float(s_val.split("%")[0])
                    delta = s_num - r_num
                    badge_delta = f'<span class="delta-win">▲ +{delta:.1f}%</span>' if delta > 0 else (f'<span class="delta-lose">▼ {delta:.1f}%</span>' if delta < 0 else '<span style="font-size:9px; color:#8e8e93;">=</span>')
                except:
                    badge_delta = ""
                
                st.markdown(f"""
                <div class="accuracy-item" style="flex-direction:column; align-items:flex-start; gap:2px; height:auto; padding:8px;">
                    <div style="font-weight:800; color:#1c1c1e; font-size:11px; margin-bottom:2px;">{m_name}</div>
                    <div style="display:flex; justify-content:space-between; width:100%; font-size:10px; color:#48484a;"><span>Reale:</span><b>{r_val}</b></div>
                    <div style="display:flex; justify-content:space-between; width:100%; font-size:10px; color:#6a5acd;"><span>Simulato:</span><b>{s_val}</b></div>
                    <div style="width:100%; text-align:right; margin-top:2px;">{badge_delta}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)
