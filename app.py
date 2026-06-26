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

# Determinazione della palette cromatica esatta
if st.session_state.tab_selezionata == "PALINSESTO":
    colore_tema = "#eefae1"      
    colore_bordo = "#a3e2ab"     
elif st.session_state.tab_selezionata == "STORICO":
    colore_tema = "#f1effa"      
    colore_bordo = "#c5bfe7"     
else:
    colore_tema = "#fffde6"      
    colore_bordo = "#f6eb9d"     

# --- RESTYLING GRAFICO ULTRA-OTTIMIZZATO (VERSIONE 5.65) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {colore_tema} !important; transition: background-color 0.2s ease; }}
    
    .block-container {{ 
        padding-top: 2rem !important; 
        padding-bottom: 1rem !important; 
        padding-left: 0.5rem !important; 
        padding-right: 0.5rem !important; 
    }}
    
    .brand-box {{ text-align: center; margin-bottom: 12px; padding: 2px; }}
    .main-title {{ font-size: 22px; font-weight: 800; color: #1c1c1e; margin: 0; }}
    .version-label {{ font-size: 10px; font-weight: 700; color: #007aff; margin-top: 1px; text-transform: uppercase; letter-spacing: 0.5px; }}

    div.stButton > button {{
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 11px !important;
        padding: 6px 10px !important;
        height: auto !important;
        width: 100% !important;
        border: none !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03) !important;
        margin-bottom: -4px !important;
    }}
    
    div.stButton > button[id*="fase_1"] {{ background-color: #2cd158 !important; color: white !important; }}
    div.stButton > button[id*="fase_2"] {{ background-color: #6a5acd !important; color: white !important; }}
    div.stButton > button[id*="fase_3"] {{ background-color: #ffd700 !important; color: #1c1c1e !important; }}
    
    .tab-click-col div.stButton > button {{
        font-size: 10px !important;
        padding: 6px 2px !important;
        border-radius: 6px !important;
        border: 1px solid #d1d1d6 !important;
        text-transform: uppercase;
    }}
    
    .match-card {{ 
        background-color: #ffffff !important; 
        padding: 12px; 
        border-radius: 14px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.04); 
        margin-bottom: 10px; 
        border: 1px solid {colore_bordo} !important; 
    }}
    
    .meta-label {{ color: #007aff; font-size: 9px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 2px; }}
    .team-text {{ font-size: 15px; font-weight: 700; color: #1c1c1e; margin: 2px 0 6px 0; letter-spacing: -0.3px; }}
    .score-badge {{ background-color: rgba(240,240,245,1); color: #1c1c1e; font-size: 11px; font-weight: 700; padding: 4px 8px; border-radius: 6px; display: inline-block; margin-bottom: 6px; border: 1px solid {colore_bordo}; }}
    
    .block-header {{ font-size: 10px; font-weight: 800; color: #007aff; text-transform: uppercase; margin: 2px 0 8px 0; letter-spacing: 0.4px; display: flex; align-items: center; }}
    .block-header.stats {{ color: #ff9500; }}

    .market-box {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 5px; }}
    .market-cell {{ background: rgba(248, 249, 250, 1); padding: 6px; border-radius: 6px; font-size: 11px; display: flex; flex-direction: column; justify-content: center; border: 1px solid #e5e5ea; }}
    .market-cell b {{ color: #8e8e93; font-size: 9px; text-transform: uppercase; margin-bottom: 1px; }}
    .market-val-row {{ display: flex; justify-content: space-between; align-items: center; font-weight: 600; color: #1c1c1e; }}
    
    .win-badge {{ color: #34c759; font-weight: bold; font-size: 9px; background: #e8f9ee; padding: 2px 5px; border-radius: 4px; text-transform: uppercase; }}
    .lose-badge {{ color: #ff3b30; font-weight: bold; font-size: 9px; background: #ffebeb; padding: 2px 5px; border-radius: 4px; text-transform: uppercase; }}
    .wait-badge {{ color: #ff9500; font-weight: bold; font-size: 9px; background: #fff5e6; padding: 2px 5px; border-radius: 4px; text-transform: uppercase; }}
    
    .match-separator {{ margin-bottom: 18px; border-bottom: 2px dotted {colore_bordo}; height: 1px; width: 100%; }}
    
    .accuracy-container {{ background: #ffffff; padding: 12px; border-radius: 14px; margin-top: 12px; margin-bottom: 14px; box-shadow: 0 3px 10px rgba(0,0,0,0.03); border: 1px solid #d1d1d6; }}
    .accuracy-title {{ font-size: 11px; font-weight: 800; color: #1c1c1e; text-transform: uppercase; margin-bottom: 8px; text-align: center; letter-spacing: 0.5px; }}
    .accuracy-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; }}
    .accuracy-item {{ background: #f8f9fa; padding: 6px 8px; border-radius: 8px; font-size: 11px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #e5e5ea; }}
    .accuracy-item span {{ color: #48484a; font-weight: 600; }}
    .accuracy-val {{ color: #007aff; font-weight: 800; font-size: 11px; }}
    </style>
""", unsafe_allow_html=True)

def calcola_accuratezza_globale():
    frames = []
    if not df_storico.empty: frames.append(df_storico)
    if not df_database.empty: frames.append(df_database)
    if not frames: return {}
    
    df_totale = pd.concat(frames, ignore_index=True)
    
    mappa_esiti = {
        "1X2": "Esito_1X2", 
        "Ris. Esatto": "Esito_Risultato_Esatto", 
        "Doppia Chance": "Esito_Doppia_Chance",
        "U/O 1.5": "Esito_U/O_1.5", 
        "U/O 2.5": "Esito_U/O_2.5", 
        "U/O 3.5": "Esito_U/O_3.5", 
        "Goal/NoGoal": "Esito_Goal_NoGoal",
        "Combo DC + U/O": "Esito_DC+U/O2.5",
        "MG Casa": "Esito_Media_Goal_Casa",
        "MG Ospite": "Esito_Media_Goal_Trasferta",
        "MG Totale": "Esito_Media_Goal_Totale",
        "Corner 1X2": "Esito_Corner_1X2"
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
    """Cerca in modo sicuro la colonna provando sia con indice numerico sia liscia"""
    for k in keys_list:
        if k in row: return row[k]
        # Prova varianti comuni con prefissi numerici
        for prefix in ["1. ", "2. ", "3. ", "4. ", "5. ", "6. ", "7. ", "8. "]:
            if f"{prefix}{k}" in row: return row[f"{prefix}{k}"]
    return "-"

# Titolo Brand
st.markdown("""
<div class="brand-box">
    <div class="main-title">⚽ Betting Pro Mobile</div>
    <div class="version-label">Versione Progetto: 5.65</div>
</div>
""", unsafe_allow_html=True)

# --- I 3 PULSANTI VERTICALI DI AZIONE ---
testo_p1 = f"🚀 FASE 1: Estrazione & Pronostici ({st.session_state.log_fase1})"
if st.button(testo_p1, key="fase_1_btn", use_container_width=True):
    with st.spinner("⏳ In corso..."):
        try:
            import modulo_01_estrattore as m1
            import modulo_02_motore as m2
            m1.esegui_estrazione()
            m2.esegui_calcolo_motore()
            st.session_state.log_fase1 = datetime.datetime.now(FUSO_ROMA).strftime("%H:%M:%S")
            st.toast("🚀 Palinsesto Estratto!", icon="✅")
            st.rerun()
        except Exception as e: st.error(f"Errore: {str(e)}")

testo_p2 = f"🏆 FASE 2: Convalida Risultati ({st.session_state.log_fase2})"
if st.button(testo_p2, key="fase_2_btn", use_container_width=True):
    with st.spinner("⏳ In corso..."):
        try:
            import modulo_03_validatore as m3
            m3.esegui_validazione()
            st.session_state.log_fase2 = datetime.datetime.now(FUSO_ROMA).strftime("%H:%M:%S")
            st.toast("🏆 Storico Convalidato!", icon="✅")
            st.rerun()
        except Exception as e: st.error(f"Errore: {str(e)}")

testo_p3 = f"🗄️ FASE 3: Archiviazione Totale ({st.session_state.log_fase3})"
if st.button(testo_p3, key="fase_3_btn", use_container_width=True):
    with st.spinner("⏳ In corso..."):
        try:
            import modulo_04_trasferitore as m4
            m4.esegui_allineamento()
            st.session_state.log_fase3 = datetime.datetime.now(FUSO_ROMA).strftime("%H:%M:%S")
            st.toast("🗄️ Database Sincronizzato!", icon="✅")
            st.rerun()
        except Exception as e: st.error(f"Errore: {str(e)}")

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# --- MICRO-TAB ORIZZONTALIZZATI COMPATTI PER IPHONE ---
st.markdown("<div class='tab-click-col'>", unsafe_allow_html=True)
col_t1, col_t2, col_t3 = st.columns(3)

with col_t1:
    label_p1 = f"🎯 Palinsesto ({len(df_palinsesto)})"
    if st.session_state.tab_selezionata == "PALINSESTO":
        st.button(label_p1, key="btn_pal", use_container_width=True)
    else:
        if st.button(label_p1, key="btn_pal_off", use_container_width=True):
            st.session_state.tab_selezionata = "PALINSESTO"
            st.rerun()

with col_t2:
    label_p2 = f"📊 Storico ({len(df_storico)})"
    if st.session_state.tab_selezionata == "STORICO":
        st.button(label_p2, key="btn_sto", use_container_width=True)
    else:
        if st.button(label_p2, key="btn_sto_off", use_container_width=True):
            st.session_state.tab_selezionata = "STORICO"
            st.rerun()

with col_t3:
    label_p3 = f"🗄️ Database ({len(df_database)})"
    if st.session_state.tab_selezionata == "DATABASE":
        st.button(label_p3, key="btn_db", use_container_width=True)
    else:
        if st.button(label_p3, key="btn_db_off", use_container_width=True):
            st.session_state.tab_selezionata = "DATABASE"
            st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(f"""
    <style>
    #button-btn_pal {{ background-color: #2cd158 !important; color: white !important; font-weight: 800 !important; }}
    #button-btn_sto {{ background-color: #6a5acd !important; color: white !important; font-weight: 800 !important; }}
    #button-btn_db {{ background-color: #ffd700 !important; color: #1c1c1e !important; font-weight: 800 !important; }}
    #button-btn_pal_off, #button-btn_sto_off, #button-btn_db_off {{ background-color: #ffffff !important; color: #1c1c1e !important; }}
    </style>
""", unsafe_allow_html=True)

# BOX ACCURATEZZA ALGORITMO (12 Mercati Completi)
dict_acc = calcola_accuratezza_globale()
if dict_acc:
    st.markdown("""
    <div class="accuracy-container">
        <div class="accuracy-title">📈 Performance Reale Dixon-Coles (12 Mercati)</div>
        <div class="accuracy-grid">
    """, unsafe_allow_html=True)
    for m_name, m_val in dict_acc.items():
        st.markdown(f'<div class="accuracy-item"><span>{m_name}</span><span class="accuracy-val">{m_val}</span></div>', unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

def clean(val):
    if pd.isna(val) or val == "-": return "-"
    try:
        f_val = float(val)
        return str(int(f_val)) if f_val.is_integer() else str(f_val)
    except: return str(val)

# --- RENDERING INTERFACCIA ---
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
                    <div class="market-cell"><b>Gol Fatti Totali</b><div class="market-val-row"><span>{clean(safe_get(row, ['Media_Goal_Casa_Orig', 'Gol_Fatti_Casa']))} F</span><span>vs</span><span>{clean(safe_get(row, ['Media_Goal_Trasferta_Orig', 'Gol_Fatti_Ospite']))} F</span></div></div>
                    <div class="market-cell"><b>Gol Subiti Totali</b><div class="market-val-row"><span>{clean(safe_get(row, ['Goal_Subiti_Casa']))} S</span><span>vs</span><span>{clean(safe_get(row, ['Goal_Subiti_Ospite']))} S</span></div></div>
                </div>
            </div>
            <div class="match-separator"></div>
            """, unsafe_allow_html=True)
    else: st.info("Palinsesto vuoto.")

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

elif st.session_state.tab_selezionata == "DATABASE":
    if not df_database.empty:
        st.markdown('<div class="block-header">🗄️ Archivio Generale Partite</div>', unsafe_allow_html=True)
        for idx, row in df_database.iterrows():
            st.markdown(f"""
            <div class="match-card">
                <div class="meta-label">📦 ID Match: {safe_get(row, ['Match_ID'])} | {safe_get(row, ['Campionato'])} | {safe_get(row, ['Data_Ora_Match', 'Data'])}</div>
                <div class="team-text" style="font-size:13px;">{safe_get(row, ['3. Match', 'Match'])}</div>
                <div class="market-box" style="grid-template-columns: 1fr 1fr;">
                    <div class="market-cell"><b>Risultato</b><div style="font-weight:700;">{safe_get(row, ['Risultato_Reale'])}</div></div>
                    <div class="market-cell"><b>Esito 1X2</b><div style="font-weight:700;">{safe_get(row, ['Esito_1X2'])}</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else: st.info("Database di archiviazione vuoto.")
