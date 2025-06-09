# PodcastCrew TTS Implementation Documentation

## Overview

This document details the implementation of text-to-speech (TTS) functionality within the PodcastCrew system to enable multilingual podcast production in both English and French.

## Problem Statement

The PodcastCrew class was designed to create podcasts in multiple languages (English and French), but was failing during initialization because:

1. The `OpenAITTSTool` initialization was incorrectly receiving language parameters directly in the constructor
2. The `openai_tts_tool.py` file existed but was empty (0 bytes), causing audio files to be generated but with no actual content

## Solution Implementation

### 1. Fixed OpenAITTSTool Initialization

Modified the PodcastCrew class to correctly initialize `OpenAITTSTool` instances without passing language parameters in the constructor. The language parameter is now passed during tool execution rather than initialization:

```python
# Before (incorrect):
self.tts_tool_en = OpenAITTSTool(language="english")
self.tts_tool_fr = OpenAITTSTool(language="french")

# After (correct):
self.tts_tool_en = OpenAITTSTool()
self.tts_tool_fr = OpenAITTSTool()
```

### 2. Implemented Complete OpenAITTSTool Class

Created a fully-featured implementation of the `OpenAITTSTool` class with the following capabilities:

#### Key Features

- **Language-Aware Voice Selection**: Automatically selects appropriate voices based on language parameter
- **Text Chunking**: Splits long text into manageable chunks to handle OpenAI API token limits
- **Audio Concatenation**: Seamlessly combines audio chunks into a single coherent output
- **Modern API Usage**: Uses current OpenAI API patterns instead of deprecated methods

#### Code Structure

- `TextToSpeechInput`: Pydantic model for validating input parameters
- `OpenAITTSTool`: Main tool class inheriting from `BaseTool`
- `LANGUAGE_VOICE_MAP`: Class variable mapping languages to appropriate voices
- Helper methods for chunking, processing, and combining audio

### 3. Fixed Import Paths

Corrected the import path for BaseTool from:

```python
from crewai_tools import BaseTool  # Incorrect
```

to:

```python
from crewai.tools import BaseTool  # Correct
```

## Usage

The PodcastCrew uses separate TTS tool instances for English and French:

1. `tts_tool_en`: Used by the `podcast_speaker` agent for English content
2. `tts_tool_fr`: Used by the `podcast_speaker_french` agent for French content

The language parameter is specified in the task configuration and passed during tool execution.

## Technical Details

### Language-Voice Mapping

OpenAI voices have been mapped to languages for optimal results:

```python
LANGUAGE_VOICE_MAP = {
    "english": "alloy",
    "en": "alloy",
    "french": "nova", 
    "fr": "nova",
    # Additional languages...
}
```

### Text Chunking Algorithm

Long texts are split by:

1. First trying to split on paragraph boundaries (`\n\n`)
2. If paragraphs are too long, splitting on sentence boundaries (`.`)
3. If sentences are still too long, including them as-is

### Audio Processing

Audio processing uses the `pydub` library for:

1. Loading individual audio chunks
2. Concatenating them into a combined audio stream
3. Exporting the final result to the specified output file

## Future Improvements

Potential areas for enhancement:

- Add more sophisticated text chunking that preserves semantic meaning
- Implement caching for repeated TTS requests
- Add audio post-processing options (normalization, noise reduction)
- Support additional output formats beyond MP3

## Dependencies

- openai: For API access to OpenAI's text-to-speech service
- pydub: For audio file manipulation
- crewai: For the base tool functionality and agent framework
