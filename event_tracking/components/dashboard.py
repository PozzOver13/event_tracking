import streamlit as st

# Dizionario dei colori personalizzati per calendario
CALENDAR_COLORS = {
    "Giulia": "#FFB6C1",  # Rosa pastello
    "Pozz": "#ADD8E6",  # Blu pastello
    "Pozz Health & Learn": "#98FB98",  # Verde pastello
    "Pozz Work": "#FFFACD"  # Giallo pastello
}

# Creazione di un dizionario per mappare i numeri dei mesi ai nomi in italiano
MESI_ITALIANI = {
    'January': 'Gennaio', 'February': 'Febbraio', 'March': 'Marzo',
    'April': 'Aprile', 'May': 'Maggio', 'June': 'Giugno',
    'July': 'Luglio', 'August': 'Agosto', 'September': 'Settembre',
    'October': 'Ottobre', 'November': 'Novembre', 'December': 'Dicembre'
}

def header_display():
    # Stile e intestazione
    st.title("📅 Dashboard Analisi Google Calendar")
    st.markdown("""
    Questa dashboard ti permette di esplorare e analizzare i tuoi eventi di Google Calendar.
    Utilizza i filtri sulla barra laterale per personalizzare la visualizzazione.
    """)

def sidebar_display(df):
    # Preparazione della sidebar per i filtri
    st.sidebar.header("Filtri")

    # Filtro per anno
    years = sorted(df['year'].unique())
    selected_year = st.sidebar.selectbox("Anno", years, index=len(years) - 1)

    # Filtro per calendario
    calendars = sorted(df['calendar_name'].unique())
    selected_calendars = st.sidebar.multiselect("Calendari", calendars, default=calendars)

    dict_out = {
        "selected_year": selected_year,
        "selected_calendars": selected_calendars
    }

    return dict_out
