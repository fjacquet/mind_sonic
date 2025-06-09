import logging
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List, Optional

from mind_sonic.tools.openai_tts_tool import OpenAITTSTool
from mind_sonic.tools.save_to_rag_tool import SaveToRagTool
from crewai_tools import RagTool
from mind_sonic.utils.logging_utils import log_function_call

# Set up logger
logger = logging.getLogger(__name__)


@CrewBase
class PodcastCrew:
    """PodcastCrew for podcast delivery in multiple languages"""

    agents: List[BaseAgent]
    tasks: List[Task]
    logger = logger  # Use the module-level logger

    # Tools
    rag_tool: Optional[RagTool] = None
    save_tool: Optional[SaveToRagTool] = None
    tts_tool_en: Optional[OpenAITTSTool] = None
    tts_tool_fr: Optional[OpenAITTSTool] = None

    def __init__(self):
        """Initialize the PodcastCrew and set up tools"""
        super().__init__()
        self.setup_tools()

    def setup_tools(self) -> None:
        """Set up tools for the crew"""
        self.logger.info("Setting up tools for PodcastCrew")

        # Initialize RAG tool if not already created
        if self.rag_tool is None:
            self.rag_tool = RagTool()

        # Initialize Save to RAG tool if not already created
        if self.save_tool is None:
            self.save_tool = SaveToRagTool(rag_tool=self.rag_tool)

        # Initialize TTS tools for English and French if not already created
        if self.tts_tool_en is None:
            self.tts_tool_en = OpenAITTSTool()

        if self.tts_tool_fr is None:
            self.tts_tool_fr = OpenAITTSTool()

    @agent
    @log_function_call(logger)
    def podcast_speaker(self) -> Agent:
        """Create podcast speaker agent for English content"""
        self.logger.info("Creating podcast speaker agent (English)")
        return Agent(
            config=self.agents_config["podcast_speaker"],  # type: ignore[index]
            tools=[
                self.rag_tool,
                self.tts_tool_en,  # Use English TTS tool
                self.save_tool,
            ],
            allow_delegation=False,
            verbose=True,
            reasoning=True,
            max_reasoning_attempts=5,
        )

    @agent
    @log_function_call(logger)
    def translator(self) -> Agent:
        """Create translator agent for converting English to French"""
        self.logger.info("Creating translator agent (English to French)")
        return Agent(
            config=self.agents_config["translator"],  # type: ignore[index]
            tools=[
                self.rag_tool,
                self.save_tool,
            ],
            allow_delegation=False,
            verbose=True,
            reasoning=True,
            max_reasoning_attempts=5,
        )

    @agent
    @log_function_call(logger)
    def podcast_speaker_french(self) -> Agent:
        """Create podcast speaker agent for French content"""
        self.logger.info("Creating podcast speaker agent (French)")
        return Agent(
            config=self.agents_config["podcast_speaker_french"],  # type: ignore[index]
            tools=[
                self.rag_tool,
                self.tts_tool_fr,  # Use French TTS tool with recommended French voices
                self.save_tool,
            ],
            allow_delegation=False,
            verbose=True,
            reasoning=True,
            max_reasoning_attempts=5,
        )

    @task
    @log_function_call(logger)
    def podcast_task(self) -> Task:
        """Create task for English podcast delivery"""
        return Task(
            config=self.tasks_config["podcast_task"],  # type: ignore[index]§
        )

    @task
    @log_function_call(logger)
    def translation_task(self) -> Task:
        """Create task for translating podcast script to French"""
        return Task(
            config=self.tasks_config["translation_task"],  # type: ignore[index]
        )

    @task
    @log_function_call(logger)
    def french_podcast_task(self) -> Task:
        """Create task for French podcast delivery"""
        return Task(
            config=self.tasks_config["french_podcast_task"],
        )

    @crew
    @log_function_call(logger)
    def crew(self) -> Crew:
        """Creates the PodcastCrew for multilingual podcast delivery"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
