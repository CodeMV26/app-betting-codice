import streamlit as st
import pandas as pd
import os

# Configurazione geometrica blindata per iPhone X (5.8") e iPhone 13 (6.1")
st.set_page_config(page_title="⚽ Betting Pro Mobile", page_icon="⚽", layout="centered")

# --- RESTYLING GRAFICO EMENDATO (VERSIONE 5.20) ---
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
    
    /* Titoli Sezioni Interne */
    .section-title { font-size: 10px; font-weight: 800; color: #ff9500; text-transform: uppercase; grid-column: span 2; margin: 6px 0 4px 0; padding-top: 4px; border-top: 1px dashed #e5e5ea; letter-spacing: 0.4px; }
    .section-title.prob { color: #007aff; }

    /* Griglia fissa a 2 Colonne */
    .market-box { display: grid; grid-template-columns: repeat(2, 1fr); gap: 5px; }
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

st.markdown("""
<div class="brand-box">
    <div class="main-title">⚽ Betting Pro Mobile</div>
    <div class="version-label">Versione Progetto: 5.20</div>
</div>
""", unsafe_allow_html=True)

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

# RENDERING SICURO E COMPLETO
if "🎯 Palinsesto" in opzione_tab:
    if not df_palinsesto.empty:
        for idx, row in df_palinsesto.iterrows():
            
            # Helper interno leggero per ripulire i numeri decimali o mancanti nelle statistiche
            def fmt(val):
                if pd.isna(val) or val == "-": return "0"
                if isinstance(val, float): return str(int(val)) if val.is_integer() else f"{val:.1f}"
                return str(val)

            st.markdown(f"""
            <div class="match-card">
                <div class="meta-label">🏆 {row.get('Campionato', '-')} | {row.get('Data_Ora_Match', '-')}</div>
                <div class="team-text"> {row.get('3. Match', 'Match')}</div>
                
                <div class="market-box">
                    <div class="section-title">📊 Statistiche Squadre (Casa vs Ospite)</div>
                    <div class="market-cell"><b>Pos. Classifica</b><div class="market-val-row"><span>{fmt(row.get('PosClassifica_Casa'))}°</span><span>vs</span><span>{fmt(row.get('PosClassifica_Ospite'))}°</span></div></div>
                    <div class="market-cell"><b>Punti Totali</b><div class="market-val-row"><span>{fmt(row.get('Punti_Casa'))} pt</span><span>vs</span><span>{fmt(row.get('Punti_Trasferta'))} pt</span></div></div>
                    <div class="market-cell"><b>Partite Giocate</b><div class="market-val-row"><span>{fmt(row.get('Giocate_Casa'))} G</span><span>vs</span><span>{fmt(row.get('Giocate_Ospite'))} G</span></div></div>
                    <div class="market-cell"><b>V / P / S</b><div class="market-val-row"><span>{fmt(row.get('Vinte_Casa'))}-{fmt(row.get('Pareggi_Casa'))}-{fmt(row.get('Perse_Casa'))}</span><span>vs</span><span>{fmt(row.get('Vinte_Ospite'))}-{fmt(row.get('Pareggi_Ospite'))}-{fmt(row.get('Perse_Ospite'))}</span></div></div>
                    <div class="market-cell"><b>Gol Fatti Totali</b><div class="market-val-row"><span>{fmt(row.get('Media_Goal_Casa_Orig'))} F</span><span>vs</span><span>{fmt(row.get('Media_Goal_Trasferta_Orig'))} F</span></div></div>
                    <div class="market-cell"><b>Gol Subiti Totali</b><div class="market-val-row"><span>{fmt(row.get('Goal_Subiti_Casa'))} S</span><span>vs</span><span>{fmt(row.get('Goal_Subiti_Ospite'))} S</span></div></div>
                    
                    <div class="section-title prob">🎲 Algoritmo & Probabilità</div>
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
