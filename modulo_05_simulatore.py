import pandas as pd
import os

# --- CONFIGURAZIONE ---
FILE_STORICO = "Storico_Validato_Betting.xlsx"
OUTPUT_SIMULAZIONE = "Report_Simulatore_Betting.xlsx"
PUNTATA_FISSA = 10.0  # Euro da puntare su ogni match qualificato
QUOTA_MEDIA_STIMATA = 1.85  # Quota media prudenziale per il calcolo del rendimento

def esegui_simulazione():
    print("\n📊 --- APP BETTING CLOUD - SIMULATORE STRATEGIE ---")
    
    if not os.path.exists(FILE_STORICO):
        print(f"⚠️ Nessun file {FILE_STORICO} trovato. Impossibile simulare la strategia.")
        return

    df_storico = pd.read_excel(FILE_STORICO)
    if df_storico.empty:
        print("⚠️ Lo storico dei dati è vuoto.")
        return

    # Pulizia e filtro: simuliamo solo sui match che hanno già un esito reale (VINCENTE/PERDENTE)
    # e che hanno un'alta affidabilità (maggiore del 65%)
    if 'Esito 1X2' not in df_storico.columns or 'Affidabilità' not in df_storico.columns:
        print("⚠️ Colonne di validazione non trovate. Attendi che il validatore elabori i dati reali.")
        return

    # Convertiamo l'affidabilità in numero per il filtro
    df_storico['Aff_Num'] = df_storico['Affidabilità'].str.replace('%', '').astype(float)
    
    # Filtro Strategia: Solo match giocati e con Affidabilità > 65%
    df_filtrato = df_storico[(df_storico['Esito 1X2'].isin(['VINCENTE', 'PERDENTE'])) & (df_storico['Aff_Num'] > 65)].copy()

    if df_filtrato.empty:
        print("⚠️ Nessun match soddisfa i criteri della strategia (Affidabilità > 65% e match terminato).")
        return

    tot_giocate = len(df_filtrato)
    vincenti = len(df_filtrato[df_filtrato['Esito 1X2'] == 'VINCENTE'])
    perdenti = len(df_filtrato[df_filtrato['Esito 1X2'] == 'PERDENTE'])
    
    win_rate = round((vincenti / tot_giocate) * 100, 2) if tot_giocate > 0 else 0

    # Calcolo Finanziario
    capitale_investito = tot_giocate * PUNTATA_FISSA
    lordo_vincite = vincenti * (PUNTATA_FISSA * QUOTA_MEDIA_STIMATA)
    bilancio_netto = lordo_vincite - capitale_investito
    roi = round((bilancio_netto / capitale_investito) * 100, 2) if capitale_investito > 0 else 0

    # Creazione del Report di Sintesi
    report_data = {
        'Metrica': [
            'Strategia Applicata', 'Puntata Singola (€)', 'Quota Media Stimata', 
            'Totale Scommesse Simulate', 'Scommesse Vincenti', 'Scommesse Perdenti', 
            'Win Rate (%)', 'Capitale Totale Investito (€)', 'Rendimento Netto (€)', 'ROI (%)'
        ],
        'Valore': [
            'Affidabilità Alta (>65%)', f"{PUNTATA_FISSA} €", f"{QUOTA_MEDIA_STIMATA}", 
            tot_giocate, vincenti, perdenti, f"{win_rate} %", 
            f"{capitale_investito} €", f"{round(bilancio_netto, 2)} €", f"{roi} %"
        ]
    }
    df_report = pd.DataFrame(report_data)

    # Salviamo il report finale in un nuovo foglio Excel
    with pd.ExcelWriter(OUTPUT_SIMULAZIONE, engine='xlsxwriter') as writer:
        df_report.to_excel(writer, sheet_name='Sintesi_Performance', index=False)
        df_filtrato.to_excel(writer, sheet_name='Dettaglio_Giocate', index=False)
        
    print(f"✅ Simulazione completata con successo!")
    print(f"📈 Scommesse analizzate: {tot_giocate} | Win Rate: {win_rate}% | ROI: {roi}%")
    print(f"💾 Report salvato in: {OUTPUT_SIMULAZIONE}")

if __name__ == "__main__":
    esegui_simulazione()
