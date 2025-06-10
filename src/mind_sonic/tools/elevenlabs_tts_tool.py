import logging
import os
from typing import Any, Type

from crewai.tools import BaseTool
from elevenlabs.client import ElevenLabs
from pydantic import BaseModel, Field

# Set up logging
logger = logging.getLogger(__name__)


class ElevenLabsTextToSpeechInput(BaseModel):
    """Input for the ElevenLabs TTS tool."""

    text: str = Field(
        ...,
        description="The text content to convert to speech.",
    )
    output_file: str = Field(
        ...,
        description='Path to save the output audio file, e.g., settings.OUTPUT_DIR / "podcast_episode.mp3".',
    )
    voice_id: str = Field(
        default="Rachel",
        description="The ID or name of the voice to use (e.g., 'Rachel', 'Adam', or a custom voice ID).",
    )
    model_id: str = Field(
        default="eleven_multilingual_v2",
        description="The ID of the ElevenLabs model to use.",
    )


class ElevenLabsTTSTool(BaseTool):
    """Tool for converting text to speech using the ElevenLabs API.

    This tool uses the ElevenLabs API to generate high-quality speech from text.
    It requires the ELEVENLABS_API_KEY environment variable to be set.
    """

    name: str = "elevenlabs_text_to_speech"
    description: str = "Convert text to a high-quality audio file using a specific voice."
    args_schema: Type[BaseModel] = ElevenLabsTextToSpeechInput
    client: ElevenLabs = Field(default_factory=lambda: ElevenLabs())

    def _run(
        self,
        text: str,
        output_file: str,
        voice_id: str = "Rachel",
        model_id: str = "eleven_multilingual_v2",
    ) -> str:
        """Use the tool."""
        logger.info(
            f"Starting ElevenLabs TTS generation for voice '{voice_id}' and model '{model_id}'"
        )
        try:
            # Ensure the output directory exists
            output_dir = os.path.dirname(output_file)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Generate audio from text
            audio = self.client.generate(text=text, voice=voice_id, model=model_id)

            # Save the generated audio to a file
            with open(output_file, "wb") as f:
                f.write(audio)

            # Verify the output file was created
            if os.path.exists(output_file):
                size = os.path.getsize(output_file)
                success_msg = (
                    f"Successfully generated audio file: {output_file} ({size} bytes)"
                )
                logger.info(success_msg)
                return success_msg
            else:
                error_msg = f"Failed to generate audio file: {output_file}"
                logger.error(error_msg)
                return error_msg

        except Exception as e:
            error_msg = f"Error using ElevenLabs TTS tool: {e}"
            logger.error(error_msg, exc_info=True)
            return error_msg
