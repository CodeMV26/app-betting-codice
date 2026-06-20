# Sostituisci il blocco "st.tabs" con questo selettore a comparsa ottimizzato per mobile
scelta_tab = st.selectbox(
    "Visualizza Sezione:",
    [
        f"🎯 Palinsesto ({count_palinsesto})", 
        f"📊 Storico ({count_storico})", 
        f"🗄️ Database Totale ({count_database})"
    ]
)

# TAB 1: PALINSESTO
if "🎯 Palinsesto" in scelta_tab:
    if os.path.exists(PALINSESTO_FILE):
        # ... (lascia qui sotto tutto il codice originale del TAB 1) ...
    else:
        st.info("ℹ️ Nessun match in palinsesto calcolato. Avvia la Fase 1.")

# TAB 2: STORICO
elif "📊 Storico" in scelta_tab:
    if not df_g.empty:
        # ... (lascia qui sotto tutto il codice originale del TAB 2) ...

# TAB 3: DATABASE TOTALMENTE AUTOMATIZZATO
elif "🗄️ Database Totale" in scelta_tab:
    if not df_g.empty:
        # ... (lascia qui sotto tutto il codice originale del TAB 3) ...
