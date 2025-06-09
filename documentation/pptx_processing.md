# PowerPoint (PPTX) Processing in Mind Sonic

This document explains how PowerPoint files are processed in the Mind Sonic application using the custom PowerPointLoader and PowerPointChunker classes.

## Overview

Mind Sonic can index and process PowerPoint (.pptx) files by:

1. Extracting text content from slides
2. Chunking the content appropriately
3. Embedding the chunks in a vector database
4. Making the content available for RAG (Retrieval Augmented Generation)

## Components

### PowerPointLoader

The `PowerPointLoader` class in `mind_sonic/loaders/pptx_loader.py` is responsible for extracting text from PowerPoint files. It:

- Processes each slide in the presentation
- Extracts text from all shapes on each slide
- Formats the output with slide numbers for better context preservation
- Returns data in the specific format required by the embedchain BaseChunker

```python
from mind_sonic.loaders.pptx_loader import PowerPointLoader

loader = PowerPointLoader()
data = loader.load_data("path/to/presentation.pptx")
```

### PowerPointChunker

The `PowerPointChunker` class in `mind_sonic/loaders/pptx_chunker.py` is responsible for splitting the extracted text into appropriate chunks for embedding. It:

- Uses RecursiveCharacterTextSplitter for effective text chunking
- Sets data_type to DataType.CUSTOM for proper handling in embedchain
- Provides detailed logging for debugging and monitoring
- Preserves slide structure in chunks when possible

```python
from mind_sonic.loaders.pptx_chunker import PowerPointChunker

chunker = PowerPointChunker()
chunks = chunker.create_chunks(loader, "path/to/presentation.pptx", app_id="default-app-id")
```

## Integration with IndexerCrew

The `IndexerCrew` class in `mind_sonic/crews/indexer_crew/indexer_crew.py` uses these components to process PPTX files:

```python
def process_file(self, input_data):
    file = input_data["file"]
    datatype = get_embedchain_data_type(file) or input_data["suffix"]
    
    if datatype == "custom" and file.lower().endswith((".pptx", ".ppt")):
        from mind_sonic.loaders.pptx_loader import PowerPointLoader
        from mind_sonic.loaders.pptx_chunker import PowerPointChunker
        
        loader = PowerPointLoader()
        chunker = PowerPointChunker()
        
        self.rag_tool.add(source=file, data_type=datatype, loader=loader, chunker=chunker)
    else:
        self.rag_tool.add(source=file, data_type=datatype)
        
    return f"Processed {file} of type {datatype}"
```

## Important Implementation Details

### PowerPointLoader Format

The PowerPointLoader returns data in the following format, which is required by the BaseChunker:

```python
{
    "data": [{
        "content": "extracted text content",
        "meta_data": {
            "source": "file path",
            "file_type": "pptx",
            "slide_count": number_of_slides,
            "url": "file path"  # BaseChunker expects a url in metadata
        }
    }],
    "doc_id": "unique document identifier"
}
```

### PowerPointChunker Requirements

The PowerPointChunker must:

1. Be initialized with a text_splitter
2. Have its data_type set to DataType.CUSTOM
3. Override the get_chunks method to handle the loader output format

## Troubleshooting

Common issues:

1. **"BaseChunker.**init**() missing 1 required positional argument: 'text_splitter'"**  
   Solution: Ensure the PowerPointChunker is initialized with a text_splitter.

2. **"'NoneType' object has no attribute 'value'"**  
   Solution: Ensure the data_type is set using set_data_type(DataType.CUSTOM).

3. **"list indices must be integers or slices, not str"**  
   Solution: Ensure the PowerPointLoader returns data in the correct format with "data" and "doc_id" keys.

## Flow

1. SonicFlow.index_pptx calls process_files with PPTX files
2. process_files uses IndexerCrew to process files
3. IndexerCrew.process_file creates PowerPointLoader and PowerPointChunker
4. PowerPointLoader extracts text from PPTX slides
5. PowerPointChunker splits content into chunks
6. RAG tool adds chunks to vector database
7. Processed files are archived
