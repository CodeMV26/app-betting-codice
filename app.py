import streamlit as st
import pandas as pd
import os

# Configurazione geometrica blindata per iPhone X (5.8") e iPhone 13 (6.1")
st.set_page_config(page_title="⚽ Betting Pro Mobile", page_icon="⚽", layout="centered")

# --- RESTYLING GRAFICO EMENDATO ---
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

/* Pulsanti d'Azione Ultra-Compatti (Micro-iOS) */
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
    margin-bottom: 4px !important;
}
div.stButton:nth-child(1) > button { background-color: #007aff !important; color: white !important; }
div.stButton:nth-child(2) > button { background-color: #34c759 !important; color: white !important; }
div.stButton:nth-child(3) > button { background-color: #5856d6 !important; color: white !important; }

/* Box Accuratezza Azzurro Soft */
.accuracy-container { background: #e1f5fe; padding: 12px; border-radius: 14px; margin-top: 10px; margin-bottom: 14px; border: 1px solid #b3e5fc; }
.accuracy-title { font-size: 11px; font-weight: 800; color: #0288d1; text-transform: uppercase; margin-bottom: 8px; text-align: center; letter-spacing: 0.5px; }
.accuracy-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; }
.accuracy-item { background: #ffffff; padding: 6px 8px; border-radius: 8px; font-size: 11px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #e1f5fe; }
.accuracy-item span { color: #48484a; font-weight: 600; }
.accuracy-val { color: #34c759; font-weight: 800; font-size: 12px; }

/* Card dei Match */
.match-card { background-color: #ffffff; padding: 12px; border-radius: 14px; box-shadow: 0 3px 10px rgba(0,0,0,0.01); margin-bottom: 10px; border: 1px solid #e5e5ea; }
.meta-label { color: #007aff; font-size: 9px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 2px; }
.team-text { font-size: 15px; font-weight: 700; color: #1c1c1e; margin: 2px 0 6px 0; letter-spacing: -0.3px; }

/* Griglia Mercati fissa a 2 Colonne */
.market-box { display: grid; grid-template-columns: repeat(2, 1fr); gap: 5px; border-top: 1px dashed #e5e5ea; padding-top: 6px; }
.market-cell { background: #f8f9fa; padding: 6px; border-radius: 6px; font-size: 11px; display: flex; flex-direction: column; justify-content: center; border: 1px solid #f2f2f7; }
.market-cell b { color: #8e8e93; font-size: 9px; text-transform: uppercase; margin-bottom: 1px; }
.market-val-row { display: flex; justify-content: space-between; align-items: center; font-weight: 600; color: #1c1c1e; }
</style>
""", unsafe_allow_html=True)

DB_FILE = "Database_Storico_Completo.xlsx"
STORICO_FILE = "Storico_Validato_Betting.xlsx"
PALINSESTO_FILE = "Pronostici_App_Betting.xlsx"

@st.cache_data(ttl=2)
def carica_dati(path):
    if os.path.exists(path):
        try:
            return pd.read_excel(path)
        except:
            return pd.DataFrame()
    return pd.DataFrame()

df_palinsesto = carica_dati(PALINSESTO_FILE)
df_storico = carica_dati(STORICO_FILE)
df_database = carica_dati(DB_FILE)

def safe_get(row, col_name, default="-"):
    if col_name in row and pd.notna(row[col_name]):
        return str(row[col_name])
    return default

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
        "MG Ospite": "Esito_Media_Goal_Trasferta", "Corner 1X2": "Esito_Corner_1X2"
    }
    
    accuratezza = {}
    for nome_m, col in mappa_esiti.items():
        if col in df_totale.columns:
            validi = df_totale[df_totale[col].isin(['VINCENTE', 'PERDENTE'])]
            if len(validi) > 0:
                vincenti = len(validi[validi[col] == 'VINCENTE'])
                accuratezza[nome_m] = f"{(vincenti / len(validi)) * 100:.1f}%"
            else:
                accuratezza[nome_m] = "0.0%"
        else:
            accuratezza[nome_m] = "N.D."
    return accuratezza

# Intestazione Visiva
st.markdown("""
<div class="brand-box">
    <div class="main-title">⚽ Betting Pro Mobile</div>
    <div class="version-label">Versione Progetto: 6.36</div>
</div>
""", unsafe_allow_html=True)

# --- PANEL PULSANTI AZIONE (I 3 TRIGGER DELLE ACTIONS) ---
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🚀 PRE-MATCH", use_container_width=True):
        st.info("Avvia l'azione '1. Fase Pre-Match' direttamente su GitHub Actions per aggiornare i pronostici.")
with col2:
    if st.button("🏆 POST-MATCH", use_container_width=True):
        st.info("Avvia l'azione '2. Fase Post-Match' su GitHub Actions per convalidare i risultati reali.")
with col3:
    if st.button("🔄 REFRESH", use_container_width=True):
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Box Accuratezza
dict_acc = calcola_accuratezza_globale()
if dict_acc:
    st.markdown('<div class="accuracy-container"><div class="accuracy-title">📈 Accuratezza Algoritmo Dixon-Coles</div><div class="accuracy-grid">', unsafe_allow_html=True)
    for m_name, m_val in dict_acc.items():
        st.markdown(f'<div class="accuracy-item"><span>{m_name}</span><span class="accuracy-val">{m_val}</span></div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

# Opzione Tab di Visualizzazione
opzione_tab = st.selectbox("Seleziona File da Visualizzare:", [
    f"🎯 Palinsesto Attivo ({len(df_palinsesto)})",
    f"📊 Storico Convalidato ({len(df_storico)})",
    f"🗄️ Database Totale ({len(df_database)})"
], label_visibility="collapsed")

# RENDERING DEI MATCH
if "Palinsesto" in opzione_tab:
    if not df_palinsesto.empty:
        for idx, row in df_palinsesto.iterrows():
            st.markdown(f"""
            <div class="match-card">
                <div class="meta-label">🏆 {safe_get(row, 'Campionato')} | {safe_get(row, 'Data_Ora_Match')}</div>
                <div class="team-text">{safe_get(row, '3. Match')}</div>
                <div class="market-box">
                    <div class="market-cell"><b>1X2</b><div class="market-val-row">{safe_get(row, '1X2')}</div></div>
                    <div class="market-cell"><b>Ris. Esatto</b><div class="market-val-row">{safe_get(row, 'Risultato_Esatto')}</div></div>
                    <div class="market-cell"><b>Doppia Chance</b><div class="market-val-row">{safe_get(row, 'Doppia_Chance')}</div></div>
                    <div class="market-cell"><b>Combo DC+U/O 2.5</b><div class="market-val-row">{safe_get(row, 'DC+U/O2.5')}</div></div>
                    <div class="market-cell"><b>U/O 1.5</b><div class="market-val-row">{safe_get(row, 'U/O_1.5')}</div></div>
                    <div class="market-cell"><b>U/O 2.5</b><div class="market-val-row">{safe_get(row, 'U/O_2.5')}</div></div>
                    <div class="market-cell"><b>U/O 3.5</b><div class="market-val-row">{safe_get(row, 'U/O_3.5')}</div></div>
                    <div class="market-cell"><b>Goal/NoGoal</b><div class="market-val-row">{safe_get(row, 'Goal_NoGoal')}</div></div>
                    <div class="market-cell"><b>MG Casa</b><div class="market-val-row">{safe_get(row, 'Pronostico_MG_Casa')}</div></div>
                    <div class="market-cell"><b>MG Ospite</b><div class="market-val-row">{safe_get(row, 'Pronostico_MG_Trasferta')}</div></div>
                    <div class="market-cell"><b>Corner 1X2</b><div class="market-val-row">{safe_get(row, 'Corner_1X2')}</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nessun match presente in palinsesto.")
else:
    st.info("Visualizzazione Storico/Database disponibile. Nessun record da validare al momento.")
