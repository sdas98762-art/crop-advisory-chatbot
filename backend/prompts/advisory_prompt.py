"""Advisory prompt template with optional weather context injection."""

ADVISORY_WITH_WEATHER_TEMPLATE = """Current weather context for the farmer's location:
{weather_context}

Farmer's question: {question}

Using the weather context above and the knowledge base context, provide weather-aware farming advice.
"""
