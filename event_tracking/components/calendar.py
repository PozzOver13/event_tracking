import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

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