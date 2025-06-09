#!/usr/bin/env python
"""
PowerPoint Chunker for EmbedChain

This module provides a custom chunker for PowerPoint (PPTX) files.
"""

import logging
from embedchain.chunkers.base_chunker import BaseChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from embedchain.models.data_type import DataType

logger = logging.getLogger(__name__)

# Default chunking parameters
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200


class PowerPointChunker(BaseChunker):
    """Custom chunker for PowerPoint (.pptx) files.

    This chunker is designed to work with the PowerPointLoader to process PowerPoint files
    for embedding and retrieval in a RAG system. It inherits from BaseChunker and customizes
    the chunking process for PowerPoint content.

    The chunker handles the specific format of PowerPoint content, where text is organized
    by slides, and ensures that chunks maintain the slide-based context when possible.

    Key features:
    - Uses RecursiveCharacterTextSplitter for effective text chunking
    - Sets data_type to DataType.CUSTOM for proper handling in embedchain
    - Provides detailed logging for debugging and monitoring
    - Preserves slide structure in chunks when possible

    Usage:
        chunker = PowerPointChunker()
        chunks = chunker.create_chunks(loader, source_file, app_id)
    """

    def __init__(self):
        """Initialize the PowerPoint chunker.

        Creates a text splitter with appropriate chunk size and overlap.
        Sets the data type to CUSTOM to handle PowerPoint files.

        Note: The BaseChunker requires a text_splitter argument during initialization,
        and the data_type must be set using set_data_type() to avoid errors.
        """
        logger.info("Initializing PowerPointChunker")
        # Create a text splitter for chunking the PowerPoint content
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=DEFAULT_CHUNK_SIZE,
            chunk_overlap=DEFAULT_CHUNK_OVERLAP,
            length_function=len,
        )

        # Initialize the base chunker with the text splitter
        super().__init__(text_splitter=text_splitter)

        # Set the data type to CUSTOM for PowerPoint files
        # This is required for the BaseChunker to properly handle the data
        self.set_data_type(DataType.CUSTOM)
        logger.info(
            "PowerPointChunker initialized successfully with data_type: %s",
            self.data_type,
        )

    def get_chunks(self, loader_output, config=None):
        """Get chunks from loader output.

        This method processes the output from the PowerPointLoader and splits it into
        chunks suitable for embedding. It uses the text_splitter configured during
        initialization to create appropriately sized chunks while preserving context.

        The method handles the specific format returned by PowerPointLoader and ensures
        that the metadata is properly preserved in each chunk.

        Args:
            loader_output: Output from the PowerPointLoader containing content and metadata
            config: Optional ChunkerConfig with chunking parameters

        Returns:
            List of chunks, where each chunk is a dictionary with 'content' and 'metadata' keys

        Raises:
            Exception: If there's an error during the chunking process
        """
        logger.info("PowerPointChunker.get_chunks called")

        # Extract content and metadata
        content_text = loader_output.get("content", "")
        metadata = loader_output.get("metadata", {})

        # Log the content and metadata for debugging
        logger.info("Content length: %d", len(content_text))
        logger.info("Metadata: %s", metadata)

        # Split content into chunks using the text splitter
        chunks = []
        try:
            # Create chunks using the text splitter
            # The text_splitter.create_documents method splits the text and preserves metadata
            split_docs = self.text_splitter.create_documents(
                [content_text], metadatas=[metadata]
            )

            # Convert the split documents to the expected format
            for doc in split_docs:
                chunks.append({"content": doc.page_content, "metadata": doc.metadata})

            logger.info("Successfully created %d chunks", len(chunks))
        except Exception as e:
            logger.error("Error creating chunks: %s", str(e))
            raise

        return chunks

    def create_chunks(self, loader, src, app_id=None, config=None, **kwargs):
        """Override create_chunks to add logging and error handling.

        This method extends the parent class's create_chunks method with additional
        logging and error handling. It calls the BaseChunker's create_chunks method,
        which in turn will call our custom get_chunks method to process the content.

        The method provides detailed logging about the chunking process, including:
        - The source file being processed
        - The type of loader being used
        - The structure of the data returned by the loader
        - The number of chunks created
        - Any errors that occur during processing

        Args:
            loader: The loader instance (PowerPointLoader) used to load the data
            src: Path to the source file
            app_id: Application ID for the embedchain app
            config: Optional chunking configuration
            **kwargs: Additional keyword arguments passed to the loader

        Returns:
            Dictionary containing the chunked documents and metadata

        Raises:
            Exception: If there's an error during the chunking process
        """
        logger.info(
            "PowerPointChunker.create_chunks called with src: %s, app_id: %s",
            src,
            app_id,
        )
        try:
            # Get loader data
            logger.debug("Loader type: %s", type(loader).__name__)
            data_result = loader.load_data(src, **kwargs)
            logger.debug(
                "Loader data result keys: %s",
                data_result.keys() if isinstance(data_result, dict) else "Not a dict",
            )

            # Now call super().create_chunks with the same parameters
            # The BaseChunker.create_chunks method will call our get_chunks method
            result = super().create_chunks(loader, src, app_id, config, **kwargs)
            logger.info(
                "Successfully created %d chunks", len(result.get("documents", []))
            )
            return result
        except Exception as e:
            logger.error(
                "Error in PowerPointChunker.create_chunks: %s", str(e), exc_info=True
            )
            raise
