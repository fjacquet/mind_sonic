#!/usr/bin/env python3
"""
Script to convert podcast script to audio using OpenAI's TTS API.
Handles long scripts by splitting them into smaller chunks.
"""

import os
import openai
import tempfile
from pathlib import Path
from pydub import AudioSegment

# Maximum character limit for OpenAI TTS API (conservative estimate)
MAX_CHUNK_SIZE = 4000


def split_text(text, max_length=MAX_CHUNK_SIZE):
    """
    Split text into chunks of maximum length while trying to preserve sentence boundaries.

    Args:
        text: The text to split
        max_length: Maximum length of each chunk

    Returns:
        List of text chunks
    """
    # If text is already short enough, return it as is
    if len(text) <= max_length:
        return [text]

    chunks = []
    current_chunk = ""

    # Split by paragraphs first
    paragraphs = text.split("\n\n")

    for paragraph in paragraphs:
        # If adding this paragraph would exceed the limit
        if len(current_chunk) + len(paragraph) + 2 > max_length:  # +2 for '\n\n'
            # If current_chunk is not empty, add it to chunks
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""

            # If the paragraph itself is too long, split it by sentences
            if len(paragraph) > max_length:
                sentences = (
                    paragraph.replace(". ", ".|")
                    .replace("! ", "!|")
                    .replace("? ", "?|")
                    .split("|")
                )

                for sentence in sentences:
                    if (
                        len(current_chunk) + len(sentence) + 1 > max_length
                    ):  # +1 for space
                        if current_chunk:
                            chunks.append(current_chunk)
                            current_chunk = sentence
                        else:
                            # If a single sentence is too long, split it by words
                            if len(sentence) > max_length:
                                words = sentence.split(" ")
                                for word in words:
                                    if (
                                        len(current_chunk) + len(word) + 1 > max_length
                                    ):  # +1 for space
                                        chunks.append(current_chunk)
                                        current_chunk = word + " "
                                    else:
                                        current_chunk += word + " "
                            else:
                                chunks.append(sentence)
                    else:
                        current_chunk += sentence + " "
            else:
                current_chunk = paragraph
        else:
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph

    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def convert_script_to_audio(script_file, output_file, voice="alloy", model="tts-1"):
    """
    Convert a podcast script to audio using OpenAI's TTS API.
    Handles long scripts by splitting them into smaller chunks.

    Args:
        script_file: Path to the script file
        output_file: Path to save the audio file
        voice: OpenAI voice to use
        model: OpenAI TTS model to use
    """
    print(f"Converting script '{script_file}' to audio...")

    # Read the script content
    with open(script_file, "r", encoding="utf-8") as f:
        script_content = f.read()

    # Split the content into smaller chunks
    chunks = split_text(script_content)
    print(f"Split script into {len(chunks)} chunks")

    # Create OpenAI client
    client = openai.OpenAI()

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Process each chunk and combine the audio
    if len(chunks) == 1:
        # If there's only one chunk, process it directly
        print(f"Using OpenAI TTS with voice '{voice}' and model '{model}'...")
        response = client.audio.speech.create(input=chunks[0], model=model, voice=voice)

        # Save audio to file
        print(f"Saving audio to '{output_file}'...")
        with open(output_file, "wb") as f:
            f.write(response.content)
    else:
        # If there are multiple chunks, process each one and combine them
        combined_audio = None
        temp_files = []

        try:
            for i, chunk in enumerate(chunks):
                print(f"Processing chunk {i + 1}/{len(chunks)}...")

                # Convert chunk to speech
                response = client.audio.speech.create(
                    input=chunk, model=model, voice=voice
                )

                # Save to temporary file
                with tempfile.NamedTemporaryFile(
                    suffix=".mp3", delete=False
                ) as temp_file:
                    temp_file.write(response.content)
                    temp_files.append(temp_file.name)

            # Combine all audio files
            print("Combining audio chunks...")
            combined_audio = AudioSegment.from_mp3(temp_files[0])
            for temp_file in temp_files[1:]:
                audio_segment = AudioSegment.from_mp3(temp_file)
                combined_audio += audio_segment

            # Export the combined audio
            print(f"Saving combined audio to '{output_file}'...")
            combined_audio.export(output_file, format="mp3")

        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except:
                    pass

    print("Conversion complete!")


if __name__ == "__main__":
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Convert script to audio using OpenAI's TTS API"
    )
    parser.add_argument(
        "--script",
        "-s",
        type=str,
        default="output/podcast_script.md",
        help="Path to the script file (default: output/podcast_script.md)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="output/podcast_delivery.mp3",
        help="Path to save the audio file (default: output/podcast_delivery.mp3)",
    )
    parser.add_argument(
        "--voice",
        "-v",
        type=str,
        default="alloy",
        choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        help="OpenAI voice to use (default: alloy)",
    )
    parser.add_argument(
        "--model",
        "-m",
        type=str,
        default="tts-1",
        choices=["tts-1", "tts-1-hd"],
        help="OpenAI TTS model to use (default: tts-1)",
    )

    args = parser.parse_args()

    # Define paths
    script_file = Path(args.script)
    output_file = Path(args.output)

    # Check if script file exists
    if not script_file.exists():
        print(f"Error: Script file '{script_file}' not found!")
        exit(1)

    # Convert script to audio
    convert_script_to_audio(
        script_file, output_file, voice=args.voice, model=args.model
    )
