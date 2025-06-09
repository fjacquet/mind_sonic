import os
import tempfile
import uuid
from typing import Any, ClassVar, Dict, List, Optional

import openai
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from pydub import AudioSegment


class TextToSpeechInput(BaseModel):
    """Input for the OpenAI TTS tool."""
    text: str = Field(..., description="Text to convert to speech")
    output_file: str = Field(..., description="Path to save the output audio file")
    language: str = Field(default="english", description="Language of the text (e.g., 'english', 'french')")
    voice: Optional[str] = Field(default=None, description="Voice to use for TTS (if not specified, will use default based on language)")
    model: str = Field(default="tts-1", description="TTS model to use")
    response_format: str = Field(default="mp3", description="Audio format for the output")
    speed: float = Field(default=1.0, description="Speed of the speech")


class OpenAITTSTool(BaseTool):
    """Tool for converting text to speech using OpenAI's API with language-aware voice selection.
    
    This tool enhances the basic OpenAI TTS functionality with several key features:
    - Automatic voice selection based on language input (e.g., English → 'alloy', French → 'nova')
    - Text chunking to handle content that exceeds OpenAI's token limits
    - Automatic audio concatenation for seamless playback of multi-chunk content
    - Proper directory creation and file management
    
    The tool is designed to be used by agents in the PodcastCrew system to generate
    audio content in multiple languages from text scripts without manually specifying voices.
    
    Example usage:
        tts_tool = OpenAITTSTool()
        result = tts_tool.run(
            text="Text to convert to speech",
            output_file="output/audio_file.mp3",
            language="french"  # Will automatically select appropriate French voice
        )
    """
    name: str = "openai_text_to_speech"
    description: str = "Convert text to speech using OpenAI's TTS API with language-aware voice selection"
    args_schema: Any = TextToSpeechInput
    
    # Map languages to appropriate voices
    LANGUAGE_VOICE_MAP: ClassVar[Dict[str, str]] = {
        "english": "alloy",
        "en": "alloy",
        "french": "nova",
        "fr": "nova",
        "german": "onyx",
        "de": "onyx",
        "spanish": "shimmer",
        "es": "shimmer",
        "italian": "echo",
        "it": "echo",
        "japanese": "nova",
        "ja": "nova",
        "chinese": "shimmer",
        "zh": "shimmer",
        "portuguese": "alloy",
        "pt": "alloy",
        "dutch": "fable",
        "nl": "fable",
    }
    
    def _run(
        self, text: str, output_file: str, language: str = "english", voice: Optional[str] = None, 
        model: str = "tts-1", response_format: str = "mp3", speed: float = 1.0
    ) -> str:
        """Convert text to speech and save to a file.
        
        Args:
            text: Text to convert to speech
            output_file: Path to save the output audio file
            language: Language of the text (e.g., 'english', 'french')
            voice: Voice to use for TTS (if not specified, will use default based on language)
            model: TTS model to use
            response_format: Audio format for the output
            speed: Speed of the speech
            
        Returns:
            Path to the saved audio file
        """
        language = language.lower()
        
        # Select voice based on language if not specified
        if not voice:
            voice = self.LANGUAGE_VOICE_MAP.get(language, "alloy") 
            print(f"Selected voice '{voice}' for language '{language}'")
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
        
        # Check if text needs to be chunked (OpenAI has a token limit)
        chunks = self._chunk_text(text)
        
        if len(chunks) > 1:
            print(f"Text exceeds token limit. Splitting into {len(chunks)} chunks.")
            self._process_chunks(chunks, output_file, model, voice, response_format, speed)
        else:
            self._process_single(text, output_file, model, voice, response_format, speed)
        
        return f"Audio saved to {output_file}"
    
    def _chunk_text(self, text: str, max_chars: int = 4000) -> List[str]:
        """Split text into semantically appropriate chunks that respect OpenAI's token limits.
        
        This method implements a hierarchical chunking strategy that attempts to preserve
        natural language boundaries while staying within the specified character limit:
        1. First tries to split at paragraph breaks (\n\n)
        2. If paragraphs exceed the limit, splits at sentence boundaries (. )
        3. If sentences exceed the limit, includes them as-is
        
        Args:
            text: The text content to split into appropriate chunks
            max_chars: Maximum number of characters per chunk (default 4000 approximates OpenAI's limit)
            
        Returns:
            List of text chunks ready for processing by the TTS API
        
        Note:
            The actual token limit depends on the model used. This character-based approximation
            is simpler but may not perfectly match OpenAI's token counting for all languages.
        """
        # Simple character-based chunking for now
        # A more sophisticated approach would consider sentence boundaries
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        paragraphs = text.split("\n\n")
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 2 <= max_chars:  # +2 for newlines
                if current_chunk:
                    current_chunk += "\n\n"
                current_chunk += paragraph
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                # If a single paragraph is longer than max_chars, split it by sentences
                if len(paragraph) > max_chars:
                    sentences = paragraph.split(". ")
                    current_chunk = ""
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) + 2 <= max_chars:
                            if current_chunk:
                                current_chunk += ". "
                            current_chunk += sentence
                        else:
                            if current_chunk:
                                chunks.append(current_chunk + ".")
                            # If a single sentence is still too long, just add it as is
                            if len(sentence) > max_chars:
                                chunks.append(sentence + ".")
                                current_chunk = ""
                            else:
                                current_chunk = sentence
                    if current_chunk:
                        chunks.append(current_chunk + ".")
                    current_chunk = ""
                else:
                    current_chunk = paragraph
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _process_chunks(self, chunks: List[str], output_file: str, model: str, voice: str, 
                        response_format: str, speed: float) -> None:
        """Process multiple text chunks and concatenate them into a single seamless audio file.
        
        This method handles the workflow for processing long text content:
        1. Creates temporary files for each chunk's audio output
        2. Processes each text chunk individually via OpenAI's TTS API
        3. Loads and concatenates all audio chunks using pydub
        4. Exports the final combined audio to the requested output file
        5. Cleans up all temporary files
        
        Args:
            chunks: List of text chunks to process (from _chunk_text method)
            output_file: Path where the final concatenated audio will be saved
            model: TTS model identifier (e.g., 'tts-1')
            voice: Voice identifier to use (e.g., 'alloy', 'nova')
            response_format: Audio format extension (e.g., 'mp3')
            speed: Speech speed multiplier (e.g., 1.0 for normal speed)
            
        Notes:
            - Uses temporary files with unique names to avoid conflicts
            - Includes proper cleanup in a finally block to ensure temp files are removed
            - Uses pydub's AudioSegment for audio manipulation
        """
        combined_audio = AudioSegment.empty()
        temp_files = []
        
        try:
            for i, chunk in enumerate(chunks):
                # Create temp file for each chunk
                with tempfile.NamedTemporaryFile(suffix=f".{response_format}", delete=False) as temp:
                    temp_file = temp.name
                    temp_files.append(temp_file)
                
                # Generate audio for this chunk
                self._process_single(chunk, temp_file, model, voice, response_format, speed)
                
                # Add to combined audio
                audio_chunk = AudioSegment.from_file(temp_file, format=response_format)
                combined_audio += audio_chunk
            
            # Export combined audio
            combined_audio.export(output_file, format=response_format)
        
        finally:
            # Clean up temp files
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except Exception:
                    pass
    
    def _process_single(self, text: str, output_file: str, model: str, voice: str, 
                        response_format: str, speed: float) -> None:
        """Process a single text chunk and save it as an audio file.
        
        This method handles the direct interaction with OpenAI's TTS API to generate
        audio from a single chunk of text (either the full text or a portion of it).
        It's used both directly for short text and as a helper by _process_chunks for longer text.
        
        Args:
            text: The text content to convert to speech
            output_file: Path where the audio file will be saved
            model: TTS model identifier (e.g., 'tts-1', 'tts-1-hd')
            voice: Voice identifier to use (e.g., 'alloy', 'nova', 'shimmer')
            response_format: Audio format to generate (e.g., 'mp3', 'wav')
            speed: Speech speed multiplier (1.0 is normal, 0.5 is half speed, etc.)
            
        Note:
            Uses the modern OpenAI API pattern with direct binary file writing
            rather than the deprecated stream_to_file approach.
        """
        response = openai.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            response_format=response_format,
            speed=speed
        )
        
        # Write the binary content to file
        with open(output_file, "wb") as file:
            file.write(response.content)
