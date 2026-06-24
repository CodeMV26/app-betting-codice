import streamlit as st
import pandas as pd
import os

# Configurazione geometrica bloccata per iPhone X (5.8") e iPhone 13 (6.1")
st.set_page_config(page_title="⚽ Betting Pro Mobile", page_icon="⚽", layout="centered")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; padding-left: 0.7rem !important; padding-right: 0.7rem !important; }
    .match-card { background-color: #ffffff; padding: 12px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 12px; border-left: 5px solid #007aff; }
    .card-storico { border-left-color: #34c759; }
    .card-database { border-left-color: #ff9500; }
    .meta-label { color: #8e8e93; font-size: 11px; font-weight: bold; text-transform: uppercase; }
    .team-text { font-size: 15px; font-weight: bold; color: #1c1c1e; margin: 4px 0; }
    .score-badge { background-color: #e5e5ea; color: #1c1c1e; font-size: 12px; font-weight: bold; padding: 3px 8px; border-radius: 5px; display: inline-block; margin: 4px 0; }
    
    .market-box { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; margin-top: 8px; }
    .market-cell { background: #f8f9fa; padding: 6px; border-radius: 6px; border: 1px solid #efeff4; font-size: 12px; }
    .market-cell b { color: #48484a; }
    
    .win-text { color: #34c759; font-weight: bold; font-size: 11px; }
    .lose-text { color: #ff3b30; font-weight: bold; font-size: 11px; }
    .wait-text { color: #ff9500; font-weight: bold; font-size: 11px; }
    
    /* Box accuratezza mercati - Mobile First */
    .accuracy-container { background: #1c1c1e; color: #ffffff; padding: 12px; border-radius: 10px; margin-bottom: 16px; }
    .accuracy-title { font-size: 13px; font-weight: bold; color: #34c759; text-transform: uppercase; margin-bottom: 8px; text-align: center; }
    .accuracy-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; }
    .accuracy-item { background: #2c2c2e; padding: 6px; border-radius: 6px; font-size: 11px; display: flex; justify-content: space-between; }
    .accuracy-val { color: #34c759; font-weight: bold; }
    
    .sub-title { font-size: 10px; font-weight: bold; color: #007aff; text-transform: uppercase; grid-column: span 2; margin-top: 4px; border-bottom: 1px solid #e5e5ea; }
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

# Funzione per calcolare l'accuratezza reale unificata (Storico + Database) sui 12 mercati
def calcola_accuratezza_globale():
    frames = []
    if not df_storico.empty: frames.append(df_storico)
    if not df_database.empty: frames.append(df_database)
    if not frames: return {}
    
    df_totale = pd.concat(frames, ignore_index=True)
    mappa_esiti = {
        "1X2": "Esito_1X2", "Ris. Esatto": "Esito_Risultato_Esatto", "Doppia Chance": "Esito_Doppia_Chance",
        "DC+U/O 2.5": "Esito_DC+U/O2.5", "Under/Over 1.5": "Esito_U/O_1.5", "Under/Over 2.5": "Esito_U/O_2.5",
        "Under/Over 3.5": "Esito_U/O_3.5", "Goal/NoGoal": "Esito_Goal_NoGoal", "MG Casa": "Esito_Media_Goal_Casa",
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

st.title("⚽ Betting Pro Mobile")

# --- PANNELLO DI CONTROLLO A TRE FASI CONFIGURATO DAL DIRETTORE ---
st.markdown("### 🎛️ Pannello di Controllo Operativo")

if st.button("🚀 AVVIA FASE 1: Estrazione Integrale + Pronostici Dixon-Coles", use_container_width=True):
    with st.spinner("⏳ Estrazione totale statistiche API e calcolo in corso..."):
        try:
            import modulo_01_estrattore as m1
            import modulo_02_motore as m2
            m1.esegui_estrazione() # Scarica TUTTI i parametri statistici disponibili
            m2.esegui_calcolo_motore() # Associa i 12 mercati alle schede
            st.success("✅ FASE 1 Completata! Palinsesto Attivo generato.")
            st.rerun()
        except Exception as e: st.error(f"Errore Fase 1: {str(e)}")

if st.button("🏆 AVVIA FASE 2: Validazione Esiti Risultati Reali", use_container_width=True):
    with st.spinner("⏳ Verifica risultati su API e calcolo accuratezza mercati..."):
        try:
            import modulo_03_validatore as m3
            m3.esegui_validazione() # Valida ed esegui i calcoli di precisione accurati
            st.success("✅ FASE 2 Completata! Esiti aggiornati nello Storico Convalidato.")
            st.rerun()
        except Exception as e: st.error(f"Errore Fase 2: {str(e)}")

if st.button("🗄️ AVVIA FASE 3: Archiviazione Definitiva nel Database Totale", use_container_width=True):
    with st.spinner("⏳ Scrittura protetta e consolidamento storico in corso..."):
        try:
            import modulo_04_allineatore as m4
            m4.esegui_allineamento() # Copia i match terminati con statistiche iniziali intatte
            st.success("✅ FASE 3 Completata! Database Storico Totale alimentato e salvato.")
            st.rerun()
        except Exception as e: st.error(f"Errore Fase 3: {str(e)}")

st.markdown("---")

opzione_tab = st.selectbox("📂 Seleziona Schermata:", [
    f"🎯 Palinsesto Attivo ({len(df_palinsesto)})", 
    f"📊 Storico Convalidato ({len(df_storico)})", 
    f"🗄️ Database Totale ({len(df_database)})"
])

# VISUALIZZAZIONE ACCURATEZZA DEI MERCATI IN TEMPO REALE SUL DISPLAY
dict_acc = calcola_accuratezza_globale()
if dict_acc:
    st.markdown("""
    <div class="accuracy-container">
        <div class="accuracy-title">📈 Accuratezza Algoritmo sui Match Terminati</div>
        <div class="accuracy-grid">
    """, unsafe_allow_html=True)
    for m_name, m_val in dict_acc.items():
        st.markdown(f'<div class="accuracy-item"><span>{m_name}:</span><span class="accuracy-val">{m_val}</span></div>', unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

# ----------------- FILTRI VISUALIZZAZIONE SCHEDE -----------------
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
                    <div class="market-cell"><b>Corner 1X2:</b> {row.get('Corner_1X2', '-')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else: st.info("Nessun match presente in palinsesto.")

elif "📊 Storico" in opzione_tab:
    if not df_storico.empty:
        for idx, row in df_storico.iterrows():
            def badge_esito(col):
                val = str(row.get(col, '-')).strip().upper()
                if "VINCENTE" in val: return "<span class='win-text'>[✅]</span>"
                if "PERDENTE" in val: return "<span class='lose-text'>[❌]</span>"
                return "<span class='wait-text'>[⏳]</span>"

            st.markdown(f"""
            <div class="match-card card-storico">
                <div class="meta-label">🏆 {row.get('Campionato', '-')} | {row.get('Data_Ora_Match', '-')}</div>
                <div class="team-text">{row.get('3. Match', 'Match')}</div>
                <div class="score-badge">⚽ Finale Reale: {row.get('Risultato_Reale', 'IN ATTESA')}</div>
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
    else: st.info("Nessun match convalidato nello storico recente.")

elif "🗄️ Database Totale" in opzione_tab:
    if not df_database.empty:
        for idx, row in df_database.iterrows():
            st.markdown(f"""
            <div class="match-card card-database">
                <div class="meta-label">🏆 {row.get('Campionato', '-')} | {row.get('Data_Ora_Match', '-')}</div>
                <div class="team-text">{row.get('3. Match', 'Match')}</div>
                <div class="score-badge">⚽ Risultato: {row.get('Risultato_Reale', '-')}</div>
                <div class="market-box">
                    <div class="sub-title">Dati Statistici Archiviati</div>
                    <div class="market-cell"><b>Punti Casa:</b> {row.get('Punti_Casa', '-')}</div>
                    <div class="market-cell"><b>Punti Ospite:</b> {row.get('Punti_Trasferta', '-')}</div>
                    <div class="market-cell"><b>GF Casa:</b> {row.get('Media_Goal_Casa_Orig', row.get('Media_Goal_Casa', '-'))}</div>
                    <div class="market-cell"><b>GF Ospite:</b> {row.get('Media_Goal_Trasferta_Orig', row.get('Media_Goal_Trasferta', '-'))}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
