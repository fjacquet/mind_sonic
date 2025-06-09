#!/usr/bin/env python
"""
File Finding Utilities

This module contains utilities for finding files of various types.
"""

import os
import glob
from pathlib import Path

from mind_sonic.models import DocumentState


def find_files(knowledge_dir: str, document_state: DocumentState) -> DocumentState:
    """Find files of various types in the knowledge directory.

    Args:
        knowledge_dir: Path to the knowledge directory
        document_state: State object to populate with file lists

    Returns:
        Updated document state with file lists
    """
    knowledge_path = Path(knowledge_dir)

    if not os.path.exists(knowledge_path):
        return document_state

    # Define file types to search for
    file_types = {
        "txt": document_state.list_txt,
        "csv": document_state.list_csv,
        "docx": document_state.list_docx,
        "html": document_state.list_html,
        "md": document_state.list_md,
        "pdf": document_state.list_pdf,
        "pptx": document_state.list_pptx,
        "xlsx": document_state.list_xlsx,
    }

    # Find files for each type
    for file_type, file_list in file_types.items():
        type_dir = knowledge_path / file_type
        if os.path.exists(type_dir):
            pattern = os.path.join(str(type_dir), "**", f"*.{file_type}")
            setattr(
                document_state, f"list_{file_type}", glob.glob(pattern, recursive=True)
            )

    return document_state
