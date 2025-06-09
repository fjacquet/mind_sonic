DEFAULT_RAG_CONFIG = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4.1-mini",
            "temperature": 0.7,
            "max_tokens": 1000,
        },
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-large",
        },
    },
    "vectordb": {
        "provider": "chroma",
        "config": {
            "collection_name": "mind_sonic",
            "dir": "./storage/chroma",
            "allow_reset": True,
        },
    },
    "chunker": {
        "chunk_size": 400,
        "chunk_overlap": 100,
        "length_function": "len",
        "min_chunk_size": 0,
    },
}
