#!/usr/bin/env python
"""
File Processing Utilities

This module contains utilities for processing files of various types.
"""
from pathlib import Path
from typing import List

from mind_sonic.crews.indexer_crew.indexer_crew import IndexerCrew
from mind_sonic.utils.file_archiver import archive_files


def process_files(file_list: List[str], file_type: str) -> None:
    """Process files of a specific type.
    
    Args:
        file_list: List of files to process
        file_type: Type of files being processed
    """
    print(f"Indexing {file_type}")
    for file in file_list:
        print(Path(file).name)
        try:
            indexer = IndexerCrew()
            result = indexer.process_file({"file": file, "suffix": file_type})
            print(result)
            archive_files(file)
        except Exception as e:
            print(f"Error indexing {file}: {e}")
