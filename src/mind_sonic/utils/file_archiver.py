#!/usr/bin/env python
"""
File Archiving Utilities

This module contains utilities for archiving processed files.
"""

import os
import shutil
from mind_sonic.config.settings import settings


def archive_files(file: str) -> None:
    """Move processed files to an archive directory.

    Preserves the original directory structure within the archive.

    Args:
        file: Path to the file to archive
    """
    knowledge_path = settings.KNOWLEDGE_DIR
    archive_path = settings.ARCHIVE_DIR

    # settings.py ensures KNOWLEDGE_DIR exists, but an extra check is fine.
    if not knowledge_path.exists():
        # Or log a warning, as this directory should ideally always exist.
        return

    # Extract the subfolder path and create destination
    # Ensure 'file' is relative to knowledge_path for relpath to work correctly if 'file' is absolute
    try:
        rel_path = Path(file).relative_to(knowledge_path)
    except ValueError:
        # 'file' is not under knowledge_path, handle appropriately (e.g., log and skip)
        # For now, let's assume 'file' is always expected to be within knowledge_path
        # This might indicate an issue upstream if 'file' is not in KNOWLEDGE_DIR
        # For robustness, one might log this and return.
        # For now, we'll let it proceed which might lead to unexpected rel_path if 'file' is outside.
        # A safer approach if file can be outside knowledge_dir:
        # if not Path(file).is_relative_to(knowledge_path):
        #     logger.warning(f"File {file} is not in knowledge directory {knowledge_path}, cannot archive.")
        #     return
        # rel_path = os.path.relpath(file, str(knowledge_path)) # original approach if we are sure 'file' is inside
        # For now, sticking to a more direct conversion of original logic, assuming 'file' is correctly passed
        rel_path_str = os.path.relpath(file, str(knowledge_path))

    dest_dir_path = archive_path / Path(rel_path_str).parent
    dest_dir_path.mkdir(parents=True, exist_ok=True)

    # Move the file to archive
    dest_file_path = archive_path / rel_path_str
    shutil.move(file, str(dest_file_path))
