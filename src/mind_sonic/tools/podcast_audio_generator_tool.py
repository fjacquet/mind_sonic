"""
Podcast Audio Generator Tool - A simplified wrapper around OpenAITTSTool for agents.
This tool handles all the file reading and error handling internally,
making it much easier for agents to use.
"""

import os
import logging
from typing import Any, Optional, Type
from pydantic import BaseModel, Field

from crewai.tools import BaseTool
from mind_sonic.tools.openai_tts_tool import OpenAITTSTool
from mind_sonic.tools.elevenlabs_tts_tool import ElevenLabsTTSTool

logger = logging.getLogger(__name__)

class PodcastAudioGeneratorInput(BaseModel):
    """Input for the PodcastAudioGeneratorTool."""

    podcast_script: str = Field(..., description="The podcast script to be converted to audio.")
    output_file: str = Field(
        ...,
        description='Path to save the output audio file, e.g., settings.OUTPUT_DIR / "podcast_delivery.mp3".',
    )
    voice: str = Field(
        default="alloy",
        description="The voice to use. For OpenAI: 'alloy', 'shimmer', etc. For ElevenLabs: 'Rachel', 'Adam', etc.",
    )
    tts_provider: str = Field(
        default="openai",
        description="The TTS provider to use: 'openai' or 'elevenlabs'.",
    )
    model: str = Field(default="tts-1", description="TTS model to use")

class PodcastAudioGeneratorTool(BaseTool):
    """A tool to generate podcast audio from a script using a specified TTS provider.

    This tool delegates the actual TTS generation to a specific TTS tool like OpenAITTSTool or ElevenLabsTTSTool.
    """

    name: str = "podcast_audio_generator"
    description: str = "Generates podcast audio from a script using a selected TTS provider."
    args_schema: Type[BaseModel] = PodcastAudioGeneratorInput

    def _run(
        self,
        podcast_script: str,
        output_file: str,
        voice: str,
        tts_provider: str = "openai",
    ) -> str:
        """Use the tool."""
        logger.info(f"Generating podcast audio via {tts_provider.upper()} for script: {podcast_script[:100]}...")

        try:
            if tts_provider.lower() == "elevenlabs":
                tts_tool = ElevenLabsTTSTool()
                # For ElevenLabs, the 'voice' parameter is used as 'voice_id'
                return tts_tool.run(
                    text=podcast_script, output_file=output_file, voice_id=voice
                )
            elif tts_provider.lower() == "openai":
                tts_tool = OpenAITTSTool()
                return tts_tool.run(
                    text=podcast_script, output_file=output_file, voice=voice
                )
            else:
                return f"Error: Unsupported TTS provider '{tts_provider}'. Please use 'openai' or 'elevenlabs'."

        except Exception as e:
            error_msg = f"Error generating podcast audio with {tts_provider.upper()}: {e}"
            logger.error(error_msg, exc_info=True)
            return error_msg
