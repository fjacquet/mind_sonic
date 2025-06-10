# MindSonic Configuration Guide

This document outlines the configuration options and settings used throughout the MindSonic project.

## RAG Tool Configuration

The RAG (Retrieval-Augmented Generation) tool is configured with the following settings in the indexer crew:

```python
config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4.1-mini",
            "temperature": 0.7,
            "max_tokens": 1000
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-large"
        }
    },
    "vectordb": {
        "provider": "chroma",
        "config": {
            "collection_name": "mind_sonic",
            "dir": "./storage/chroma",
            "allow_reset": True
        }
    },
    "chunker": {
        "chunk_size": 400,
        "chunk_overlap": 100,
        "length_function": "len",
        "min_chunk_size": 0
    }
}
```

### Configuration Sections

#### LLM Configuration

- `provider`: The provider of the language model (e.g., "openai").
- `config.model`: The specific model to use (e.g., "gpt-4.1-mini").
- `config.temperature`: Controls the randomness of the model's output (0.0 to 1.0).
- `config.max_tokens`: Maximum number of tokens to generate in the response.

#### Embedder Configuration

- `provider`: The provider of the embedding model (e.g., "openai").
- `config.model`: The specific embedding model to use (e.g., "text-embedding-3-large").

#### Vector Database Configuration

- `provider`: The vector database provider (e.g., "chroma").
- `config.collection_name`: The name of the collection in the vector database.
- `config.dir`: The directory where the vector database files are stored.
- `config.allow_reset`: Whether to allow resetting the database.

#### Chunker Configuration

- `chunk_size`: The size of each chunk in tokens.
- `chunk_overlap`: The number of tokens to overlap between chunks.
- `length_function`: The function used to measure token length.
- `min_chunk_size`: The minimum size of a chunk.

## Environment Variables

The following environment variables should be set in your `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## File Structure Configuration

MindSonic expects certain directories to exist for proper operation:

- `knowledge/`: Directory containing files to be processed
  - `txt/`: Text files
  - `csv/`: CSV files
  - `docx/`: Word documents
  - `html/`: HTML files
  - `md/`: Markdown files
  - `pdf/`: PDF files
  - `pptx/`: PowerPoint files
  - `xlsx/`: Excel files
- `archive/`: Directory where processed files are moved after indexing

## Utility Module Structure

The utility functions are organized into separate modules by functionality:

- `file_finder.py`: Functions for finding files of various types
- `file_archiver.py`: Functions for archiving processed files
- `file_processor.py`: Functions for processing different file types

## Customizing Configurations

When modifying configurations, consider the following guidelines:

1. **LLM Models**: Choose models based on your specific needs:

   ```python
   config = {
       "llm": {
           "provider": "openai",
           "config": {
               "model": "gpt-4",  # For higher quality
               # OR
               "model": "gpt-3.5-turbo",  # For faster processing
               "temperature": 0.7,
               "max_tokens": 1000
           }
       }
   }
   ```

2. **Embedder Model**: Select an appropriate embedding model:

   ```python
   config = {
       "embedder": {
           "provider": "openai",
           "config": {
               "model": "text-embedding-3-large",  # High quality embeddings
               # OR
               "model": "text-embedding-3-small"  # Faster, more economical
           }
       }
   }
   ```

3. **Vector Database**: The project currently uses Chroma, but you can switch to other providers:

   ```python
   # For Chroma (default)
   config = {
       "vectordb": {
           "provider": "chroma",
           "config": {
               "collection_name": "mind_sonic",
               "dir": "./storage/chroma",
               "allow_reset": True
           }
       }
   }
   ```
   
   ```python
   # For other providers like Pinecone
   config = {
       "vectordb": {
           "provider": "pinecone",
           "config": {
               "api_key": "your_pinecone_api_key",
               "environment": "your_environment",
               "index_name": "mind_sonic"
           }
       }
   }
   ```

4. **Chunking Strategy**: Adjust based on your content:

   ```python
   # For preserving more context
   config = {
       "chunker": {
           "chunk_size": 800,
           "chunk_overlap": 200,
           "length_function": "len",
           "min_chunk_size": 100
       }
   }
   ```
   
   ```python
   # For more precise retrieval
   config = {
       "chunker": {
           "chunk_size": 300,
           "chunk_overlap": 50,
           "length_function": "len",
           "min_chunk_size": 0
       }
   }
   ```

   - Adjust overlap based on content complexity
