#!/usr/bin/env python
"""
MindSonic - A simple file processing flow with CrewAI

This module implements a lightweight flow for processing different file types
and generating a poem using CrewAI. The design follows KISS, YAGNI, and DRY principles.
"""
from typing import List
import argparse
import logging
import os
from datetime import datetime
from pathlib import Path

from crewai.flow import Flow, and_, listen, router, start

from mind_sonic.crews.indexer_crew.indexer_crew import IndexerCrew
from mind_sonic.crews.poem_crew.poem_crew import PoemCrew
from mind_sonic.crews.research_crew.research_crew import ResearchCrew
from mind_sonic.models import DocumentState, SonicState
from mind_sonic.utils.file_finder import find_files
from mind_sonic.utils.file_processor import process_files
from mind_sonic.utils.logging_utils import setup_logging

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)


def read_file(file_path: str) -> str:
    """Read the content of a file and return it as a string."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip()
    

class SonicFlow(Flow[SonicState]):
    """Main flow for processing files and generating a poem.
    
    Follows a simple pattern:
    1. List all files
    2. Process each file type in parallel
    3. Generate a poem when done
    """
    @start()
    def list_files(self):
        """Entry point: find all files to process."""
        logger.info("Listing files")
        document_state = DocumentState()
        self.state.document_state = find_files("knowledge", document_state)

    @router(list_files)
    def start_indexing(self):
        """Route to parallel indexing processes."""
        logger.info("Starting indexing")



    @listen(start_indexing)
    def index_text(self):
        """Process text files."""
        process_files(self.state.document_state.list_txt, "text")

    @listen(start_indexing)
    def index_csv(self):
        """Process CSV files."""
        process_files(self.state.document_state.list_csv, "csv")

    @listen(start_indexing)
    def index_docx(self):
        """Process DOCX files."""
        process_files(self.state.document_state.list_docx, "docx")

    @listen(start_indexing)
    def index_html(self):
        """Process HTML files."""
        process_files(self.state.document_state.list_html, "html")

    @listen(start_indexing)
    def index_md(self):
        """Process Markdown files."""
        process_files(self.state.document_state.list_md, "markdown")

    @listen(start_indexing)
    def index_pdf(self):
        """Process PDF files."""
        process_files(self.state.document_state.list_pdf, "PDF")

    @listen(start_indexing)
    def index_xlsx(self):
        """Process Excel files."""
        process_files(self.state.document_state.list_xlsx, "xlsx")
    
    @listen(
        and_(
            start_indexing,
            index_text,
            index_csv,
            index_docx,
            index_html,
            index_md,
            index_pdf,
            index_xlsx,
        )
    )
    def end_indexing(self):
        """Meeting point after all files are processed."""
        logger.info("Indexing done")


    @listen(end_indexing)
    def start_research(self):
        """Start research after indexing."""

        print("Starting research")
        # Ensure the output directory exists before research begins
        os.makedirs("output", exist_ok=True)

        query = getattr(self, "query", None)
        if query is None:
            request_file = Path(__file__).with_name("request.txt")
            if request_file.exists():
                query = read_file(request_file)
            else:
                query = ""

        inputs = {
            "query": query,
            "current_year": datetime.now().year,
        }

        ResearchCrew().crew().kickoff(inputs=inputs)

        
    @listen(start_research)
    def end_research(self):
        """Generate a poem after research."""
        logger.info("Research done, let's finish with a poem")
        poem = PoemCrew().crew().kickoff()
        self.state.poem = poem
        logger.info(poem)

def kickoff(query: str | None = None) -> None:
    """Start the SonicFlow execution."""
    sonic_flow = SonicFlow()
    if query is not None:
        sonic_flow.query = query
    sonic_flow.kickoff()


def plot() -> None:
    """Generate a visual representation of the flow."""
    sonic_flow = SonicFlow()
    sonic_flow.plot()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the MindSonic flow")
    parser.add_argument(
        "--query",
        help="Research query to override the content of request.txt",
    )
    args = parser.parse_args()

    kickoff(query=args.query)
