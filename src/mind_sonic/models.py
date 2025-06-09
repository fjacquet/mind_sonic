#!/usr/bin/env python
"""
MindSonic Data Models

This module contains the data models used throughout the MindSonic application.
"""

from typing import List
from pydantic import BaseModel, Field


class DocumentState(BaseModel):
    """Stores lists of files by type for processing.

    Each attribute represents a collection of files of a specific type.
    """

    list_txt: List[str] = Field(default_factory=list)
    list_csv: List[str] = Field(default_factory=list)
    list_docx: List[str] = Field(default_factory=list)
    list_html: List[str] = Field(default_factory=list)
    list_md: List[str] = Field(default_factory=list)
    list_pptx: List[str] = Field(default_factory=list)
    list_pdf: List[str] = Field(default_factory=list)
    list_xlsx: List[str] = Field(default_factory=list)


class SonicState(BaseModel):
    """Main state for the SonicFlow.

    Tracks processing state and holds document collections.
    """

    sentence_count: int = 1
    poem: str = ""
    document_state: DocumentState = DocumentState()
