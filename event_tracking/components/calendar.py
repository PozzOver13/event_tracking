import os
import json
import datetime
import pandas as pd

from dotenv import load_dotenv, find_dotenv

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


def get_calendars_to_include():
    """
    Recupera la lista dei calendari da includere dall'ambiente
    Formato della variabile d'ambiente: CALENDARS_TO_INCLUDE=calendario1,calendario2,calendario3
    """
    dotenv_path = find_dotenv()

    # load up the entries as environment variables
    load_dotenv(dotenv_path)

    calendars_str = os.environ.get('CALENDARS_TO_INCLUDE', '')
    if not calendars_str:
        # Se la variabile non è impostata, includi tutti i calendari
        return None

    # Split della stringa in una lista di nomi di calendari
    return [cal.strip() for cal in calendars_str.split(',')]


def fetch_all_calendars(service):
    """
    Recupera tutti i calendari disponibili per l'utente
    e filtra in base alla variabile d'ambiente
    """
    calendar_list = service.calendarList().list().execute()
    all_calendars = calendar_list.get('items', [])

    calendars_to_include = get_calendars_to_include()

    if calendars_to_include is None:
        # Includi tutti i calendari
        print(f"Nessun filtro specificato. Inclusi tutti i {len(all_calendars)} calendari.")
        return all_calendars

    # Filtra i calendari in base al nome
    filtered_calendars = [
        cal for cal in all_calendars
        if cal['summary'] in calendars_to_include
    ]

    print(f"Filtrati {len(filtered_calendars)} calendari su {len(all_calendars)} totali.")
    print(f"Calendari inclusi: {[cal['summary'] for cal in filtered_calendars]}")

    return filtered_calendars


def fetch_calendar_events(time_period_days=30):
    """
    Recupera gli eventi da tutti i calendari dell'utente per un determinato periodo di tempo
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

    # Recupera tutti i calendari
    calendars = fetch_all_calendars(service)
    print(f'Trovati {len(calendars)} calendari')

    all_events = []

    # Per ogni calendario, recupera gli eventi
    for calendar in calendars:
        calendar_id = calendar['id']
        calendar_name = calendar['summary']
        print(f'Recupero eventi dal calendario: {calendar_name}')

        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=start_date_str,
            timeMax=now_str,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        # Aggiungi il nome del calendario a ogni evento
        for event in events:
            event['calendar_name'] = calendar_name
            event['calendar_id'] = calendar_id

        all_events.extend(events)
        print(f'  - Trovati {len(events)} eventi in questo calendario')

    print(f'Totale eventi recuperati: {len(all_events)}')
    return all_events


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

        # Informazioni sul calendario
        calendar_name = event.get('calendar_name', 'Calendario principale')
        calendar_id = event.get('calendar_id', 'primary')

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
            'calendar_name': calendar_name,  # Aggiunta questa riga
            #'calendar_id': calendar_id,  # Aggiunta questa riga
            'start_time': start_time,
            'end_time': end_time,
            'all_day': all_day,
            'duration_minutes': duration_minutes,
            #'attendees': attendees,
            #'attendee_count': len(attendees),
            'day_of_week': start_time.strftime('%A'),
            'week_number': start_time.isocalendar()[1],
            'day': start_time.day,
            'month': start_time.strftime('%B'),
            'year': start_time.year,
            'hour_of_day': start_time.hour if not all_day else None
        }

        processed_events.append(event_data)

    return pd.DataFrame(processed_events)