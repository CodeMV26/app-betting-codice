import streamlit as st
import pandas as pd
import os

# Configurazione della pagina ottimizzata per Mobile
st.set_page_config(page_title="App Betting", page_icon="⚽", layout="centered")

# Stile CSS per rendere l'interfaccia simile a un'app nativa per iPhone
st.markdown("""
    <style>
    .main { background-color: #f2f2f7; }
    .card {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .badge-verde {
        background-color: #34c759;
        color: white;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 12px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚽ App Betting Cloud")

# Barra di navigazione in alto (pulsanti grandi per il pollice)
tabs = st.tabs(["🎯 Pronostici", "📊 Archivio", "🤖 Simulatore"])

# --- TAB 1: PRONOSTICI DEL GIORNO ---
with tabs[0]:
    st.subheader("Match e Pronostici Calcolati")
    if os.path.exists("Pronostici_App_Betting.xlsx"):
        df_prono = pd.read_excel("Pronostici_App_Betting.xlsx")
        
        if df_prono.empty:
            st.info("Nessun pronostico generato nel file.")
        else:
            # Filtro per Campionato
            campionati = ["Tutti"] + list(df_prono['Campionato'].unique())
            scelta_camp = st.selectbox("Filtra Competizione:", campionati)
            
            df_filtrato = df_prono if scelta_camp == "Tutti" else df_prono[df_prono['Campionato'] == scelta_camp]
            
            # Generazione delle Card per iPhone
            for _, row in df_filtrato.iterrows():
                st.markdown(f"""
                <div class="card">
                    <b style="color:#8e8e93; font-size:12px;">🏆 {row.get('Campionato', 'Campionato')}</b>
                    <h3 style="margin:5px 0;">{row.get('3. Match', 'Match')}</h3>
                    <p style="margin:2px 0; font-size:14px;">📊 <b>Segno:</b> {row.get('PRONOSTICO', '-')} | <b>U/O:</b> {row.get('U/O 2.5', '-')}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ File Pronostici_App_Betting.xlsx non ancora presente. Esegui il flusso Pre-Match.")

# --- TAB 2: ARCHIVIO STORICO ---
with tabs[1]:
    st.subheader("Patrimonio Dati Accumulato")
    if os.path.exists("Storico_Validato_Betting.xlsx"):
        df_storico = pd.read_excel("Storico_Validato_Betting.xlsx")
        st.metric(label="Partite totali in archivio", value=len(df_storico))
        st.dataframe(df_storico, use_container_width=True)
    else:
        st.info("ℹ️ L'archivio storico si popolerà dopo aver eseguito la Fase 2 (Post-Match).")

# --- TAB 3: SIMULATORE ---
with tabs[2]:
    st.subheader("Laboratorio Algoritmi & ROI")
    st.info("Qui inseriremo i grafici di rendimento e i selettori dei modelli matematici.")
    st.slider("Soglia di confidenza algoritmo (%)", 50, 100, 65)
