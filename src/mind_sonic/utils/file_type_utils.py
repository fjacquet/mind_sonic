#!/usr/bin/env python
"""
File Type Utilities

This module contains utilities for determining file types and formats.
"""
import os
from typing import Optional


def get_embedchain_data_type(file_path: str) -> Optional[str]:
    """
    Maps a file path's suffix to the corresponding Embedchain data type.

    Args:
        file_path: The path to the file.

    Returns:
        A string representing the Embedchain data type (e.g., 'pdf_file', 'doc', 'csv'),
        or None if no direct mapping is found.
    """
    file_path = file_path.lower()  # Convert to lowercase for case-insensitive matching
    _, file_extension = os.path.splitext(file_path)

    # Dictionary for direct suffix-to-type mapping
    suffix_to_type = {
        ".pdf": "pdf_file",
        ".doc": "doc",
        ".docx": "doc",  # Embedchain treats both as 'doc' type
        ".csv": "csv",
        ".json": "json",
        ".xml": "xml",
        ".md": "text",  # Markdown is often treated as plain text or 'mdx'
        ".mdx": "mdx",
        ".txt": "text",
        ".xls": "excel",
        ".xlsx": "excel",
        ".ppt": "powerpoint",
        ".pptx": "powerpoint",
    }

    # Handle directory special case
    if os.path.isdir(file_path):
        return "directory"

    # Handle web pages (URLs) - simple check, might need more robust URL validation
    if file_path.startswith(("http://", "https://")):
        # Specific checks for well-known web data types from URLs
        if "youtube.com" in file_path or "youtu.be" in file_path:
            return "youtube_video"
        if "sitemap.xml" in file_path:
            return "sitemap"
        # Notion URL check (simplified, could be more robust)
        if "notion.so" in file_path:
            return "notion"
        # Default for general web pages if no specific type is matched
        return "web_page"

    # Return the mapped type for known suffixes
    if file_extension in suffix_to_type:
        return suffix_to_type[file_extension]

    # Return None if no mapping is found
    return None
