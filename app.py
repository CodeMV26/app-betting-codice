import streamlit as st
import pandas as pd
import os

# Configurazione geometrica blindata per iPhone X (5.8") e iPhone 13 (6.1")
st.set_page_config(page_title="⚽ Betting Pro Mobile", page_icon="⚽", layout="centered")

# --- RESTYLING GRAFICO PREMIUM LIVELLO APPLE IOS ---
st.markdown("""
    <style>
    /* Sfondo globale dell'applicazione */
    .stApp { background-color: #f2f2f7; }
    .block-container { padding-top: 0.5rem !important; padding-bottom: 1rem !important; padding-left: 0.6rem !important; padding-right: 0.6rem !important; }
    
    /* Intestazione principale */
    .main-title { font-size: 24px; font-weight: 800; color: #1c1c1e; text-align: center; margin-bottom: 12px; letter-spacing: -0.5px; }
    .section-title { font-size: 14px; font-weight: 700; color: #8e8e93; text-transform: uppercase; margin-bottom: 8px; padding-left: 4px; }

    /* Modifica stile nativo dei pulsanti Streamlit per renderli compatti e iOS-like */
    div.stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        padding: 10px !important;
        border: none !important;
        transition: all 0.2s ease;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
    }
    /* Colori specifici personalizzati per i 3 bottoni */
    div.stButton:nth-child(2) > button { background-color: #007aff !important; color: white !important; }
    div.stButton:nth-child(3) > button { background-color: #34c759 !important; color: white !important; }
    div.stButton:nth-child(4) > button { background-color: #ff9500 !important; color: white !important; }
    
    /* Box Accuratezza Algoritmo Premium */
    .accuracy-container { background: #1c1c1e; padding: 14px; border-radius: 16px; margin-bottom: 16px; box-shadow: 0 8px 20px rgba(0,0,0,0.15); }
    .accuracy-title { font-size: 12px; font-weight: 800; color: #34c759; text-transform: uppercase; margin-bottom: 10px; text-align: center; letter-spacing: 0.5px; }
    .accuracy-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
    .accuracy-item { background: #2c2c2e; padding: 8px 10px; border-radius: 8px; font-size: 12px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #3a3a3c; }
    .accuracy-item span { color: #aeaeae; font-weight: 500; }
    .accuracy-val { color: #30d158; font-weight: 700; font-family: monospace; font-size: 13px; }
    
    /* Card dei Match Evoluta */
    .match-card { background-color: #ffffff; padding: 14px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.03); margin-bottom: 12px; border: 1px solid #e5e5ea; }
    .meta-label { color: #007aff; font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.3px; margin-bottom: 4px; }
    .team-text { font-size: 16px; font-weight: 700; color: #1c1c1e; margin: 2px 0 8px 0; letter-spacing: -0.3px; }
    .score-badge { background-color: #f2f2f7; color: #1c1c1e; font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 8px; display: inline-block; margin-bottom: 8px; border: 1px solid #e5e5ea; }
    
    /* Griglia Mercati Pulita e Allineata */
    .market-box { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; border-top: 1px dashed #e5e5ea; padding-top: 8px; }
    .market-cell { background: #f8f9fa; padding: 8px; border-radius: 8px; font-size: 12px; display: flex; flex-direction: column; justify-content: center; border: 1px solid #f2f2f7; }
    .market-cell b { color: #8e8e93; font-size: 10px; text-transform: uppercase; margin-bottom: 2px; }
    .market-val-row { display: flex; justify-content: space-between; align-items: center; font-weight: 600; color: #1c1c1e; }
    
    /* Indicatori Esito Minimalisti */
    .win-badge { color: #34c759; font-weight: bold; font-size: 11px; background: #e8f9ee; padding: 2px 6px; border-radius: 4px; }
    .lose-badge { color: #ff3b30; font-weight: bold; font-size: 11px; background: #ffebeb; padding: 2px 6px; border-radius: 4px; }
    .wait-badge { color: #ff9500; font-weight: bold; font-size: 11px; background: #fff5e6; padding: 2px 6px; border-radius: 4px; }
    
    .sub-title { font-size: 10px; font-weight: bold; color: #8e8e93; text-transform: uppercase; grid-column: span 2; margin-top: 6px; padding-top: 4px; border-top: 1px solid #f2f2f7; }
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
        "MG Ospite": "Esito_Media_Goal_Trasferta"
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

st.markdown('<div class="main-title">⚽ Betting Pro Mobile</div>', unsafe_allow_html=True)

# --- PANNELLO DI CONTROLLO A TRE FASI CONFIGURATO DAL DIRETTORE ---
st.markdown('<div class="section-title">🎛️ Pannello Operativo</div>', unsafe_allow_html=True)

if st.button("🚀 FASE 1: Estrattore Totale & Pronostici", use_container_width=True):
    with st.spinner("⏳ Fase 1 in corso..."):
        try:
            import modulo_01_estrattore as m1
            import modulo_02_motore as m2
            m1.esegui_estrazione()
            m2.esegui_calcolo_motore()
            st.success("✅ Palinsesto Attivo pronto!")
            st.rerun()
        except Exception as e: st.error(f"Errore: {str(e)}")

if st.button("🏆 FASE 2: Convalida Risultati Reali", use_container_width=True):
    with st.spinner("⏳ Fase 2 in corso..."):
        try:
            import modulo_03_validatore as m3
            m3.esegui_validazione()
            st.success("✅ Storico aggiornato!")
            st.rerun()
        except Exception as e: st.error(f"Errore: {str(e)}")

if st.button("🗄️ FASE 3: Archiviazione Completa", use_container_width=True):
    with st.spinner("⏳ Fase 3 in corso..."):
        try:
            import modulo_04_allineatore as m4
            m4.esegui_allineamento()
            st.success("✅ Archiviato nel Database Totale!")
            st.rerun()
        except Exception as e: st.error(f"Errore: {str(e)}")

st.markdown("<br>", unsafe_allow_html=True)

# SELETTORE SCHERMATA COMPATTO
opzione_tab = st.selectbox("📂 Visualizza File:", [
    f"🎯 Palinsesto Attivo ({len(df_palinsesto)})", 
    f"📊 Storico Convalidato ({len(df_storico)})", 
    f"🗄️ Database Totale ({len(df_database)})"
], label_visibility="collapsed")

# BLOCCO ACCURATEZZA IN TEMPO REALE
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

# ----------------- RENDERING DELLE SCHEDE INTERNE -----------------
if "🎯 Palinsesto" in opzione_tab:
    if not df_palinsesto.empty:
        for idx, row in df_palinsesto.iterrows():
            st.markdown(f"""
            <div class="match-card">
                <div class="meta-label">🏆 {row.get('Campionato', '-')} | {row.get('Data_Ora_Match', '-')}</div>
                <div class="team-text"> {row.get('3. Match', 'Match')}</div>
                <div class="market-box">
                    <div class="market-cell"><b>1X2</b><div class="market-val-row">{row.get('1X2', '-')}</div></div>
                    <div class="market-cell"><b>Ris. Esatto</b><div class="market-val-row">{row.get('Risultato_Esatto', '-')}</div></div>
                    <div class="market-cell"><b>Doppia Chance</b><div class="market-val-row">{row.get('Doppia_Chance', '-')}</div></div>
                    <div class="market-cell"><b>Combo DC+U/O</b><div class="market-val-row">{row.get('DC+U/O2.5', '-')}</div></div>
                    <div class="market-cell"><b>U/O 1.5</b><div class="market-val-row">{row.get('U/O_1.5', '-')}</div></div>
                    <div class="market-cell"><b>U/O 2.5</b><div class="market-val-row">{row.get('U/O_2.5', '-')}</div></div>
                    <div class="market-cell"><b>U/O 3.5</b><div class="market-val-row">{row.get('U/O_3.5', '-')}</div></div>
                    <div class="market-cell"><b>Goal/NoGoal</b><div class="market-val-row">{row.get('Goal_NoGoal', '-')}</div></div>
                    <div class="market-cell"><b>MG Casa</b><div class="market-val-row">{row.get('Pronostico_MG_Casa', '-')}</div></div>
                    <div class="market-cell"><b>MG Ospite</b><div class="market-val-row">{row.get('Pronostico_MG_Trasferta', '-')}</div></div>
                    <div class="market-cell"><b>Corner 1X2</b><div class="market-val-row">{row.get('Corner_1X2', '-')}</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else: st.info("Palinsesto vuoto.")

elif "📊 Storico" in opzione_tab:
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
                <div class="market-box">
                    <div class="market-cell"><b>1X2</b><div class="market-val-row"><span>{row.get('1X2', '-')}</span>{badge_esito('Esito_1X2')}</div></div>
                    <div class="market-cell"><b>Esatto</b><div class="market-val-row"><span>{row.get('Risultato_Esatto', '-')}</span>{badge_esito('Esito_Risultato_Esatto')}</div></div>
                    <div class="market-cell"><b>Doppia</b><div class="market-val-row"><span>{row.get('Doppia_Chance', '-')}</span>{badge_esito('Esito_Doppia_Chance')}</div></div>
                    <div class="market-cell"><b>Combo</b><div class="market-val-row"><span>{row.get('DC+U/O2.5', '-')}</span>{badge_esito('Esito_DC+U/O2.5')}</div></div>
                    <div class="market-cell"><b>U/O 1.5</b><div class="market-val-row"><span>{row.get('U/O_1.5', '-')}</span>{badge_esito('Esito_U/O_1.5')}</div></div>
                    <div class="market-cell"><b>U/O 2.5</b><div class="market-val-row"><span>{row.get('U/O_2.5', '-')}</span>{badge_esito('Esito_U/O_2.5')}</div></div>
                    <div class="market-cell"><b>U/O 3.5</b><div class="market-val-row"><span>{row.get('U/O_3.5', '-')}</span>{badge_esito('Esito_U/O_3.5')}</div></div>
                    <div class="market-cell"><b>G/NG</b><div class="market-val-row"><span>{row.get('Goal_NoGoal', '-')}</span>{badge_esito('Esito_Goal_NoGoal')}</div></div>
                    <div class="market-cell"><b>MG Casa</b><div class="market-val-row"><span>{row.get('Pronostico_MG_Casa', '-')}</span>{badge_esito('Esito_Media_Goal_Casa')}</div></div>
                    <div class="market-cell"><b>MG Ospite</b><div class="market-val-row"><span>{row.get('Pronostico_MG_Trasferta', '-')}</span>{badge_esito('Esito_Media_Goal_Trasferta')}</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else: st.info("Storico recente vuoto.")

elif "🗄️ Database" in opzione_tab:
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
