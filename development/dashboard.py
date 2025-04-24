import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import calendar
from datetime import datetime, timedelta
from event_tracking.config import RAW_DATA_DIR

file_path = os.path.join(RAW_DATA_DIR, 'my_calendar_db.parquet')

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
        # Conversione delle colonne di data/ora se necessario
        if pd.api.types.is_object_dtype(df['start_time']):
            df['start_time'] = pd.to_datetime(df['start_time'])
        if pd.api.types.is_object_dtype(df['end_time']):
            df['end_time'] = pd.to_datetime(df['end_time'])
        return df
    except Exception as e:
        st.error(f"Errore nel caricamento del file parquet: {e}")
        return None


# Dizionario dei colori personalizzati per calendario
calendar_colors = {
    "Giulia": "#FFB6C1",  # Rosa pastello
    "Pozz": "#ADD8E6",  # Blu pastello
    "Pozz Health & Learn": "#98FB98",  # Verde pastello
    "Pozz Work": "#FFFACD"  # Giallo pastello
}

# Stile e intestazione
st.title("📅 Dashboard Analisi Google Calendar")
st.markdown("""
Questa dashboard ti permette di esplorare e analizzare i tuoi eventi di Google Calendar.
Utilizza i filtri sulla barra laterale per personalizzare la visualizzazione.
""")

# Caricamento dati
df = load_data()

if df is not None:
    # Preparazione della sidebar per i filtri
    st.sidebar.header("Filtri")

    # Filtro per anno
    years = sorted(df['year'].unique())
    selected_year = st.sidebar.selectbox("Anno", years, index=len(years) - 1)

    # Filtro per calendario
    calendars = sorted(df['calendar_name'].unique())
    selected_calendars = st.sidebar.multiselect("Calendari", calendars, default=calendars)

    # Applicazione filtri
    filtered_df = df[(df['year'] == selected_year) &
                     (df['calendar_name'].isin(selected_calendars))]

    # Layout principale a due colonne
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Distribuzione eventi per mese")

        # Creazione di un dizionario per mappare i numeri dei mesi ai nomi in italiano
        mesi_italiani = {
            'January': 'Gennaio', 'February': 'Febbraio', 'March': 'Marzo',
            'April': 'Aprile', 'May': 'Maggio', 'June': 'Giugno',
            'July': 'Luglio', 'August': 'Agosto', 'September': 'Settembre',
            'October': 'Ottobre', 'November': 'Novembre', 'December': 'Dicembre'
        }

        # Conversione nomi mesi in italiano se disponibili
        filtered_df['mese'] = filtered_df['month'].map(mesi_italiani).fillna(filtered_df['month'])

        # Ordine corretto dei mesi per il grafico
        month_order = [mesi_italiani.get(month, month) for month in calendar.month_name[1:]]

        # Conteggio eventi per mese e calendario
        monthly_events = filtered_df.groupby(['mese', 'calendar_name']).size().reset_index(name='numero_eventi')

        # Estrai i calendari presenti nei dati filtrati e crea una mappatura dei colori
        present_calendars = filtered_df['calendar_name'].unique()
        color_discrete_map = {
            cal: calendar_colors.get(cal, px.colors.qualitative.Pastel[i % len(px.colors.qualitative.Pastel)])
            for i, cal in enumerate(present_calendars)}

        # Creazione istogramma con Plotly e colori personalizzati
        fig = px.histogram(
            monthly_events,
            x='mese',
            y='numero_eventi',
            color='calendar_name',
            title=f'Eventi per mese ({selected_year})',
            labels={'mese': 'Mese', 'numero_eventi': 'Numero di eventi', 'calendar_name': 'Calendario'},
            category_orders={"mese": month_order},
            barmode='group',
            color_discrete_map=color_discrete_map  # Usa la mappatura dei colori personalizzata
        )

        fig.update_layout(
            xaxis_title='Mese',
            yaxis_title='Numero di Eventi',
            legend_title='Calendario',
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        # Distribuzione per giorno della settimana
        st.subheader("Eventi per giorno della settimana")

        # Mappatura in italiano dei giorni della settimana
        giorni_italiani = {
            'Monday': 'Lunedì', 'Tuesday': 'Martedì', 'Wednesday': 'Mercoledì',
            'Thursday': 'Giovedì', 'Friday': 'Venerdì', 'Saturday': 'Sabato', 'Sunday': 'Domenica'
        }

        filtered_df['giorno'] = filtered_df['day_of_week'].map(giorni_italiani).fillna(filtered_df['day_of_week'])

        # Ordine corretto dei giorni
        weekday_order = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']

        weekday_events = filtered_df.groupby(['giorno', 'calendar_name']).size().reset_index(name='count')

        fig_weekday = px.histogram(
            weekday_events,
            x='giorno',
            y='count',
            color='calendar_name',
            title=f'Eventi per giorno della settimana ({selected_year})',
            labels={'giorno': 'Giorno', 'count': 'Numero di eventi', 'calendar_name': 'Calendario'},
            category_orders={"giorno": weekday_order},
            barmode='group',
            color_discrete_map=color_discrete_map  # Usa la stessa mappatura dei colori
        )

        fig_weekday.update_layout(
            xaxis_title='Giorno della Settimana',
            yaxis_title='Numero di Eventi',
            legend_title='Calendario',
            height=400
        )

        st.plotly_chart(fig_weekday, use_container_width=True)

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

        # Top 5 mesi più impegnati
        st.subheader("Mesi più impegnati")
        busy_months = filtered_df.groupby('mese').size().sort_values(ascending=False).reset_index(name='eventi')
        st.dataframe(busy_months.head(5), hide_index=True)

        # Distribuzione oraria
        st.subheader("Distribuzione oraria")

        # Filtro per eventi non giornalieri (con ora specificata)
        hourly_df = filtered_df[filtered_df['all_day'] == False]

        if not hourly_df.empty:
            hour_counts = hourly_df.groupby(['hour_of_day', 'calendar_name']).size().reset_index(name='count')

            fig_hours = px.bar(
                hour_counts,
                x='hour_of_day',
                y='count',
                color='calendar_name',
                title='Eventi per ora del giorno',
                labels={'hour_of_day': 'Ora', 'count': 'Numero di eventi'},
                color_discrete_map=color_discrete_map  # Usa la stessa mappatura dei colori
            )

            fig_hours.update_layout(
                xaxis=dict(tickmode='linear', tick0=0, dtick=2),
                xaxis_title='Ora del giorno',
                yaxis_title='Numero di eventi',
                height=350
            )

            st.plotly_chart(fig_hours, use_container_width=True)
        else:
            st.info("Non ci sono eventi con ora specificata nel periodo selezionato.")

        # Visualizzazione della legenda dei colori
        st.subheader("Legenda colori calendari")
        for calendar_name in selected_calendars:
            color = calendar_colors.get(calendar_name, "#CCCCCC")  # Colore di default grigio
            st.markdown(
                f"<div style='display: flex; align-items: center;'>"
                f"<div style='width: 20px; height: 20px; background-color: {color}; margin-right: 10px;'></div>"
                f"<div>{calendar_name}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

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