import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import calendar
from datetime import datetime, timedelta

from event_tracking.components.dashboard import *
from event_tracking.config import RAW_DATA_DIR

file_path = os.path.join(RAW_DATA_DIR, 'my_calendar_db_20250508.parquet')

# Configurazione pagina
st.set_page_config(
    page_title="Analisi Calendario",
    page_icon="📅",
    layout="wide"
)


# Funzione per caricare i dati
@st.cache_data
def load_data():
    try:
        df = pd.read_parquet(file_path)

        df['year_only'] = df['start_time'].dt.year.astype(str)
        df['year_month'] = df['start_time'].dt.strftime('%Y-%m')
        df['year_month_week'] = df['start_time'].dt.strftime('%Y-%m-') + df['week_number'].astype(str).str.zfill(2)

        # Conversione delle colonne di data/ora se necessario
        if pd.api.types.is_object_dtype(df['start_time']):
            df['start_time'] = pd.to_datetime(df['start_time'])
        if pd.api.types.is_object_dtype(df['end_time']):
            df['end_time'] = pd.to_datetime(df['end_time'])
        return df
    except Exception as e:
        st.error(f"Errore nel caricamento del file parquet: {e}")
        return None

header_display()

# Caricamento dati
df = load_data()

if df is not None:
    dict_sidebar = sidebar_display(df)
    selected_year = dict_sidebar["selected_year"]
    selected_calendars = dict_sidebar["selected_calendars"]
    selected_time_scale = dict_sidebar["selected_time_scale"]

    # Applicazione filtri
    filtered_df = df[(df['year'] == selected_year) &
                     (df['calendar_name'].isin(selected_calendars))]

    # Layout principale a due colonne
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Distribuzione attività lavorative")

        fig_contribution = get_contribution_plot(df, view=selected_time_scale)

        st.plotly_chart(fig_contribution, use_container_width=True)


    with col2:
        st.subheader("Statistiche")

        # Calcolo metriche
        total_events = len(filtered_df)
        avg_duration = filtered_df['duration_minutes'].mean()
        all_day_events = filtered_df['all_day'].sum()

        # Display delle metriche
        st.metric("Totale eventi", f"{total_events}")
        st.metric("Durata media", f"{avg_duration:.1f} min")
        st.metric("Eventi giornalieri", f"{all_day_events}")


    # Sezione per analisi futura con LLM
    st.subheader("🤖 Chat Analisi Tempo")
    st.info("""
    Questa sezione permetterà di discutere con un LLM su come hai speso il tuo tempo rispetto agli obiettivi.
    Funzionalità in fase di sviluppo.
    """)

    # Placeholder per implementazione futura
    user_input = st.text_area("Fai una domanda sulla tua gestione del tempo:", "")
    if st.button("Analizza"):
        st.write("Funzionalità non ancora implementata. Sarà disponibile nelle prossime versioni.")

        # Placeholder per future risposte
        with st.chat_message("assistant"):
            st.write("Qui apparirà l'analisi del tuo tempo basata sui dati del calendario.")

    # Esplorazione dati
    with st.expander("Esplora i dati grezzi"):
        st.dataframe(filtered_df)

else:
    st.error(
        "Impossibile caricare i dati. Assicurati che il file 'my_calendar_db.parquet' sia disponibile nella directory corrente.")

    # Demo mode
    if st.button("Carica dati di esempio"):
        st.info("Questa funzionalità sarà implementata in una versione futura.")