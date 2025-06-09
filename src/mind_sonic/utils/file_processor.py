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
    logger.info("Indexing %s", file_type)
    for file in file_list:
        logger.info(Path(file).name)
        try:
            indexer = IndexerCrew()
            result = indexer.process_file({"file": file, "suffix": file_type})
            logger.info(result)
            archive_files(file)
        except Exception as e:
            logger.error("Error indexing %s: %s", file, e)
