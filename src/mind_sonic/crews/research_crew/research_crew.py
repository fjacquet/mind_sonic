from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import RagTool
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class ResearchCrew():
    """ResearchCrew crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
 # Create a RAG tool with custom configuration
    config = {
        "llm": {
            "provider": "openai",
            "config": {
                "model": "gpt-4.1-mini",
                "temperature": 0.7,
                "max_tokens": 1000
            }
        },
        "embedder": {
            "provider": "openai",
            "config": {
                "model": "text-embedding-3-large"
            }
        },
        "vectordb": {
            "provider": "chroma",
            "config": {
                "collection_name": "mind_sonic",
                "dir": "./storage/chroma",
                "allow_reset": True
            }
        },
        "chunker": {
            "chunk_size": 400,
            "chunk_overlap": 100,
            "length_function": "len",
            "min_chunk_size": 0
        }
    }
    rag_tool = RagTool(config=config, summarize=True)
    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            tools=[self.rag_tool],
            allow_delegation=False,
            verbose=True,
            reasoning=True,
            max_reasoning_attempts=5,
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'], # type: ignore[index]
            tools=[self.rag_tool],
            allow_delegation=False,
            verbose=True,
            reasoning=True,
            max_reasoning_attempts=5,
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'], # type: ignore[index]
        )

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['reporting_task'], # type: ignore[index]
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ResearchCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            memory=True,
            cache=True,
            respect_context_limit=True,
            
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
