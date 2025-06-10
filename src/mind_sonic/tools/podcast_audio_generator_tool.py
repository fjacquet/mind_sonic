"""
Podcast Audio Generator Tool - A simplified wrapper around OpenAITTSTool for agents.
This tool handles all the file reading and error handling internally,
making it much easier for agents to use.
"""

import os
import logging
from typing import Any, Optional
from pydantic import BaseModel, Field

from crewai.tools import BaseTool
from mind_sonic.tools.openai_tts_tool import OpenAITTSTool

logger = logging.getLogger(__name__)

class PodcastAudioInput(BaseModel):
    """Input for the Podcast Audio Generator tool."""
    script_file: str = Field(..., description="Path to the script file to convert to audio")
    output_file: str = Field(..., description="Path to save the output audio file")
    language: str = Field(default="english", description="Language of the script (e.g., 'english', 'french')")
    model: str = Field(default="tts-1", description="TTS model to use")

class PodcastAudioGeneratorTool(BaseTool):
    """Tool for generating podcast audio from script files.
    
    This tool simplifies the process for agents by handling:
    1. Reading the script file
    2. Calling the OpenAI TTS API
    3. Error handling and logging
    4. File path validation
    
    Agents only need to specify the script file path and output file path.
    """
    name: str = "generate_podcast_audio"
    description: str = "Generate podcast audio from a script file"
    args_schema: Any = PodcastAudioInput
    
    def __init__(self):
        """Initialize the tool with an OpenAITTSTool instance."""
        super().__init__()
        self.tts_tool = OpenAITTSTool()
    
    def _run(
        self, script_file: str, output_file: str, 
        language: str = "english", model: str = "tts-1"
    ) -> str:
        """Generate podcast audio from a script file.
        
        Args:
            script_file: Path to the script file to convert to audio
            output_file: Path to save the output audio file
            language: Language of the script (e.g., 'english', 'french')
            model: TTS model to use
            
        Returns:
            Path to the saved audio file or error message
        """
        logger.info(f"Generating podcast audio from {script_file} in {language}")
        
        try:
            # Check if script file exists
            if not os.path.exists(script_file):
                error_msg = f"Script file not found: {script_file}"
                logger.error(error_msg)
                return error_msg
            
            # Read script content
            with open(script_file, 'r', encoding='utf-8') as file:
                script_content = file.read()
                
            if not script_content.strip():
                error_msg = f"Script file is empty: {script_file}"
                logger.error(error_msg)
                return error_msg
                
            logger.info(f"Read {len(script_content)} characters from {script_file}")
            
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            
            # Generate audio using OpenAITTSTool
            result = self.tts_tool._run(
                text=script_content,
                output_file=output_file,
                language=language,
                model=model
            )
            
            # Verify the output file was created
            if os.path.exists(output_file):
                size = os.path.getsize(output_file)
                logger.info(f"Generated audio file: {output_file} ({size} bytes)")
                return f"Successfully generated audio file: {output_file} ({size} bytes)"
            else:
                error_msg = f"Failed to generate audio file: {output_file}"
                logger.error(error_msg)
                return error_msg
                
        except Exception as e:
            error_msg = f"Error generating podcast audio: {str(e)}"
            logger.error(error_msg)
            return error_msg
