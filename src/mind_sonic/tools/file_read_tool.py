import os
import logging
from typing import Type, Any
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

logger = logging.getLogger(__name__)

class FileReadToolInput(BaseModel):
    """Input for FileReadTool."""
    file_path: str = Field(..., description="The path to the file to be read.")

class FileReadTool(BaseTool):
    name: str = "read_file_content"
    description: str = "Reads the entire content of a specified file."
    args_schema: Type[BaseModel] = FileReadToolInput

    def _run(self, file_path: str) -> str:
        """Reads the content of a file."""
        try:
            if not os.path.exists(file_path):
                return f"Error: File not found at {file_path}"
            
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            logger.info(f"Successfully read {len(content)} characters from {file_path}")
            return content
        except Exception as e:
            logger.error(f"An error occurred while reading the file {file_path}: {e}")
            return f"Error: An error occurred while reading the file: {e}"
