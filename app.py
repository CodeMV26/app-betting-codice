import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime

st.set_page_config(page_title="Pannello Betting", page_icon="⚽", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f2f2f7; }
    .card, .card-storico, .card-database { background-color: white; padding: 14px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); margin-bottom: 14px; }
    .card { border-left: 5px solid #007aff; }
    .card-storico { border-left: 5px solid #34c759; }
    .card-database { border-left: 5px solid #ff9500; }
    .time-label { color: #8e8e93; font-size: 11px; font-weight: bold; }
    .update-label { color: #8e8e93; font-size: 13px; margin-bottom: 15px; font-style: italic; }
    .result-label { color: #1c1c1e; font-size: 14px; font-weight: bold; margin: 6px 0; background: #e5e5ea; padding: 4px 8px; border-radius: 6px; display: inline-block; }
    .market-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-top: 10px; font-size: 13px; }
    .market-item { background: #f8f9fa; padding: 6px 10px; border-radius: 6px; border: 1px solid #efeff4; }
    .esito-vincente { color: #34c759; font-weight: bold; }
    .esito-perdente { color: #ff3b30; font-weight: bold; }
    .section-title { font-size: 11px; font-weight: bold; color: #ff9500; text-transform: uppercase; margin-top: 8px; margin-bottom: 4px; grid-column: span 2; border-bottom: 1px solid #efeff4; padding-bottom: 2px; }
    .accuracy-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 12px; }
    .accuracy-card { background: #ffffff; border: 1px solid #e5e5ea; padding: 10px 12px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; }
    .accuracy-market { font-weight: 600; color: #1c1c1e; font-size: 13px; }
    .accuracy-value { background: #007aff; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; }
    .accuracy-value-nd { background: #8e8e93; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

TOKEN = st.secrets.get("GITHUB_TOKEN", "")
REPO = st.secrets.get("GITHUB_REPO", "")

st.title("⚽ Controllo Betting Pro")

if os.path.exists("Pronostici_App_Betting.xlsx"):
    mtime = os.path.getmtime("Pronostici_App_Betting.xlsx")
    data_ora = datetime.fromtimestamp(mtime).strftime('%d/%m/%Y %H:%M:%S')
    st.markdown(f"<div class='update-label'>🔄 Ultimo aggiornamento dati: {data_ora}</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='update-label'>🔄 Ultimo aggiornamento dati: Non disponibile</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("🚀 Avvia Fase 1 (Pre-Match)"):
        if TOKEN and REPO: requests.post(f"https://api.github.com/repos/{REPO}/actions/workflows/pre-match.yml/dispatches", headers={"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}, json={"ref": "main"})
with col2:
    if st.button("📊 Avvia Fase 2 (Post-Match)"):
        if TOKEN and REPO: requests.post(f"https://api.github.com/repos/{REPO}/actions/workflows/validazione_storico.yml/dispatches", headers={"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}, json={"ref": "main"})

tabs = st.tabs(["🎯 Palinsesto", "📊 Storico", "🗄️ Database Totale"])

# TAB 1: PALINSESTO
with tabs[0]:
    if os.path.exists("Pronostici_App_Betting.xlsx"):
        df = pd.read_excel("Pronostici_App_Betting.xlsx")
        for idx, row in df.iterrows():
            st.markdown(f"""
            <div class="card">
                <div class="time-label">🏆 {row.get('Campionato', '-')} | {row.get('Data_Ora_Match', '-')}</div>
                <h4 style="margin: 4px 0;">{row.get('3. Match', 'Match')}</h4>
                <div class="market-grid">
                    <div class="market-item"><b>1X2:</b> {row.get('1X2', '-')}</div>
                    <div class="market-item"><b>Esatto:</b> {row.get('Risultato_Esatto', '-')}</div>
                    <div class="market-item"><b>Doppia:</b> {row.get('Doppia_Chance', '-')}</div>
                    <div class="market-item"><b>Combo DC+U/O2.5:</b> {row.get('DC+U/O2.5', '-')}</div>
                    <div class="market-item"><b>U/O 1.5:</b> {row.get('U/O_1.5', '-')}</div>
                    <div class="market-item"><b>U/O 2.5:</b> {row.get('U/O_2.5', '-')}</div>
                    <div class="market-item"><b>U/O 3.5:</b> {row.get('U/O_3.5', '-')}</div>
                    <div class="market-item"><b>G/NG:</b> {row.get('Goal_NoGoal', '-')}</div>
                    <div class="market-item"><b>MG Casa:</b> {row.get('Pronostico_MG_Casa', '-')}</div>
                    <div class="market-item"><b>MG Ospite:</b> {row.get('Pronostico_MG_Trasferta', '-')}</div>
                    <div class="market-item"><b>Corner 1X2:</b> {row.get('Corner_1X2', '-')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ Nessun match in palinsesto calcolato. Avvia la Fase 1.")

# TAB 2: STORICO
with tabs[1]:
    if os.path.exists("Storico_Validato_Betting.xlsx"):
        df_storico = pd.read_excel("Storico_Validato_Betting.xlsx")
        if not df_storico.empty:
            df_storico['Risultato_Reale'] = df_storico['Risultato_Reale'].astype(str).str.strip()
            match_validi = df_storico[~df_storico['Risultato_Reale'].str.contains('NON ANCORA REALE|VALIDARE', case=False, na=True)]
            tot = len(match_validi)
            
            def calc_acc(col, is_corner=False):
                if is_corner: return "<span class='accuracy-value-nd'>N.D.</span>"
                val = f"{(len(match_validi[match_validi[col] == 'VINCENTE']) / tot * 100):.1f}%" if tot > 0 and col in match_validi.columns else "0.0%"
                return f"<span class='accuracy-value'>{val}</span>"

            st.write(f"📊 **Resoconto Accuratezza globale su {tot} Match Storici Conclusi:**")
            st.markdown(f"""
            <div class="accuracy-grid">
                <div class="accuracy-card"><span class="accuracy-market">1X2</span> {calc_acc('Esito_1X2')}</div>
                <div class="accuracy-card"><span class="accuracy-market">Risultato Esatto</span> {calc_acc('Esito_Risultato_Esatto')}</div>
                <div class="accuracy-card"><span class="accuracy-market">Doppia Chance</span> {calc_acc('Esito_Doppia_Chance')}</div>
                <div class="accuracy-card"><span class="accuracy-market">Combo DC+U/O2.5</span> {calc_acc('Esito_DC+U/O2.5')}</div>
                <div class="accuracy-card"><span class="accuracy-market">Under/Over 1.5</span> {calc_acc('Esito_U/O_1.5')}</div>
                <div class="accuracy-card"><span class="accuracy-market">Under/Over 2.5</span> {calc_acc('Esito_U/O_2.5')}</div>
                <div class="accuracy-card"><span class="accuracy-market">Under/Over 3.5</span> {calc_acc('Esito_U/O_3.5')}</div>
                <div class="accuracy-card"><span class="accuracy-market">Goal/NoGoal</span> {calc_acc('Esito_Goal_NoGoal')}</div>
                <div class="accuracy-card"><span class="accuracy-market">MG Casa</span> {calc_acc('Esito_Media_Goal_Casa')}</div>
                <div class="accuracy-card"><span class="accuracy-market">MG Ospite</span> {calc_acc('Esito_Media_Goal_Trasferta')}</div>
                <div class="accuracy-card"><span class="accuracy-market">Corner 1X2</span> {calc_acc('Esito_Corner_1X2', True)}</div>
            </div>
            """, unsafe_allow_html=True)
                
            st.markdown("<br><hr>", unsafe_allow_html=True)
            
            for idx, row in df_storico.iterrows():
                res_reale = row.get('Risultato_Reale', 'NON ANCORA REALE/DA VALIDARE')
                
                def get_badge(col_name):
                    val = str(row.get(col_name, '-')).strip().upper()
                    if val == "VINCENTE": return "✅ <span class='esito-vincente'>VINCENTE</span>"
                    if val == "PERDENTE": return "❌ <span class='esito-perdente'>PERDENTE</span>"
                    return "⏳ <span>In attesa</span>"

                st.markdown(f"""
                <div class="card-storico">
                    <div class="time-label">🏆 {row.get('Campionato', '-')} | {row.get('Data_Ora_Match', '-')}</div>
                    <h4 style="margin: 4px 0;">{row.get('3. Match', 'Match')}</h4>
                    <div class="result-label">⚽ Finale: {res_reale}</div>
                    <div class="market-grid">
                        <div class="market-item"><b>1X2:</b> {row.get('1X2', '-')} <br> {get_badge('Esito_1X2')}</div>
                        <div class="market-item"><b>Esatto:</b> {row.get('Risultato_Esatto', '-')} <br> {get_badge('Esito_Risultato_Esatto')}</div>
                        <div class="market-item"><b>Doppia:</b> {row.get('Doppia_Chance', '-')} <br> {get_badge('Esito_Doppia_Chance')}</div>
                        <div class="market-item"><b>Combo DC+U/O2.5:</b> {row.get('DC+U/O2.5', '-')} <br> {get_badge('Esito_DC+U/O2.5')}</div>
                        <div class="market-item"><b>U/O 1.5:</b> {row.get('U/O_1.5', '-')} <br> {get_badge('Esito_U/O_1.5')}</div>
                        <div class="market-item"><b>U/O 2.5:</b> {row.get('U/O_2.5', '-')} <br> {get_badge('Esito_U/O_2.5')}</div>
                        <div class="market-item"><b>U/O 3.5:</b> {row.get('U/O_3.5', '-')} <br> {get_badge('Esito_U/O_3.5')}</div>
                        <div class="market-item"><b>G/NG:</b> {row.get('Goal_NoGoal', '-')} <br> {get_badge('Esito_Goal_NoGoal')}</div>
                        <div class="market-item"><b>MG Casa:</b> {row.get('Pronostico_MG_Casa', '-')} <br> {get_badge('Esito_Media_Goal_Casa')}</div>
                        <div class="market-item"><b>MG Ospite:</b> {row.get('Pronostico_MG_Trasferta', '-')} <br> {get_badge('Esito_Media_Goal_Trasferta')}</div>
                        <div class="market-item"><b>Corner 1X2:</b> {row.get('Corner_1X2', '-')} <br> {get_badge('Esito_Corner_1X2')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📋 Il file storico temporaneo è vuoto.")
    else:
        st.info("ℹ️ Nessun dato storico elaborato in questa sessione.")

# TAB 3: DATABASE TOTALMENTE AUTOMATIZZATO (CON UNIONE IN MEMORIA TRA STORICO E PALINSESTO)
with tabs[2]:
    DB_FILE = "Database_Storico_Completo.xlsx"
    PALINSESTO_FILE = "Pronostici_App_Betting.xlsx"
    
    df_database = pd.DataFrame()
    df_palinsesto = pd.DataFrame()
    
    if os.path.exists(DB_FILE):
        try:
            df_database = pd.read_excel(DB_FILE)
        except Exception as e:
            st.error(f"⚠️ Errore lettura Archivio Storico: {e}")
            
    if os.path.exists(PALINSESTO_FILE):
        try:
            df_palinsesto = pd.read_excel(PALINSESTO_FILE)
        except Exception as e:
            st.error(f"⚠️ Errore lettura Palinsesto in DB: {e}")

    if not df_database.empty or not df_palinsesto.empty:
        if not df_database.empty and not df_palinsesto.empty:
            df_g = pd.concat([df_database, df_palinsesto], ignore_index=True)
            df_g = df_g.drop_duplicates(subset=['3. Match'], keep='first')
        elif not df_database.empty:
            df_g = df_database
        else:
            df_g = df_palinsesto

        if 'Data_Ora_Match' in df_g.columns:
            df_g = df_g.sort_values(by='Data_Ora_Match', ascending=False)

        st.write(f"🗄️ **Partite totali rilevate (Storico + Palinsesto Corrente): {len(df_g)}**")
        
        list_c = ["TUTTI"] + list(df_g['Campionato'].dropna().unique())
        scelta_c = st.selectbox("Filtra competizione:", list_c, key="filt_t3")
        df_m = df_g if scelta_c == "TUTTI" else df_g[df_g['Campionato'] == scelta_c]
        
        for idx, row in df_m.iterrows():
            res_r = str(row.get('Risultato_Reale', '-')).strip()
            if res_r in ['-', 'nan', '', 'NON ANCORA REALE/DA VALIDARE']:
                res_r = "DA GIOCARE / IN ATTESA DI VALIDAZIONE"
            
            def b_db(col):
                v = str(row.get(col, '-')).strip().upper()
                if v == "VINCENTE": return "✅ VINCENTE"
                if v == "PERDENTE": return "❌ PERDENTE"
                return "⏳ In attesa"

            mappa_colonne = {str(c).strip().lower(): str(c) for c in df_g.columns}
            
            def estrai_valore(lista_possibili_nomi):
                for nome in lista_possibili_nomi:
                    nome_puro = nome.strip().lower()
                    if nome_puro in mappa_colonne:
                        val = str(row.get(mappa_colonne[nome_puro], '-')).strip()
                        if val not in ['-', 'nan', '']:
                            return val
                return None

            v_punti_c = estrai_valore(["punti_casa"])
            v_punti_o = estrai_valore(["punti_trasferta"])
            v_gf_c = estrai_valore(["media_goal_casa"])
            v_gs_c = estrai_valore(["media_goal_subiti_casa"])
            v_gf_o = estrai_valore(["media_goal_trasferta"])
            v_gs_o = estrai_valore(["media_goal_subiti_trasferta"])
            v_forma_c = estrai_valore(["forma_casa"])
            v_forma_o = estrai_valore(["forma_trasferta"])

            el_st = []
            if v_punti_c is not None: el_st.append(f'<div class="market-item"><b>Punti Casa:</b> {v_punti_c}</div>')
            if v_punti_o is not None: el_st.append(f'<div class="market-item"><b>Punti Ospite:</b> {v_punti_o}</div>')
            if v_gf_c is not None: el_st.append(f'<div class="market-item"><b>Media GF Casa:</b> {v_gf_c}</div>')
            if v_gs_c is not None: el_st.append(f'<div class="market-item"><b>Media GS Casa:</b> {v_gs_c}</div>')
            if v_gf_o is not None: el_st.append(f'<div class="market-item"><b>Media GF Ospite:</b> {v_gf_o}</div>')
            if v_gs_o is not None: el_st.append(f'<div class="market-item"><b>Media GS Ospite:</b> {v_gs_o}</div>')
            if v_forma_c is not None: el_st.append(f'<div class="market-item"><b>Forma Casa:</b> {v_forma_c}</div>')
            if v_forma_o is not None: el_st.append(f'<div class="market-item"><b>Forma Ospite:</b> {v_forma_o}</div>')
            
            h_st = '<div class="section-title">📊 Statistiche Input</div>' + "".join(el_st) if el_st else ""

            m_keys = [
                ('1X2', '1X2', 'Esito_1X2'), ('Esatto', 'Risultato_Esatto', 'Esito_Risultato_Esatto'),
                ('Doppia Ch.', 'Doppia_Chance', 'Esito_Doppia_Chance'), ('Combo DC', 'DC+U/O2.5', 'Esito_DC+U/O2.5'),
                ('U/O 1.5', 'U/O_1.5', 'Esito_U/O_1.5'), ('U/O 2.5', 'U/O_2.5', 'Esito_U/O_2.5'),
                ('U/O 3.5', 'U/O_3.5', 'Esito_U/O_3.5'), ('G/NG', 'Goal_NoGoal', 'Esito_Goal_NoGoal'),
                ('Corner 1X2', 'Corner_1X2', 'Esito_Corner_1X2'),
                ('MG Casa', 'Pronostico_MG_Casa', 'Esito_Media_Goal_Casa'),
                ('MG Ospite', 'Pronostico_MG_Trasferta', 'Esito_Media_Goal_Trasferta')
            ]
            el_m = []
            for k, cp, ce in m_keys:
                vp = str(row.get(cp, '-')).strip()
                if vp not in ['-', 'nan', '']:
                    el_m.append(f'<div class="market-item"><b>{k}:</b> {vp} <br><small>{b_db(ce)}</small></div>')
            
            h_m = '<div class="section-title">🎯 Pronostici ed Esiti</div>' + "".join(el_m) if el_m else ""

            bg_color = "#e5e5ea" if "DA GIOCARE" in res_r else "#ffe5cc"
            text_color = "#1c1c1e" if "DA GIOCARE" in res_r else "#d97706"

            st.markdown(f"""
            <div class="card-database">
                <div class="time-label">🏆 {row.get('Campionato', '-')} | {row.get('Data_Ora_Match', '-')}</div>
                <h4 style="margin: 4px 0; color: #1c1c1e;">{row.get('3. Match', 'Match')}</h4>
                <div class="result-label" style="background: {bg_color}; color: {text_color};">⚽ Finale: {res_r}</div>
                <div class="market-grid">{h_st}{h_m}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ Nessun dato presente nel database storico o nel palinsesto.")
