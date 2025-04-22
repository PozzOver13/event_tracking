import os
import json
import datetime
import pandas as pd

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from event_tracking.config import PATH_TOKEN, PATH_CREDENTIALS

# Configurazione dell'autenticazione Google
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_google_calendar_credentials():
    creds = None

    # Il file token.json memorizza i token di accesso e aggiornamento dell'utente
    if os.path.exists(PATH_TOKEN):
        creds = Credentials.from_authorized_user_info(json.load(open(PATH_TOKEN)))

    # Se non ci sono credenziali valide, l'utente deve accedere
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = (
                InstalledAppFlow
                .from_client_secrets_file(PATH_CREDENTIALS, SCOPES)
            )
            creds = flow.run_local_server(port=63576)

        # Salva le credenziali per la prossima esecuzione
        with open(PATH_TOKEN, 'w') as token:
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
            #'description': description,
            #'location': location,
            'start_time': start_time,
            'end_time': end_time,
            'all_day': all_day,
            'duration_minutes': duration_minutes,
            #'attendees': attendees,
            #'attendee_count': len(attendees),
            'day_of_week': start_time.strftime('%A'),
            'week_number': start_time.isocalendar()[1],
            'month': start_time.strftime('%B'),
            'year': start_time.year,
            'hour_of_day': start_time.hour if not all_day else None
        }

        processed_events.append(event_data)

    return pd.DataFrame(processed_events)