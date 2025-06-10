import os
import tempfile
import uuid
import logging
from typing import Any, ClassVar, Dict, List, Optional

import openai
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# Set up logging
logger = logging.getLogger(__name__)


class TextToSpeechInput(BaseModel):
    """Input for the OpenAI TTS tool."""

    text: str = Field(
        ...,
        description="The full text content to convert to speech. For podcast scripts, this should be the entire script content.",
    )
    output_file: str = Field(
        ...,
        description='Path to save the output audio file. For podcasts, construct this path using the configured output directory (e.g., settings.OUTPUT_DIR / "your_podcast_audio_en.mp3" or settings.OUTPUT_DIR / "your_podcast_audio_fr.mp3").',
    )
    language: str = Field(
        default="english",
        description="Language of the text: 'english' or 'french' for podcasts",
    )
    voice: Optional[str] = Field(
        default=None,
        description="Voice to use for TTS (leave empty to auto-select based on language)",
    )
    model: str = Field(
        default="tts-1", description="TTS model to use, 'tts-1' is recommended"
    )
    response_format: str = Field(
        default="mp3", description="Audio format for the output, keep as 'mp3'"
    )
    speed: float = Field(
        default=1.0, description="Speed of the speech, 1.0 is normal speed"
    )


class OpenAITTSTool(BaseTool):
    """Tool for converting text to speech using OpenAI's API with language-aware voice selection.

    This tool uses OpenAI's TTS API to convert text to speech, with automatic voice selection
    based on the specified language. It handles chunking long texts to fit within OpenAI's token
    limits and concatenates the resulting audio chunks into a single output file.

    The tool is designed to be used by agents in the PodcastCrew system to generate
    audio content in multiple languages from text scripts without manually specifying voices.

    INSTRUCTIONS FOR PODCAST AGENTS:
    1. FIRST, read the full script content from the file (e.g., from a path like settings.OUTPUT_DIR / "podcast_script.md").

    2. THEN, call this tool with the ENTIRE script content:
       - Set output_file to a path within the configured output directory (e.g., settings.OUTPUT_DIR / "your_podcast_audio_en.mp3").
       - Set language to 'english' or 'french' accordingly.
       - Use model='tts-1'.

    3. VERIFY the audio file was created successfully after calling this tool.
    """

    name: str = "openai_text_to_speech"
    description: str = (
        "Convert text (like podcast scripts) to speech audio files. For podcasts, first read the script file, then pass the entire content to this tool."
    )
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

    MAX_CHUNK_SIZE: int = 4000

    def _run(
        self,
        text: str,
        output_file: str,
        language: str = "english",
        voice: Optional[str] = None,
        model: str = "tts-1",
        response_format: str = "mp3",
        speed: float = 1.0,
    ) -> str:
        """Convert text to speech using OpenAI's API.

        Args:
            text: Text to convert to speech
            output_file: Path to save the output audio file
            language: Language of the text (e.g., 'english', 'french')
            voice: Voice to use for TTS (if not specified, will use default based on language)
            model: TTS model to use
            response_format: Audio format for the output
            speed: Speed of the speech

        Returns:
            Path to the saved audio file or error message
        """
        try:
            # Validate inputs
            if not text or not text.strip():
                error_msg = "Error: Empty text provided. Please provide text content to convert to speech."
                logger.error(error_msg)
                return error_msg

            if len(text) < 10:  # Very short text is likely an error
                logger.warning(
                    f"Warning: Very short text provided ({len(text)} chars). This might be incomplete."
                )

            logger.info(f"Converting text ({len(text)} chars) to speech")
            logger.info(f"Output file: {output_file}")
            logger.info(f"Language: {language}")
            logger.info(f"Model: {model}")

            # Select voice based on language if not specified
            if not voice:
                voice = self._select_voice_for_language(language)
                logger.info(f"Selected voice '{voice}' for language '{language}'")

            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)

            # Process text in chunks if needed
            if len(text) > self.MAX_CHUNK_SIZE:
                return self._process_chunks(
                    text, output_file, language, voice, model, response_format, speed
                )

            # Convert text to speech using OpenAI API
            response = openai.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
                response_format=response_format,
                speed=speed,
            )

            # Save audio to file
            with open(output_file, "wb") as file:
                file.write(response.content)

            # Verify the file was created successfully
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                if file_size < 1000:  # Less than 1KB is suspicious
                    logger.warning(
                        f"Warning: Audio file is very small ({file_size} bytes). It may not contain proper audio."
                    )
                logger.info(
                    f"Audio file created successfully: {output_file} ({file_size} bytes)"
                )
                return f"Audio saved to {output_file} ({file_size} bytes)"
            else:
                error_msg = f"Error: Failed to create audio file at {output_file}"
                logger.error(error_msg)
                return error_msg

        except Exception as e:
            error_msg = f"Error generating audio: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def _select_voice_for_language(self, language: str) -> str:
        """Select voice based on language."""
        language = language.lower()
        return self.LANGUAGE_VOICE_MAP.get(language, "alloy")

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

        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks

    def _process_chunks(
        self,
        text: str,
        output_file: str,
        language: str = "english",
        voice: Optional[str] = None,
        model: str = "tts-1",
        response_format: str = "mp3",
        speed: float = 1.0,
    ) -> str:
        """Process multiple text chunks and concatenate them into a single audio file.

        Args:
            text: Text to convert to speech (will be chunked)
            output_file: Path to save the final audio file
            language: Language of the text
            voice: Voice to use (if None, will be selected based on language)
            model: TTS model to use
            response_format: Audio format for output
            speed: Speed of speech

        Returns:
            Path to the saved audio file or error message
        """
        try:
            # Import here to avoid dependency issues if pydub is not installed
            from pydub import AudioSegment

            # Chunk the text
            chunks = self._chunk_text(text, self.MAX_CHUNK_SIZE)
            logger.info(f"Processing {len(chunks)} chunks for concatenation")

            # Select voice based on language if not specified
            if voice is None:
                voice = self._select_voice_for_language(language)
                logger.info(f"Selected voice '{voice}' for language '{language}'")

            # Initialize empty audio
            combined_audio = AudioSegment.silent(duration=0)
            temp_files = []

            for i, chunk in enumerate(chunks):
                # Create temp file for each chunk with unique name
                temp_file = f"{output_file}.chunk{i}.{response_format}"
                temp_files.append(temp_file)

                try:
                    logger.info(
                        f"Processing chunk {i+1}/{len(chunks)} ({len(chunk)} chars)"
                    )

                    # Generate audio for this chunk using OpenAI API
                    response = openai.audio.speech.create(
                        model=model,
                        voice=voice,
                        input=chunk,
                        response_format=response_format,
                        speed=speed,
                    )

                    # Save chunk to temp file
                    with open(temp_file, "wb") as file:
                        file.write(response.content)

                    # Verify the file was created and has content
                    if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                        file_size = os.path.getsize(temp_file)
                        logger.info(
                            f"Successfully saved chunk {i+1} to {temp_file} ({file_size} bytes)"
                        )

                        # Add to combined audio
                        audio_chunk = AudioSegment.from_file(
                            temp_file, format=response_format
                        )
                        combined_audio += audio_chunk
                    else:
                        logger.warning(
                            f"Warning: Temp file {temp_file} was not created or is empty"
                        )
                except Exception as e:
                    logger.error(f"Error processing chunk {i+1}: {str(e)}")

            # Export combined audio
            logger.info(
                f"Exporting combined audio ({len(combined_audio)/1000:.2f} seconds) to {output_file}"
            )
            combined_audio.export(output_file, format=response_format)

            file_size = (
                os.path.getsize(output_file) if os.path.exists(output_file) else 0
            )
            logger.info(f"Successfully exported to {output_file} ({file_size} bytes)")

            return f"Audio saved to {output_file} ({file_size} bytes)"

        except Exception as e:
            error_msg = f"Error in chunk processing: {str(e)}"
            logger.error(error_msg)
            return error_msg

        finally:
            # Clean up temp files
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                        logger.debug(f"Removed temporary file {temp_file}")
                except Exception as e:
                    logger.warning(f"Error removing temp file {temp_file}: {str(e)}")
