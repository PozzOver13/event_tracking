import streamlit as st
import plotly.express as px

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
    st.title("📅 Monthly Review")
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

    # Filtro per multiscale review
    multi_scale_list = ['yearly', 'monthly', 'weekly']
    selected_time_scale = st.sidebar.selectbox("Time Scale", multi_scale_list, index=len(years) - 1)

    dict_out = {
        "selected_year": selected_year,
        "selected_calendars": selected_calendars,
        "selected_time_scale": selected_time_scale
    }

    return dict_out

def get_contribution_plot(df, view = "monthly"):
    dict_view_available = {
        'yearly': 'year_only',
        'monthly': 'year_month',
        'weekly': 'year_month_week'
    }

    df_pivot_cat = (
        df
        .loc[(df["calendar_name"] == "Pozz Work"), :]
        # .head()
        .groupby([dict_view_available[view], "event_category"])
        .size()
        .to_frame("count")
        .sort_values("count", ascending=False)
        .pivot_table(index="event_category", columns=dict_view_available[view], values="count")
        .fillna(0)
    )

    # Creazione della heatmap
    fig = px.imshow(df_pivot_cat,
                    labels=dict(x="Time", y="Summary", color="Valore"),
                    x=df_pivot_cat.columns,
                    y=df_pivot_cat.index,
                    color_continuous_scale="Blues")  # Puoi scegliere altre scale di colori

    fig.update_xaxes(type='category')
    fig.update_layout(title="Evoluzione attività svolte", title_x=0.5)

    return fig