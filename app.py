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
        try: return pd.read_excel(path)
        except: return pd.DataFrame()
    return pd.DataFrame()

df_palinsesto = carica_dati(PALINSESTO_FILE)
df_storico = carica_dati(STORICO_FILE)
df_database = carica_dati(DB_FILE)

# Determinazione della palette cromatica esatta secondo direttiva del Direttore
if st.session_state.tab_selezionata == "PALINSESTO":
    colore_tema = "#eefae1"      # Sfondo Verde Vivo Soft
    colore_bordo = "#a3e2ab"     # Bordo Verde Vivo
elif st.session_state.tab_selezionata == "STORICO":
    colore_tema = "#f1effa"      # Sfondo Viola Regale Soft
    colore_bordo = "#c5bfe7"     # Bordo Viola Regale
else:
    colore_tema = "#fffde6"      # Sfondo Giallo Canarino Soft
    colore_bordo = "#f6eb9d"     # Bordo Giallo Canarino

# --- RESTYLING GRAFICO ULTRA-OTTIMIZZATO (VERSIONE 5.30) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {colore_tema} !important; transition: background-color 0.2s ease; }}
    
    .block-container {{ 
        padding-top: 3.5rem !important; 
        padding-bottom: 1rem !important; 
        padding-left: 0.5rem !important; 
        padding-right: 0.5rem !important; 
    }}
    
    .brand-box {{ text-align: center; margin-bottom: 12px; padding: 2px; }}
    .main-title {{ font-size: 22px; font-weight: 800; color: #1c1c1e; margin: 0; }}
    .version-label {{ font-size: 10px; font-weight: 700; color: #007aff; margin-top: 1px; text-transform: uppercase; letter-spacing: 0.5px; }}

    /* Pulsanti d'Azione Principali (Verticali) - Forzatura ID Streamlit per evitare inversioni */
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
    
    /* Aggancio diretto tramite ID univoco generato da Streamlit per i pulsanti verticali */
    div.stButton > button[id*="fase_1"] {{ background-color: #2cd158 !important; color: white !important; }}
    div.stButton > button[id*="fase_2"] {{ background-color: #6a5acd !important; color: white !important; }}
    div.stButton > button[id*="fase_3"] {{ background-color: #ffd700 !important; color: #1c1c1e !important; }}
    
    /* Pulsanti dei micro-tab inferiori */
    .tab-click-col div.stButton > button {{
        font-size: 10px !important;
        padding: 6px 2px !important;
        border-radius: 6px !important;
        border: 1px solid #d1d1d6 !important;
        text-transform: uppercase;
        letter-spacing: -0.3px;
    }}
    
    /* Card dei Match Uniformata al colore esatto della videata attiva */
    .match-card {{ 
        background-color: {colore_tema} !important; 
        padding: 12px; 
        border-radius: 14px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.04); 
        margin-bottom: 10px; 
        border: 1px solid {colore_bordo} !important; 
    }}
    
    .meta-label {{ color: #007aff; font-size: 9px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 2px; }}
    .team-text {{ font-size: 15px; font-weight: 700; color: #1c1c1e; margin: 2px 0 6px 0; letter-spacing: -0.3px; }}
    .score-badge {{ background-color: rgba(255,255,255,0.7); color: #1c1c1e; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 6px; display: inline-block; margin-bottom: 6px; border: 1px solid {colore_bordo}; }}
    
    .block-header {{ font-size: 10px; font-weight: 800; color: #007aff; text-transform: uppercase; margin: 2px 0 8px 0; letter-spacing: 0.4px; display: flex; align-items: center; }}
    .block-header.stats {{ color: #ff9500; }}

    .market-box {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 5px; }}
    .market-cell {{ background: rgba(255, 255, 255, 0.7); padding: 6px; border-radius: 6px; font-size: 11px; display: flex; flex-direction: column; justify-content: center; border: 1px solid {colore_bordo}; }}
    .market-cell b {{ color: #8e8e93; font-size: 9px; text-transform: uppercase; margin-bottom: 1px; }}
    .market-val-row {{ display: flex; justify-content: space-between; align-items: center; font-weight: 600; color: #1c1c1e; }}
    
    .win-badge {{ color: #34c759; font-weight: bold; font-size: 10px; background: #e8f9ee; padding: 1px 4px; border-radius: 3px; }}
    .lose-badge {{ color: #ff3b30; font-weight: bold; font-size: 10px; background: #ffebeb; padding: 1px 4px; border-radius: 3px; }}
    .wait-badge {{ color: #ff9500; font-weight: bold; font-size: 10px; background: #fff5e6; padding: 1px 4px; border-radius: 3px; }}
    
    .sub-title {{ font-size: 9px; font-weight: bold; color: #8e8e93; text-transform: uppercase; grid-column: span 2; margin-top: 4px; padding-top: 2px; border-top: 1px dashed {colore_bordo}; }}
    .match-separator {{ margin-bottom: 18px; border-bottom: 2px dotted {colore_bordo}; height: 1px; width: 100%; }}
    
    /* Box Accuratezza sempre leggibile */
    .accuracy-container {{ background: #ffffff; padding: 12px; border-radius: 14px; margin-top: 12px; margin-bottom: 14px; box-shadow: 0 3px 10px rgba(0,0,0,0.03); border: 1px solid #d1d1d6; }}
    .accuracy-title {{ font-size: 11px; font-weight: 800; color: #1c1c1e; text-transform: uppercase; margin-bottom: 8px; text-align: center; letter-spacing: 0.5px; }}
    .accuracy-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; }}
    .accuracy-item {{ background: #f8f9fa; padding: 6px 8px; border-radius: 8px; font-size: 11px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #e5e5ea; }}
    .accuracy-item span {{ color: #48484a; font-weight: 600; }}
    .accuracy-val {{ color: #34c759; font-weight: 800; font-size: 12px; }}
    
    .debug-badge {{ background: #3a3a3c; color: #ffffff; padding: 4px 8px; border-radius: 5px; font-family: monospace; font-size: 9px; display: block; text-align: center; margin-top: 10px; }}
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
        "DC+U/O 2.5": "Esito_DC+U/O2.5", "U/O 1.5": "Esito_U/O_1.5", "U/O 2.5": "Esito_U/O_2.5",
        "U/O 3.5": "Esito_U/O_3.5", "Goal/NoGoal": "Esito_Goal_NoGoal", "MG Casa": "Esito_Media_Goal_Casa",
        "MG Ospite": "Esito_Media_Goal_Trasferta", "MG Casa+Ospite": "Esito_Media_Goal_Totale",
        "Corner 1X2": "Esito_Corner_1X2"
    }
    accuratezza = {}
    for nome_m, col in mappa_esiti.items():
        if col in df_totale.columns:
            validi = df_totale[df_totale[col].isin(['VINCENTE', 'PERDENTE'])]
            if len(validi) > 0:
                vincenti = len(validi[validi[col] == 'VINCENTE'])
                accuratezza[nome_m] = f"{(vincenti / len(validi)) * 100:.1f}%"
            else: accuratezza[nome_m] = "0.0%"
        else: accuratezza[nome_m] = "N.D."
    return accuratezza

# Titolo Brand
st.markdown("""
<div class="brand-box">
    <div class="main-title">⚽ Betting Pro Mobile</div>
    <div class="version-label">Versione Progetto: 5.30</div>
</div>
""", unsafe_allow_html=True)

# --- I 3 PULSANTI VERTICALI DI AZIONE (CON KEY UNIVOCO E STRING-MATCHING) ---
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
            import modulo_04_allineatore as m4
            m4.esegui_allineamento()
            st.session_state.log_fase3 = datetime.datetime.now(FUSO_ROMA).strftime("%H:%M:%S")
            st.toast("🗄️ Database Sincronizzato!", icon="✅")
            st.rerun()
        except Exception as e: st.error(f"Errore: {str(e)}")

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# --- MICRO-TAB ORIZZONTALI COMPATTI PER IPHONE X ---
st.markdown("<div class='tab-click-col'>", unsafe_allow_html=True)
col_t1, col_t2, col_t3 = st.columns(3)

with col_t1:
    label_p1 = f"🎯 Palinsesto ({len(df_palinsesto)})"
    if st.session_state.tab_selezionata == "PALINSESTO":
        st.button(label_p1, key="btn_pal", help="Attivo", use_container_width=True)
    else:
        if st.button(label_p1, key="btn_pal_off", use_container_width=True):
            st.session_state.tab_selezionata = "PALINSESTO"
            st.rerun()

with col_t2:
    label_p2 = f"📊 Storico ({len(df_storico)})"
    if st.session_state.tab_selezionata == "STORICO":
        st.button(label_p2, key="btn_sto", help="Attivo", use_container_width=True)
    else:
        if st.button(label_p2, key="btn_sto_off", use_container_width=True):
            st.session_state.tab_selezionata = "STORICO"
            st.rerun()

with col_t3:
    label_p3 = f"🗄️ Database ({len(df_database)})"
    if st.session_state.tab_selezionata == "DATABASE":
        st.button(label_p3, key="btn_db", help="Attivo", use_container_width=True)
    else:
        if st.button(label_p3, key="btn_db_off", use_container_width=True):
            st.session_state.tab_selezionata = "DATABASE"
            st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# CSS dinamico per i micro-tab attivi sincronizzati
st.markdown(f"""
    <style>
    #button-btn_pal {{ background-color: #2cd158 !important; color: white !important; font-weight: 800 !important; }}
    #button-btn_sto {{ background-color: #6a5acd !important; color: white !important; font-weight: 800 !important; }}
    #button-btn_db {{ background-color: #ffd700 !important; color: #1c1c1e !important; font-weight: 800 !important; }}
    #button-btn_pal_off, #button-btn_sto_off, #button-btn_db_off {{ background-color: #ffffff !important; color: #1c1c1e !important; }}
    </style>
""", unsafe_allow_html=True)

# BOX ACCURATEZZA DIXON-COLES
dict_acc = calcola_accuratezza_globale()
if dict_acc:
    st.markdown("""
    <div class="accuracy-container">
        <div class="accuracy-title">📈 Accuratezza Algoritmo Dixon-Coles</div>
        <div class="accuracy-grid">
    """, unsafe_allow_html=True)
    for m_name, m_val in dict_acc.items():
        st.markdown(f'<div class="accuracy-item"><span>{m_name}</span><span class="accuracy-val">{m_val}</span></div>', unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

# --- RENDERING INTERFACCIA IN BASE ALLA SELEZIONE ---
if st.session_state.tab_selezionata == "PALINSESTO":
    if not df_palinsesto.empty:
        for idx, row in df_palinsesto.iterrows():
            def clean(val):
                if pd.isna(val) or val == "-": return "-"
                try:
                    f_val = float(val)
                    return str(int(f_val)) if f_val.is_integer() else str(f_val)
                except: return str(val)

            st.markdown(f"""
            <div class="match-card">
                <div class="meta-label">🏆 {row.get('Campionato', '-')} | {row.get('Data_Ora_Match', '-')}</div>
                <div class="team-text"> {row.get('3. Match', 'Match')}</div>
                <div class="block-header">🎲 Algoritmo & Probabilità</div>
                <div class="market-box">
                    <div class="market-cell"><b>1X2</b><div class="market-val-row">{row.get('1X2', '-')}</div></div>
                    <div class="market-cell"><b>Ris. Esatto</b><div class="market-val-row">{row.get('Risultato_Esatto', '-')}</div></div>
                    <div class="market-cell"><b>Doppia Chance</b><div class="market-val-row">{row.get('Doppia_Chance', '-')}</div></div>
                    <div class="market-cell"><b>Combo Combo</b><div class="market-val-row">{row.get('DC+U/O2.5', '-')}</div></div>
                    <div class="market-cell"><b>U/O 1.5</b><div class="market-val-row">{row.get('U/O_1.5', '-')}</div></div>
                    <div class="market-cell"><b>U/O 2.5</b><div class="market-val-row">{row.get('U/O_2.5', '-')}</div></div>
                    <div class="market-cell"><b>U/O 3.5</b><div class="market-val-row">{row.get('U/O_3.5', '-')}</div></div>
                    <div class="market-cell"><b>Goal/NoGoal</b><div class="market-val-row">{row.get('Goal_NoGoal', '-')}</div></div>
                    <div class="market-cell"><b>MG Casa Expect.</b><div class="market-val-row">{row.get('Pronostico_MG_Casa', '-')} GOL</div></div>
                    <div class="market-cell"><b>MG Ospite Expect.</b><div class="market-val-row">{row.get('Pronostico_MG_Trasferta', '-')} GOL</div></div>
                    <div class="market-cell"><b>MG Totale Expect.</b><div class="market-val-row">{row.get('Pronostico_MG_Totale', '-')} GOL</div></div>
                    <div class="market-cell"><b>Corner 1X2</b><div class="market-val-row">{row.get('Corner_1X2', '-')}</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="match-card">
                <div class="meta-label" style="color: #ff9500;">📊 STATISTICHE TEAM | LIVE DATA</div>
                <div class="team-text" style="font-size: 13px; color: #48484a;">{row.get('3. Match', 'Match')}</div>
                <div class="block-header stats">📊 Storico Stagionale (Casa vs Ospite)</div>
                <div class="market-box">
                    <div class="market-cell"><b>Pos. Classifica</b><div class="market-val-row"><span>{clean(row.get('PosClassifica_Casa'))}°</span><span>vs</span><span>{clean(row.get('PosClassifica_Ospite'))}°</span></div></div>
                    <div class="market-cell"><b>Punti Totali</b><div class="market-val-row"><span>{clean(row.get('Punti_Casa'))} pt</span><span>vs</span><span>{clean(row.get('Punti_Trasferta'))} pt</span></div></div>
                    <div class="market-cell"><b>Partite Giocate</b><div class="market-val-row"><span>{clean(row.get('Giocate_Casa'))} G</span><span>vs</span><span>{clean(row.get('Giocate_Ospite'))} G</span></div></div>
                    <div class="market-cell"><b>V / P / S</b><div class="market-val-row"><span>{clean(row.get('Vinte_Casa'))}-{clean(row.get('Pareggi_Casa'))}-{clean(row.get('Perse_Casa'))}</span><span>vs</span><span>{clean(row.get('Vinte_Ospite'))}-{clean(row.get('Pareggi_Ospite'))}-{clean(row.get('Perse_Ospite'))}</span></div></div>
                    <div class="market-cell"><b>Gol Fatti Totali</b><div class="market-val-row"><span>{clean(row.get('Media_Goal_Casa_Orig'))} F</span><span>vs</span><span>{clean(row.get('Media_Goal_Trasferta_Orig'))} F</span></div></div>
                    <div class="market-cell"><b>Gol Subiti Totali</b><div class="market-val-row"><span>{clean(row.get('Goal_Subiti_Casa'))} S</span><span>vs</span><span>{clean(row.get('Goal_Subiti_Ospite'))} S</span></div></div>
                </div>
            </div>
            <div class="match-separator"></div>
            """, unsafe_allow_html=True)
    else: st.info("Palinsesto vuoto.")

elif st.session_state.tab_selezionata == "STORICO":
    if not df_storico.empty:
        for idx, row in df_storico.iterrows():
            def badge_esito(col):
                val = str(row.get(col, '-')).strip().upper()
                if "VINCENTE" in val: return "<span class='win-badge'>VINC</span>"
                if "PERDENTE" in val: return "<span class='lose-badge'>PERS</span>"
                return "<span class='wait-badge'>ATT</span>"

            st.markdown(f"""
            <div class="match-card">
                <div class="meta-label">🏆 {row.get('Campionato', '-')} | {row.get('Data_Ora_Match', '-')}</div>
                <div class="team-text">{row.get('3. Match', 'Match')}</div>
                <div class="score-badge">⚽ Finale Reale: {row.get('Risultato_Reale', 'IN ATTESA')}</div>
                <div class="market-box" style="border-top: 1px dashed {colore_bordo}; padding-top: 6px;">
                    <div class="market-cell"><b>1X2</b><div class="market-val-row"><span>{row.get('1X2', '-')}</span>{badge_esito('Esito_1X2')}</div></div>
                    <div class="market-cell"><b>Esatto</b><div class="market-val-row"><span>{row.get('Risultato_Esatto', '-')}</span>{badge_esito('Esito_Risultato_Esatto')}</div></div>
                    <div class="market-cell"><b>Doppia</b><div class="market-val-row"><span>{row.get('Doppia_Chance', '-')}</span>{badge_esito('Esito_Doppia_Chance')}</div></div>
                    <div class="market-cell"><b>Combo Combo</b><div class="market-val-row"><span>{row.get('DC+U/O2.5', '-')}</span>{badge_esito('Esito_DC+U/O2.5')}</div></div>
                    <div class="market-cell"><b>U/O 1.5</b><div class="market-val-row"><span>{row.get('U/O_1.5', '-')}</span>{badge_esito('Esito_U/O_1.5')}</div></div>
                    <div class="market-cell"><b>U/O 2.5</b><div class="market-val-row"><span>{row.get('U/O_2.5', '-')}</span>{badge_esito('Esito_U/O_2.5')}</div></div>
                    <div class="market-cell"><b>U/O 3.5</b><div class="market-val-row"><span>{row.get('U/O_3.5', '-')}</span>{badge_esito('Esito_U/O_3.5')}</div></div>
                    <div class="market-cell"><b>G/NG</b><div class="market-val-row"><span>{row.get('Goal_NoGoal', '-')}</span>{badge_esito('Esito_Goal_NoGoal')}</div></div>
                    <div class="market-cell"><b>MG Casa</b><div class="market-val-row"><span>{row.get('Pronostico_MG_Casa', '-')}</span>{badge_esito('Esito_Media_Goal_Casa')}</div></div>
                    <div class="market-cell"><b>MG Ospite</b><div class="market-val-row"><span>{row.get('Pronostico_MG_Trasferta', '-')}</span>{badge_esito('Esito_Media_Goal_Trasferta')}</div></div>
                    <div class="market-cell"><b>MG C+O</b><div class="market-val-row"><span>{row.get('Pronostico_MG_Totale', '-')}</span>{badge_esito('Esito_Media_Goal_Totale')}</div></div>
                    <div class="market-cell"><b>Corner 1X2</b><div class="market-val-row"><span>{row.get('Corner_1X2', '-')}</span>{badge_esito('Esito_Corner_1X2')}</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else: st.info("Storico recente vuoto.")

elif st.session_state.tab_selezionata == "DATABASE":
    if not df_database.empty:
        for idx, row in df_database.iterrows():
            st.markdown(f"""
            <div class="match-card">
                <div class="meta-label">🏆 {row.get('Campionato', '-')} | {row.get('Data_Ora_Match', '-')}</div>
                <div class="team-text">{row.get('3. Match', 'Match')}</div>
                <div class="score-badge">⚽ Risultato: {row.get('Risultato_Reale', '-')}</div>
                <div class="market-box">
                    <div class="sub-title">Dati Statistici Archiviati</div>
                    <div class="market-cell"><b>Punti Casa</b><div class="market-val-row">{row.get('Punti_Casa', '-')}</div></div>
                    <div class="market-cell"><b>Punti Ospite</b><div class="market-val-row">{row.get('Punti_Trasferta', '-')}</div></div>
                    <div class="market-cell"><b>GF Casa</b><div class="market-val-row">{row.get('Media_Goal_Casa_Orig', row.get('Media_Goal_Casa', '-'))}</div></div>
                    <div class="market-cell"><b>GF Ospite</b><div class="market-val-row">{row.get('Media_Goal_Trasferta_Orig', row.get('Media_Goal_Trasferta', '-'))}</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Log di debug in fondo
st.markdown(f'<div class="debug-badge">iPhone X Colors Locked 5.30 | Active Tab: {st.session_state.tab_selezionata}</div>', unsafe_allow_html=True)
