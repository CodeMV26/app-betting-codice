# === AGGIUNGI QUESTO BLOCCO ALLA FINE DI ESEGUI_VALIDAZIONE PRIMA DEL PRINT ===
    import pytz
    from datetime import datetime
    with open("timestamp_fase2.txt", "w") as f:
        f.write(datetime.now(pytz.timezone("Europe/Rome")).strftime('%d/%m/%Y %H:%M:%S'))
    # ==============================================================================
    
    df_prono.to_excel(OUTPUT_VALIDATO, index=False)
    print("✅ Validazione completata...")
