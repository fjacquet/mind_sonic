#!/usr/bin/env python
"""
File Processing Utilities

This module contains utilities for processing files of various types.
"""

from pathlib import Path
from typing import List
import logging

from mind_sonic.crews.indexer_crew.indexer_crew import IndexerCrew
from mind_sonic.utils.file_archiver import archive_files

logger = logging.getLogger(__name__)


def process_files(file_list: List[str], file_type: str) -> None:
    """Process files of a specific type.

    Args:
        file_list: List of files to process
        file_type: Type of files being processed
    """
    logger.info("Starting processing for %s files", file_type)
    
    indexer = IndexerCrew()  # Instantiate IndexerCrew once outside the loop
    
    for file in file_list:
        logger.info("Processing file: %s", Path(file).name)
        try:
            input_data = {"file": file, "suffix": file_type}
            result = indexer.process_file(input_data)
            logger.info("Result for %s: %s", Path(file).name, result)
            archive_files(file)
        except Exception as e:
            logger.error("Error processing file %s: %s", Path(file).name, e, exc_info=True)
