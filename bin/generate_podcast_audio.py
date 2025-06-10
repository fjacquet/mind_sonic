#!/usr/bin/env python
"""
Script to directly generate a podcast audio file from an existing script file.
This bypasses the CrewAI framework and directly uses the OpenAITTSTool.

Accepts command-line arguments for input script path, output audio path, language, and model.
"""

import os
import sys
import logging
import argparse # Added for command-line arguments

# Add the project root to the Python path
# Consider running as a module or installing the package for better path management
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from mind_sonic.tools.openai_tts_tool import OpenAITTSTool
from mind_sonic.utils.logging_utils import setup_logging

# Set up logging for this script
logger = setup_logging(component="generate_podcast_audio_script")

def _generate_audio_file(script_path: str, output_path: str, language: str, model: str, tts_tool: OpenAITTSTool):
    """Helper function to generate a single audio file."""
    try:
        if not os.path.exists(script_path):
            logger.error(f"Script file not found: {script_path}")
            return

        with open(script_path, 'r', encoding='utf-8') as file:
            script_content = file.read()
        
        if not script_content.strip():
            logger.error(f"Script file is empty: {script_path}")
            return
            
        logger.info(f"Generating {language} audio from script '{script_path}' ({len(script_content)} chars) to '{output_path}'")
        
        result = tts_tool._run(
            text=script_content,
            output_file=output_path,
            language=language,
            model=model
        )
        
        logger.info(f"{language.capitalize()} audio generation result: {result}")
        
        if os.path.exists(output_path):
            size = os.path.getsize(output_path)
            logger.info(f"{language.capitalize()} audio file created: {output_path}, Size: {size} bytes")
        else:
            # The OpenAITTSTool _run method should return an error string if it fails before file creation,
            # but this is an extra check.
            logger.error(f"Failed to create {language} audio file at: {output_path}. Result from tool: {result}")
            
    except Exception as e:
        logger.error(f"Error generating {language} audio from {script_path} to {output_path}: {e}", exc_info=True)

def main():
    """Main function to parse arguments and generate podcast audio."""
    parser = argparse.ArgumentParser(description="Generate podcast audio from a script file using OpenAITTSTool.")
    parser.add_argument("--script-path", required=True, help="Path to the input script file (e.g., output/podcast_script.md)")
    parser.add_argument("--output-path", required=True, help="Path to save the output audio file (e.g., output/podcast_delivery.mp3)")
    parser.add_argument("--language", required=True, choices=['english', 'french', 'german', 'spanish', 'italian', 'japanese', 'chinese', 'portuguese', 'dutch'], help="Language of the script")
    parser.add_argument("--model", default="tts-1", help="TTS model to use (default: tts-1)")
    
    args = parser.parse_args()
    
    logger.info(f"Starting podcast audio generation with arguments: {args}")
    
    # Initialize a single TTS tool instance
    tts_tool = OpenAITTSTool()
    
    _generate_audio_file(
        script_path=args.script_path,
        output_path=args.output_path,
        language=args.language,
        model=args.model,
        tts_tool=tts_tool
    )
    
    logger.info("Podcast audio generation process finished.")

if __name__ == "__main__":
    main()
