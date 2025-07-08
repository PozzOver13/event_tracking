import os
import json
import datetime
import pandas as pd
import pytz
from dotenv import load_dotenv, find_dotenv

from transformers import pipeline

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from event_tracking.config import PATH_TOKEN, PATH_CREDENTIALS

from dotenv import load_dotenv, find_dotenv

from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
import openai

_ = load_dotenv(find_dotenv())  # read local .env file
openai.api_key = os.environ['OPENAI_API_KEY']

# Configurazione dell'autenticazione Google
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

WORK_CATEGORIES = ["avm-property-value", "avm-meetings", "avm-genertel-poc",
                   "finbox-meetings", "finbox-gara-mcc", "finbox-privati",
                   "finbox-deploy-affordability",
                   "smart-lending-suite-meetings",
                   "side-project-tools-n-pipeline", "dss-best-practices",
                   "other"]


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
    Recupera gli eventi da tutti i calendari dell'utente per un determinato periodo di tempo,
    gestendo la paginazione per ottenere tutti gli eventi.
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

    # Per ogni calendario, recupera gli eventi con paginazione
    for calendar in calendars:
        calendar_id = calendar['id']
        calendar_name = calendar['summary']
        print(f'Recupero eventi dal calendario: {calendar_name}')

        page_token = None
        total_events_in_calendar = 0

        while True:
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=start_date_str,
                timeMax=now_str,
                singleEvents=True,
                orderBy='startTime',
                maxResults=2500,  # Imposta il limite massimo per pagina
                pageToken=page_token  # Aggiungi il pageToken se disponibile
            ).execute()

            events = events_result.get('items', [])

            # Aggiungi il nome del calendario a ogni evento
            for event in events:
                event['calendar_name'] = calendar_name
                event['calendar_id'] = calendar_id

            all_events.extend(events)
            total_events_in_calendar += len(events)

            page_token = events_result.get('nextPageToken')

            if not page_token:
                # Non ci sono più pagine, esci dal ciclo
                break
            print(f'  - Trovati {len(events)} eventi in questa pagina. Recupero la prossima pagina...')

        print(f'  - Totale eventi recuperati per {calendar_name}: {total_events_in_calendar}')

    print(f'Totale eventi recuperati complessivamente: {len(all_events)}')
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
            # 'description': description,
            # 'location': location,
            'calendar_name': calendar_name,  # Aggiunta questa riga
            # 'calendar_id': calendar_id,  # Aggiunta questa riga
            'start_time': start_time,
            'end_time': end_time,
            'all_day': all_day,
            'duration_minutes': duration_minutes,
            # 'attendees': attendees,
            # 'attendee_count': len(attendees),
            'day_of_week': start_time.strftime('%A'),
            'week_number': start_time.isocalendar()[1],
            'day': start_time.day,
            'month': start_time.strftime('%B'),
            'year': start_time.year,
            'hour_of_day': start_time.hour if not all_day else None
        }

        processed_events.append(event_data)

    return pd.DataFrame(processed_events)


def categorize_calendar_events(events_df, batch_size=10):
    events_df_work = (
        events_df
        .loc[(events_df["calendar_name"] == "Pozz Work"), :]
        # .head()
        .groupby(["summary"])
        .size()
        .to_frame("count")
        .sort_values("count", ascending=False)
        .fillna(0)
        .reset_index()
    )

    # batch_size = 70  # puoi aumentare finché non superi i limiti di token
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    results = []
    for i in range(0, len(events_df_work), batch_size):
        batch = events_df_work.iloc[i:i + batch_size]
        batch_categories = classify_batch_openai_api(llm, batch["summary"].tolist(), categories)
        results.extend(batch_categories)

    # Verifica che lunghezze corrispondano
    if len(results) != len(events_df_work):
        raise ValueError(f"Mismatch: {len(results)} results vs {len(events_df)} rows")

    events_df_work["event_category"] = results
    events_df_work["calendar_name"] = "Pozz Work"

    events_df_categorized = (
        events_df
        # .head()
        .merge(events_df_work, on=["calendar_name", "summary"], how="left")
    )

    # events_df_categorized['start_time'] = pd.to_datetime(
    #     events_df_categorized['start_time'],
    #     errors='coerce',
    #     utc=True
    # ).dt.tz_convert(None)

    events_df_categorized['start_time'] = events_df_categorized['start_time'].apply(
        lambda x: x.astimezone(pytz.utc).replace(tzinfo=None) if x is not None and x.tzinfo is not None else x)

    events_df_categorized['year_only'] = events_df_categorized['start_time'].dt.year.astype(str)
    events_df_categorized['year_month'] = events_df_categorized['start_time'].dt.strftime('%Y-%m')
    events_df_categorized['year_month_week'] = events_df_categorized['start_time'].dt.strftime('%Y-%m-') + \
                                               events_df_categorized['week_number'].astype(str).str.zfill(2)

    return events_df_categorized


def classify_batch_openai_api(llm_app, summaries, categories):
    joined = "\n".join([f"{i + 1}. {text}" for i, text in enumerate(summaries)])
    prompt = f"""
Classifica ciascun testo nella seguente lista in **una sola** delle categorie seguenti:
{", ".join(categories)}

Ecco i testi da classificare (uno per riga, preceduto dal numero):

{joined}

Rispondi fornendo solo una lista nel formato:

1. categoria
2. categoria
...
"""
    response = llm_app.invoke(prompt)
    lines = response.content.strip().split("\n")
    # Rimuove numerazione e tiene solo le categorie
    return [line.split(". ", 1)[1].strip() for line in lines if ". " in line]


# Parametri
categories = ["avm-property-value", "avm-meetings", "avm-genertel-poc",
              "finbox-meetings", "finbox-gara-mcc", "finbox-privati",
              "finbox-deploy-affordability", "smart-lending-suite-meetings",
              "side-project-tools-n-pipeline", "dss-best-practices", "other"
              ]

# Definizione dello schema della funzione per OpenAI
CLASSIFY_EVENT_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "classify_events",
        "description": "Classifica una lista di riepiloghi di eventi di calendario in categorie predefinite.",
        "parameters": {
            "type": "object",
            "properties": {
                "classifications": {
                    "type": "array",
                    "description": "Lista di oggetti, ognuno con l'ID originale e la categoria classificata.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "L'ID originale del riepilogo dell'evento."},
                            "category": {
                                "type": "string",
                                "description": "La categoria classificata per l'evento.",
                                "enum": categories # Usa le tue categorie come enum per vincolare la risposta
                            }
                        },
                        "required": ["id", "category"]
                    }
                }
            },
            "required": ["classifications"]
        }
    }
}


def classify_batch_openai_function_calling(llm_app, summaries, categories_list):
    """
    Classifica un batch di riepiloghi di eventi usando le API di OpenAI con Function Calling.
    """
    messages = [
        {"role": "system",
         "content": f"Classifica i riepiloghi degli eventi nelle seguenti categorie: {', '.join(categories_list)}. Se una categoria non è appropriata, usa 'other'."},
        {"role": "user", "content": "Classifica i seguenti riepiloghi:\n" + "\n".join(
            [f"ID {i}: {s}" for i, s in enumerate(summaries)])}
    ]

    try:
        # Nota: La classe ChatOpenAI di langchain potrebbe non supportare direttamente 'tools' o 'tool_choice'
        # nella sua interfaccia `invoke` in modo semplice come la libreria `openai` raw.
        # Per un controllo più granulare e per assicurare l'uso delle tool_calls, potremmo dover usare
        # direttamente l'API client di openai qui, invece di llm_app.invoke().

        # Alternativa 1: Usando la libreria openai direttamente (più robusto per tool_calling)
        client = openai.OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            tools=[CLASSIFY_EVENT_TOOL_SCHEMA],
            tool_choice={"type": "function", "function": {"name": "classify_events"}}  # Forza l'uso della funzione
        )

        tool_calls = response.choices[0].message.tool_calls
        if not tool_calls:
            raise ValueError("Il modello non ha richiamato la funzione 'classify_events'.")

        function_args_str = tool_calls[0].function.arguments
        parsed_args = json.loads(function_args_str)

        # Estrai le classificazioni e mettile in un dizionario per mantenere l'ordine
        category_map = {item["id"]: item["category"] for item in parsed_args.get("classifications", [])}

        # Costruisci la lista dei risultati nell'ordine originale dei summaries
        results = [category_map.get(i, "other") for i in range(len(summaries))]
        return results

    except json.JSONDecodeError as e:
        print(f"Errore nel parsing JSON dai tool_calls: {e}")
        print(f"Risposta raw: {function_args_str}")
        return ["other"] * len(summaries)
    except Exception as e:
        print(f"Errore nella classificazione con OpenAI Function Calling: {e}")
        return ["other"] * len(summaries)


# 2. `classify_batch_huggingface_zero_shot` (Classificazione Zero-Shot con Hugging Face)

# Inizializza il classificatore zero-shot una sola volta
# Questo caricherà il modello la prima volta che la funzione viene chiamata.
# Puoi spostarlo fuori dalla funzione se chiami questa funzione molte volte,
# per evitare di ricaricare il modello.
_zero_shot_classifier = None


def get_zero_shot_classifier():
    global _zero_shot_classifier
    if _zero_shot_classifier is None:
        print("Caricamento del modello Hugging Face per la classificazione zero-shot. Potrebbe richiedere del tempo...")
        _zero_shot_classifier = pipeline("zero-shot-classification",
                                         model="MoritzLaurer/Deberta-v3-large-mnli-fever-anli-ling-wanli")
        print("Modello Hugging Face caricato.")
    return _zero_shot_classifier


def classify_batch_huggingface_zero_shot(summaries, categories_list):
    """
    Classifica un batch di riepiloghi di eventi usando un modello Zero-Shot di Hugging Face.
    """
    classifier = get_zero_shot_classifier()

    # I modelli Zero-Shot di solito restituiscono score di confidenza per tutte le etichette.
    # Selezioniamo la label con il punteggio più alto.
    results = classifier(summaries, candidate_labels=categories_list)

    classified_categories = []
    for res in results:
        # res['labels'][0] è la categoria con lo score più alto
        classified_categories.append(res['labels'][0])

    return classified_categories