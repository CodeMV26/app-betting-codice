import streamlit as st
import pandas as pd
import os

# Configurazione geometrica blindata per iPhone X (5.8") e iPhone 13 (6.1")
st.set_page_config(page_title="⚽ Betting Pro Mobile", page_icon="⚽", layout="centered")

# --- RESTYLING GRAFICO EMENDATO (VERSIONE 4.4) ---
st.markdown("""
    <style>
    .stApp { background-color: #f2f2f7; }
    
    /* Spostamento verso il basso per evitare la barra 'Share' nativa di Streamlit su iPhone */
    .block-container { 
        padding-top: 3.5rem !important; 
        padding-bottom: 1rem !important; 
        padding-left: 0.6rem !important; 
        padding-right: 0.6rem !important; 
    }
    
    /* Intestazione Brand */
    .brand-box { text-align: center; margin-bottom: 10px; padding: 2px; }
    .main-title { font-size: 22px; font-weight: 800; color: #1c1c1e; margin: 0; }
    .version-label { font-size: 10px; font-weight: 700; color: #007aff; margin-top: 1px; text-transform: uppercase; letter-spacing: 0.5px; }

    /* Pulsanti d'Azione Ultra-Compatti e meno invadenti (Micro-iOS) */
    div.stButton > button {
        border-radius: 8px !important;
        font-weight: 700 !important;
        font-size: 11px !important;
        padding: 6px 10px !important;
        height: auto !important;
        width: 100% !important;
        border: none !important;
        transition: all 0.2s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03) !important;
        margin-bottom: -4px !important;
    }
    div.stButton:nth-child(1) > button { background-color: #007aff !important; color: white !important; }
    div.stButton:nth-child(2) > button { background-color: #34c759 !important; color: white !important; }
    div.stButton:nth-child(3) > button { background-color: #5856d6 !important; color: white !important; }
    
    /* Box Accuratezza Azzurro Soft */
    .accuracy-container { background: #e1f5fe; padding: 12px; border-radius: 14px; margin-top: 10px; margin-bottom: 14px; box-shadow: 0 3px 10px rgba(0,122,255,0.06); border: 1px solid #b3e5fc; }
    .accuracy-title { font-size: 11px; font-weight: 800; color: #0288d1; text-transform: uppercase; margin-bottom: 8px; text-align: center; letter-spacing: 0.5px; }
    .accuracy-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; }
    .accuracy-item { background: #ffffff; padding: 6px 8px; border-radius: 8px; font-size: 11px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #e1f5fe; }
    .accuracy-item span { color: #48484a; font-weight: 600; }
    .accuracy-val { color: #34c759; font-weight: 800; font-size: 12px; }
    
    /* Card dei Match */
    .match-card { background-color: #ffffff; padding: 12px; border-radius: 14px; box-shadow: 0 3px 10px rgba(0,0,0,0.01); margin-bottom: 10px; border: 1px solid #e5e5ea; }
    .meta-label { color: #007aff; font-size: 9px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 2px; }
    .team-text { font-size: 15px; font-weight: 700; color: #1c1c1e; margin: 2px 0 6px 0; letter-spacing: -0.3px; }
    .score-badge { background-color: #f2f2f7; color: #1c1c1e; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 6px; display: inline-block; margin-bottom: 6px; border: 1px solid #e5e5ea; }
    
    /* Griglia Mercati fissa a 2 Colonne */
    .market-box { display: grid; grid-template-columns: repeat(2, 1fr); gap: 5px; border-top: 1px dashed #e5e5ea; padding-top: 6px; }
    .market-cell { background: #f8f9fa; padding: 6px; border-radius: 6px; font-size: 11px; display: flex; flex-direction: column; justify-content: center; border: 1px solid #f2f2f7; }
    .market-cell b { color: #8e8e93; font-size: 9px; text-transform: uppercase; margin-bottom: 1px; }
    .market-val-row { display: flex; justify-content: space-between; align-items: center; font-weight: 600; color: #1c1c1e; }
    
    .win-badge { color: #34c759; font-weight: bold; font-size: 10px; background: #e8f9ee; padding: 1px 4px; border-radius: 3px; }
    .lose-badge { color: #ff3b30; font-weight: bold; font-size: 10px; background: #ffebeb; padding: 1px 4px; border-radius: 3px; }
    .wait-badge { color: #ff9500; font-weight: bold; font-size: 10px; background: #fff5e6; padding: 1px 4px; border-radius: 3px; }
    
    .sub-title { font-size: 9px; font-weight: bold; color: #8e8e93; text-transform: uppercase; grid-column: span 2; margin-top: 4px; padding-top: 2px; border-top: 1px solid #f2f2f7; }
    </style>
""", unsafe_allow_html=True)

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

# Intestazione Spinta in basso via CSS - Visibilità Garantita
st.markdown("""
<div class="brand-box">
    <div class="main-title">⚽ Betting Pro Mobile</div>
    <div class="version-label">Versione Progetto: 4.4</div>
</div>
""", unsafe_allow_html=True)

# --- I 3 PULSANTI IN VERSIONE MICRO-IOS (ULTRA COMPATTI) ---
if st.button("🚀 FASE 1: Estrazione & Pronostici", use_container_width=True):
    with st.spinner("⏳ Elaborazione..."):
        try:
            import modulo_01_estrattore as m1
            import modulo_02_motore as m2
            m1.esegui_estrazione()
            m2.esegui_calcolo_motore()
            st.success("✅ Palinsesto Pronto!")
            st.rerun()
        except Exception as e: st.error(f"Errore: {str(e)}")

if st.button("🏆 FASE 2: Convalida Risultati", use_container_width=True):
    with st.spinner("⏳ Elaborazione..."):
        try:
            import modulo_03_validatore as m3
            m3.esegui_validazione()
            st.success("✅ Storico Aggiornato!")
            st.rerun()
        except Exception as e: st.error(f"Errore: {str(e)}")

if st.button("🗄️ FASE 3: Archiviazione Totale", use_container_width=True):
    with st.spinner("⏳ Elaborazione..."):
        try:
            import modulo_04_allineatore as m4
            m4.esegui_allineamento()
            st.success("✅ Database Consolidato!")
            st.rerun()
        except Exception as e: st.error(f"Errore: {str(e)}")

st.markdown("<br>", unsafe_allow_html=True)

opzione_tab = st.selectbox("📂 Visualizza File:", [
    f"🎯 Palinsesto Attivo ({len(df_palinsesto)})", 
    f"📊 Storico Convalidato ({len(df_storico)})", 
    f"🗄️ Database Totale ({len(df_database)})"
], label_visibility="collapsed")
