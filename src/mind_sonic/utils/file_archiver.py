#!/usr/bin/env python
"""
File Archiving Utilities

This module contains utilities for archiving processed files.
"""

import os
import shutil


def archive_files(file: str) -> None:
    """Move processed files to an archive directory.

    Preserves the original directory structure within the archive.

    Args:
        file: Path to the file to archive
    """
    knowledge_dir = "knowledge"
    archive_dir = "archive"

    if not os.path.exists(knowledge_dir):
        return

    # Extract the subfolder path and create destination
    rel_path = os.path.relpath(file, knowledge_dir)
    dest_dir = os.path.join(archive_dir, os.path.dirname(rel_path))
    os.makedirs(dest_dir, exist_ok=True)

    # Move the file to archive
    dest_file = os.path.join(archive_dir, rel_path)
    shutil.move(file, dest_file)
