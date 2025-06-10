from crewai.project import CrewBase # Kept CrewBase, removed Agent, Crew, Process, Task, agent, crew, task, BaseAgent
from crewai_tools import RagTool
# from typing import List # List is no longer used
from mind_sonic.rag_config import DEFAULT_RAG_CONFIG

from mind_sonic.utils.file_type_utils import get_embedchain_data_type

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators


@CrewBase
class IndexerCrew:
    """IndexerCrew for processing and indexing files into a vector database.

    This crew is responsible for processing various file types, determining their
    appropriate data type for embedchain, and adding them to the RAG tool's vector database.
    It uses OpenAI models for embeddings and language processing.
    """

    # Create a RAG tool with shared configuration
    config = DEFAULT_RAG_CONFIG
    rag_tool = RagTool(config=config, summarize=True)

    def process_file(self, input_data):
        """Process a file using the RAG tool

        Args:
            input_data (dict): Dictionary containing file information
                - suffix: The file type/suffix
                - file: The file path
        """
        file = input_data["file"]
        datatype = get_embedchain_data_type(file) or input_data["suffix"]

        # Special handling for PowerPoint files
        if datatype == "custom" and file.lower().endswith((".pptx", ".ppt")):
            from mind_sonic.loaders.pptx_loader import PowerPointLoader
            from mind_sonic.loaders.pptx_chunker import PowerPointChunker

            # Create custom loader and chunker for PowerPoint files
            loader = PowerPointLoader()
            chunker = PowerPointChunker()

            # Add the file with custom loader and chunker
            self.rag_tool.add(
                source=file, data_type=datatype, loader=loader, chunker=chunker
            )
        else:
            # Standard processing for other file types
            self.rag_tool.add(source=file, data_type=datatype)

        return f"Processed {file} of type {datatype}"

