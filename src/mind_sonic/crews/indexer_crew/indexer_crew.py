from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import RagTool
from typing import List
from mind_sonic.rag_config import DEFAULT_RAG_CONFIG

from mind_sonic.utils.file_type_utils import get_embedchain_data_type
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class IndexerCrew():
    """IndexerCrew for processing and indexing files into a vector database.
    
    This crew is responsible for processing various file types, determining their
    appropriate data type for embedchain, and adding them to the RAG tool's vector database.
    It uses OpenAI models for embeddings and language processing.
    """

    agents: List[BaseAgent]
    tasks: List[Task]

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
            self.rag_tool.add(source=file, data_type=datatype, loader=loader, chunker=chunker)
        else:
            # Standard processing for other file types
            self.rag_tool.add(source=file, data_type=datatype)
            
        return f"Processed {file} of type {datatype}"



    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            verbose=True,
            tools=[self.rag_tool],
            allow_delegation=False,
        )



    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the IndexerCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
