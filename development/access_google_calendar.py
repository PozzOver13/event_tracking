import os
import datetime
import json

import pandas as pd
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter









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
    # Esegui con un periodo di 90 giorni
    df, docs = main(90)
    print(f"Dataset creato con {len(df)} eventi e {len(docs)} documenti LangChain")