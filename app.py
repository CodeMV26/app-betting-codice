import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime
import pytz
import time
import re

st.set_page_config(page_title="Pannello Betting", page_icon="⚽", layout="centered")

# Stili CSS ottimizzati per iPhone
st.markdown("""
    <style>
    .main { background-color: #f2f2f7; }
    .card, .card-storico, .card-database { background-color: white; padding: 14px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); margin-bottom: 14px; }
    .card { border-left: 5px solid #007aff; }
    .card-storico { border-left: 5px solid #34c759; }
    .card-database { border-left: 5px solid #ff9500; }
    .time-label { color: #8e8e93; font-size: 11px; font-weight: bold; }
    .update-container { background: #ffffff; padding: 10px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #e5e5ea; }
    .update-label { color: #1c1c1e; font-size: 12px; font-style: italic; margin-bottom: 4px; }
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
FUSO_ROMA = pytz.timezone("Europe/Rome")

st.title("⚽ Controllo Betting Pro")

# Il pulsante distrugge la vecchia cache prima di ricaricare la pagina
if st.button("🔄 Aggiorna Schermata", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# Definizione File fisici obbligatori
DB_FILE = "Database_Storico_Completo.xlsx"
STORICO_FILE = "Storico_Validato_Betting.xlsx"
PALINSESTO_FILE = "Pronostici_App_Betting.xlsx"

# ========================================================================
# BLOCCO DATE RIGIDAMENTE ISOLATE - SOLO ED ESCLUSIVAMENTE DA LOG LOGISTICI
# ========================================================================
st.markdown('<div class="update-container">', unsafe_allow_html=True)

# 1. LETTURA STATICA FASE 1 (SOLO DA LOG)
if os.path.exists("timestamp_fase1.txt"):
    try:
        with open("timestamp_fase1.txt", "r") as f:
            stringa_data_fase1 = f.read().strip()
        if stringa_data_fase1:
            st.markdown(f"<div class='update-label'>📅 <b>Ultimo calcolo Palinsesto (Fase 1):</b> {stringa_data_fase1}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='update-label'>📅 <b>Ultimo calcolo Palinsesto (Fase 1):</b> Log presente ma vuoto</div>", unsafe_allow_html=True)
    except:
        st.markdown("<div class='update-label'>📅 <b>Ultimo calcolo Palinsesto (Fase 1):</b> Errore lettura log</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='update-label'>📅 <b>Ultimo calcolo Palinsesto (Fase 1):</b> In attesa del primo avvio della Fase 1</div>", unsafe_allow_html=True)

# 2. LETTURA STATICA FASE 2 (SOLO DA LOG)
if os.path.exists("timestamp_fase2.txt"):
    try:
        with open("timestamp_fase2.txt", "r") as f:
            stringa_data_fase2 = f.read().strip()
        if stringa_data_fase2:
            st.markdown(f"<div class='update-label'>🗄️ <b>Ultima Validazione Storico (Fase 2):</b> {stringa_data_fase2}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='update-label'>🗄️ <b>Ultima Validazione Storico (Fase 2):</b> Log presente ma vuoto</div>", unsafe_allow_html=True)
    except:
        st.markdown("<div class='update-label'>🗄️ <b>Ultima Validazione Storico (Fase 2):</b> Errore lettura log</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='update-label'>🗄️ <b>Ultima Validazione Storico (Fase 2):</b> In attesa del primo avvio della Fase 2</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
# ========================================================================


# Funzione per monitorare i workflow
def esegui_e_attendi_workflow(workflow_name):
    if not TOKEN or not REPO:
        st.error("Credenziali GitHub mancanti nei Secrets.")
        return
    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
    url_dispatch = f"https://api.github.com/repos/{REPO}/actions/workflows/{workflow_name}/dispatches"
    url_runs = f"https://api.github.com/repos/{REPO}/actions/workflows/{workflow_name}/runs"
    
    res = requests.post(url_dispatch, headers=headers, json={"ref": "main"})
    if res.status_code != 204:
        st.error("Impossibile avviare il workflow su GitHub.")
        return

    time.sleep(6)
    completato = False
    successo = False
    
    for _ in range(50): 
        try:
            r = requests.get(url_runs, headers=headers).json()
            if "workflow_runs" in r and len(r["workflow_runs"]) > 0:
                ultimo_run = r["workflow_runs"][0]
                if ultimo_run.get("status") == "completed":
                    completato = True
                    successo = (ultimo_run.get("conclusion") == "success")
                    break
        except:
            pass
        time.sleep(6)
    
    if completato:
        st.cache_data.clear()
        if successo:
            st.toast("✅ Elaborazione completata con successo!", icon="🎉")
        else:
            st.toast("❌ Errore durante l'esecuzione su GitHub.", icon="🚨")
        time.sleep(1)
        st.rerun()
    else:
        st.warning("⏱️ Timeout raggiunto. Verifica lo stato direttamente su GitHub.")


col1, col2 = st.columns(2)
with col1:
    if st.button("🚀 Avvia Fase 1 (Pre-Match)", use_container_width=True):
        with st.spinner("⏳ Fase 1 in progress su GitHub... Attendi..."):
            esegui_e_attendi_workflow("pre-match.yml")
with col2:
    if st.button("📊 Avvia Fase 2 (Post-Match)", use_container_width=True):
        with st.spinner("⏳ Fase 2 in progress su GitHub... Attendi..."):
            esegui_e_attendi_workflow("validazione_storico.yml")


# Lettura file forzata senza memorizzazione vecchia in cache
@st.cache_data(ttl=10)
def leggi_excel_fresco(file_path):
    if os.path.exists(file_path):
        return pd.read_excel(file_path)
    return pd.DataFrame()

df_database = leggi_excel_fresco(DB_FILE)
df_palinsesto = leggi_excel_fresco(PALINSESTO_FILE)

if not df_database.empty and not df_palinsesto.empty:
    df_g = pd.concat([df_database, df_palinsesto], ignore_index=True)
    df_g = df_g.drop_duplicates(subset=['3. Match'], keep='first')
elif not df_database.empty:
    df_g = df_database
else:
    df_g = df_palinsesto

if not df_g.empty and 'Risultato_Reale' not in df_g.columns:
    df_g['Risultato_Reale'] = "-"


# CONTEGGI DINAMICI
count_palinsesto = len(df_palinsesto) if not df_palinsesto.empty else 0
df_storico_conteggio = leggi_excel_fresco(STORICO_FILE)
count_storico = len(df_storico_conteggio) if not df_storico_conteggio.empty else 0
count_database = len(df_g) if not df_g.empty else 0


# SELETTORE
scelta_tab = st.selectbox(
    "📂 Seleziona Sezione da Visualizzare:",
    [
        f"🎯 Palinsesto ({count_palinsesto})", 
        f"📊 Storico ({count_storico})", 
        f"🗄️ Database Totale ({count_database})"
    ]
)

# SEZIONE 1: PALINSESTO
if "🎯 Palinsesto" in scelta_tab:
    if not df_palinsesto.empty:
        for idx, row in df_palinsesto.iterrows():
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

# SEZIONE 2: STORICO
elif "📊 Storico" in scelta_tab:
    if not df_g.empty:
        def is_match_terminato(val):
            v_str = str(val).strip()
            return bool(re.match(r'^\d+-\d+$', v_str))
        
        mask_terminati = df_g['Risultato_Reale'].apply(is_match_terminato)
        match_validi = df_g[mask_terminati].copy()
        tot = len(match_validi)
        
        def calc_acc(col, is_corner=False):
            if is_corner: return "<span class='accuracy-value-nd'>N.D.</span>"
            if tot == 0 or col not in match_validi.columns: return "<span class='accuracy-value'>0.0%</span>"
            
            vincenti = len(match_validi[match_validi[col].astype(str).str.strip().str.upper() == 'VINCENTE'])
            percentuale = (vincenti / tot) * 100
            return f"<span class='accuracy-value'>{percentuale:.1f}%</span>"

        st.write(f"📊 **Resoconto Accuratezza su {tot} Match Terminati presenti nel Database Totale:**")
        st.markdown(f"""
        <div class="accuracy-grid">
            <div class="accuracy-card"><span class="accuracy-market">1X2</span> {calc_acc('App_Esito_1X2' if 'App_Esito_1X2' in match_validi.columns else 'Esito_1X2')}</div>
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
    else:
        st.info("ℹ️ Nessun dato disponibile nel database totale per elaborare l'accuratezza.")

    st.markdown("<br><hr>", unsafe_allow_html=True)

    if not df_storico_conteggio.empty:
        for idx, row in df_storico_conteggio.iterrows():
            res_reale = str(row.get('Risultato_Reale', '')).strip().upper()
            if "ELABORAZIONE" in res_reale or "VALIDARE" in res_reale or "NON ANCORA" in res_reale:
                res_reale = "IN ATTESA DI VALIDAZIONE"
            
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

# SEZIONE 3: DATABASE TOTALMENTE AUTOMATIZZATO
elif "🗄️ Database Totale" in scelta_tab:
    if not df_g.empty:
        if 'Data_Ora_Match' in df_g.columns:
            df_g['Data_Ora_Match_Parsed'] = pd.to_datetime(df_g['Data_Ora_Match'], format='%d/%m/%Y %H:%M', errors='coerce')
            df_g = df_g.sort_values(by='Data_Ora_Match_Parsed', ascending=True)

        st.write(f"🗄️ **Partite totali rilevate (Ordinamento Crescente): {len(df_g)}**")
        
        list_c = ["TUTTI"] + list(df_g['Campionato'].dropna().unique())
        scelta_c = st.selectbox("Filtra competizione:", list_c, key="filt_t3")
        df_m = df_g if scelta_c == "TUTTI" else df_g[df_g['Campionato'] == scelta_c]
        
        for idx, row in df_m.iterrows():
            res_r = str(row.get('Risultato_Reale', '-')).strip()
            res_r_up = res_r.upper()
            
            if res_r in ['-', 'nan', ''] or "ELABORAZIONE" in res_r_up or "VALIDARE" in res_r_up or "NON ANCORA" in res_r_up:
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
                ('Doppia Ch.', 'Doppia_Chance', 'Esito_Doppia_Chance'), ('Combo DC+U/O2.5', 'DC+U/O2.5', 'Esito_DC+U/O2.5'),
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
            
        st.markdown("<br><hr>", unsafe_allow_html=True)
        
        # RESET AVANZATO (STREAMLIT + GITHUB)
        @st.dialog("⚠️ CONFERMA CANCELLAZIONE")
        def conferma_reset_dialog():
            st.warning("Sei veramente sicuro di voler svuotare interamente l'archivio storico anche su GitHub? Questa azione eliminerà tutti i record in modo definitivo.")
            col_yes, col_no = st.columns(2)
            if col_yes.button("🔥 Sì, Cancella Tutto", use_container_width=True):
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                if os.path.exists(STORICO_FILE): os.remove(STORICO_FILE)
                
                if TOKEN and REPO:
                    headers = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}
                    for file_da_eliminare in [DB_FILE, STORICO_FILE]:
                        url_file = f"https://api.github.com/repos/{REPO}/contents/{file_da_eliminare}"
                        res_get = requests.get(url_file, headers=headers)
                        if res_get.status_code == 200:
                            sha = res_get.json().get("sha")
                            payload = {
                                "message": f"Svuotamento database storico ({file_da_eliminare}) tramite pannello Streamlit",
                                "sha": sha,
                                "branch": "main"
                            }
                            requests.delete(url_file, headers=headers, json=payload)
                
                st.cache_data.clear()
                st.success("Database svuotato con successo localmente e su GitHub!")
                st.rerun()
            if col_no.button("❌ Annulla", use_container_width=True):
                st.rerun()

        if st.button("🗑️ Reset Database Storico", type="primary", use_container_width=True):
            conferma_reset_dialog()
            
    else:
        st.info("ℹ️ Nessun dato presente nel database storico o nel palinsesto.")
