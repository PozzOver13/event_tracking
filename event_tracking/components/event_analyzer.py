from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Analisi delle categorie degli eventi
def analyze_event_categories(df):
    """
    Analizza le categorie degli eventi e fornisce un sommario.

    :param df: DataFrame degli eventi
    :return: Dizionario con statistiche delle categorie
    """
    # Conteggio degli eventi per categoria
    category_counts = df['event_category'].value_counts()

    # Calcolo del tempo totale per categoria
    category_duration = df.groupby('event_category')['duration_minutes'].sum()

    # Percentuale di tempo per categoria
    total_time = category_duration.sum()
    category_percentage = (category_duration / total_time * 100).round(2)

    return {
        'counts': category_counts.to_dict(),
        'total_duration': category_duration.to_dict(),
        'percentage': category_percentage.to_dict()
    }

# Interfaccia con Ollama per analisi approfondita
def create_ollama_analyzer(llm_initialized):
    """
    Crea un analizzatore basato su Ollama per interpretazioni più dettagliate.

    :return: Catena LLM per l'analisi
    """

    prompt_template = PromptTemplate(
        input_variables=["categories", "total_time", "top_categories"],
        template="""
        Analizza il seguente profilo temporale degli eventi:
        - Categorie degli eventi: {categories}
        - Tempo totale analizzato: {total_time} minuti
        - Categorie principali: {top_categories}

        Fornisci un'interpretazione dettagliata di come il tempo è stato distribuito,
        evidenziando i pattern più significativi e fornendo eventuali suggerimenti
        per un migliore utilizzo del tempo.
        """
    )

    return LLMChain(llm=llm_initialized, prompt=prompt_template)
