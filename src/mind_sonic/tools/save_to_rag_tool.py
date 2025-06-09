from typing import Optional, Type

from crewai_tools import RagTool
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from mind_sonic.rag_config import DEFAULT_RAG_CONFIG


class SaveToRagInput(BaseModel):
    """Input schema for SaveToRagTool."""

    text: str = Field(..., description="Text to store in the vector database")


class SaveToRagTool(BaseTool):
    """Tool that saves arbitrary text into the project's RAG database."""

    name: str = "SaveToRag"
    description: str = "Persist text so it can be retrieved later via the RAG tool."
    args_schema: Type[BaseModel] = SaveToRagInput

    def __init__(self, rag_tool: Optional[RagTool] = None) -> None:
        super().__init__()
        self.rag_tool = rag_tool or RagTool(config=DEFAULT_RAG_CONFIG, summarize=True)

    def _run(self, text: str) -> str:
        self.rag_tool.add(source=text, data_type="text")
        return "stored"
