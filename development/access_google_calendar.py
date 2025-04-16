import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pandas as pd
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Configurazione dell'autenticazione Google
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def get_google_calendar_credentials():
    creds = None
    # Il file token.json memorizza i token di accesso e aggiornamento dell'utente
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_info(json.load(open('token.json')))

    # Se non ci sono credenziali valide, l'utente deve accedere
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Salva le credenziali per la prossima esecuzione
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def fetch_calendar_events(time_period_days=30):
    """
    Recupera gli eventi dal calendario dell'utente per un determinato periodo di tempo
    """
    creds = get_google_calendar_credentials()
    service = build('calendar', 'v3', credentials=creds)

    # Calcola l'intervallo di date
    now = datetime.datetime.utcnow()
    start_date = now - datetime.timedelta(days=time_period_days)

    # Formatta le date nel formato richiesto da Google Calendar API
    now_str = now.isoformat() + 'Z'  # 'Z' indica UTC
    start_date_str = start_date.isoformat() + 'Z'

    print(f'Recupero eventi dal {start_date.strftime("%Y-%m-%d")} a oggi')

    # Chiama l'API Calendar
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_date_str,
        timeMax=now_str,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    return events


def process_calendar_events(events):
    """
    Elabora gli eventi del calendario e li trasforma in un DataFrame
    """
    processed_events = []

    for event in events:
        # Estrai informazioni di base
        event_id = event.get('id', '')
        summary = event.get('summary', 'Evento senza titolo')
        description = event.get('description', '')
        location = event.get('location', '')

        # Gestione delle date di inizio e fine
        start_time = None
        end_time = None
        all_day = False

        if 'dateTime' in event['start']:
            # Evento con orario specifico
            start_time = datetime.datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
            end_time = datetime.datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))
        else:
            # Evento che dura tutto il giorno
            start_time = datetime.datetime.fromisoformat(event['start']['date'])
            end_time = datetime.datetime.fromisoformat(event['end']['date'])
            all_day = True

        # Calcola la durata in minuti (per eventi non di tutto il giorno)
        duration_minutes = None
        if not all_day:
            duration = end_time - start_time
            duration_minutes = duration.total_seconds() / 60

        # Raccogli informazioni sui partecipanti
        attendees = []
        if 'attendees' in event:
            for attendee in event['attendees']:
                attendees.append(attendee.get('email', ''))

        # Crea un dizionario con tutte le informazioni rilevanti
        event_data = {
            'event_id': event_id,
            'summary': summary,
            'description': description,
            'location': location,
            'start_time': start_time,
            'end_time': end_time,
            'all_day': all_day,
            'duration_minutes': duration_minutes,
            'attendees': attendees,
            'attendee_count': len(attendees),
            'day_of_week': start_time.strftime('%A'),
            'week_number': start_time.isocalendar()[1],
            'month': start_time.strftime('%B'),
            'year': start_time.year,
            'hour_of_day': start_time.hour if not all_day else None
        }

        processed_events.append(event_data)

    return pd.DataFrame(processed_events)


def create_langchain_documents(df):
    """
    Converte il DataFrame in documenti LangChain per l'analisi
    """
    documents = []

    # Crea un documento per ogni evento
    for _, row in df.iterrows():
        content = f"""
        Evento: {row['summary']}
        Descrizione: {row['description']}
        Data: {row['start_time'].strftime('%Y-%m-%d')}
        Ora di inizio: {row['start_time'].strftime('%H:%M') if not row['all_day'] else 'Tutto il giorno'}
        Ora di fine: {row['end_time'].strftime('%H:%M') if not row['all_day'] else 'Tutto il giorno'}
        Durata (minuti): {row['duration_minutes'] if not row['all_day'] else 'N/A'}
        Luogo: {row['location']}
        Partecipanti: {', '.join(row['attendees']) if row['attendees'] else 'Nessuno'}
        """

        metadata = {
            'event_id': row['event_id'],
            'summary': row['summary'],
            'start_time': row['start_time'],
            'day_of_week': row['day_of_week'],
            'all_day': row['all_day'],
            'duration_minutes': row['duration_minutes'],
            'attendee_count': row['attendee_count']
        }

        doc = Document(page_content=content.strip(), metadata=metadata)
        documents.append(doc)

    return documents


def categorize_events(df):
    """
    Categorizza gli eventi in base al titolo e alla descrizione
    Questa è una funzione di esempio - in un'implementazione reale potresti
    usare un modello LLM per categorizzare in modo più sofisticato
    """
    # Categorizzazione semplice basata su parole chiave
    categories = []

    for _, row in df.iterrows():
        summary_lower = row['summary'].lower()
        description_lower = str(row['description']).lower()
        text = summary_lower + ' ' + description_lower

        if any(word in text for word in ['riunione', 'meeting', 'call', 'conf']):
            categories.append('Riunione')
        elif any(word in text for word in ['formazione', 'corso', 'training', 'workshop']):
            categories.append('Formazione')
        elif any(word in text for word in ['consegna', 'scadenza', 'deadline']):
            categories.append('Scadenza')
        elif any(word in text for word in ['viaggio', 'trasferta', 'volo']):
            categories.append('Viaggio')
        elif any(word in text for word in ['pranzo', 'cena', 'colazione']):
            categories.append('Pasto')
        elif any(word in text for word in ['compleanno', 'anniversario', 'festa']):
            categories.append('Evento personale')
        else:
            categories.append('Altro')

    df['categoria'] = categories
    return df


def main(days=30):
    """
    Funzione principale che coordina l'estrazione e l'elaborazione dei dati
    """
    # Recupera gli eventi
    events = fetch_calendar_events(days)

    if not events:
        print('Nessun evento trovato nel periodo specificato.')
        return None, None

    print(f'Trovati {len(events)} eventi.')

    # Elabora gli eventi in un DataFrame
    df = process_calendar_events(events)

    # Categorizza gli eventi
    df = categorize_events(df)

    # Crea documenti LangChain
    documents = create_langchain_documents(df)

    # Salva il DataFrame per ulteriori analisi
    df.to_csv('calendar_events.csv', index=False)

    return df, documents


if __name__ == "__main__":
    import json  # Aggiunto import mancante

    # Esegui con un periodo di 90 giorni
    df, docs = main(90)
    print(f"Dataset creato con {len(df)} eventi e {len(docs)} documenti LangChain")