#!/usr/bin/env python
"""
MindSonic Data Models

This module contains the data models used throughout the MindSonic application.
"""
from typing import List
from pydantic import BaseModel


class DocumentState(BaseModel):
    """Stores lists of files by type for processing.
    
    Each attribute represents a collection of files of a specific type.
    """
    list_txt: List[str] = []
    list_csv: List[str] = []
    list_docx: List[str] = []
    list_html: List[str] = []
    list_md: List[str] = []
    list_pdf: List[str] = []
    list_xlsx: List[str] = []


class SonicState(BaseModel):
    """Main state for the SonicFlow.
    
    Tracks processing state and holds document collections.
    """
    sentence_count: int = 1
    poem: str = ""
    document_state: DocumentState = DocumentState()
