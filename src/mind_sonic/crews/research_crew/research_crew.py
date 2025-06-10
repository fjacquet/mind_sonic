from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import RagTool, SerperDevTool, ScrapeWebsiteTool
from typing import List

from mind_sonic.rag_config import DEFAULT_RAG_CONFIG
from mind_sonic.tools.save_to_rag_tool import SaveToRagTool
from mind_sonic.tools.yahoo_ticker_info_tool import YahooFinanceTickerInfoTool
from mind_sonic.tools.yahoo_history_tool import YahooFinanceHistoryTool
from mind_sonic.tools.yahoo_company_info_tool import YahooFinanceCompanyInfoTool
from mind_sonic.tools.yahoo_etf_holdings_tool import YahooFinanceETFHoldingsTool
from mind_sonic.tools.yahoo_news_tool import YahooFinanceNewsTool
# from mind_sonic.tools.openai_tts_tool import OpenAITTSTool # Removed unused import
from mind_sonic.utils.logging_utils import get_logger, log_function_call
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators


@CrewBase
class ResearchCrew:
    """ResearchCrew for researching a topic and generating a report and podcast.

    This crew is responsible for researching a topic, generating a report,
    creating a podcast script, and delivering an audio podcast using AI agents.
    """

    # Initialize logger for this crew
    logger = get_logger(component="research_crew")
    agents: List[BaseAgent]
    tasks: List[Task]
    # Create a RAG tool with shared configuration
    config = DEFAULT_RAG_CONFIG
    rag_tool = RagTool(config=config, summarize=True)
    serper_tool = SerperDevTool()
    scrape_tool = ScrapeWebsiteTool()

    # Yahoo Finance tools
    ticker_info_tool = YahooFinanceTickerInfoTool()
    history_tool = YahooFinanceHistoryTool()
    company_info_tool = YahooFinanceCompanyInfoTool()
    etf_holdings_tool = YahooFinanceETFHoldingsTool()
    news_tool = YahooFinanceNewsTool()

    # Text-to-Speech tool (Removed unused tts_tool instance)
    # tts_tool = OpenAITTSTool()

    save_tool = SaveToRagTool(rag_tool)
    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    @log_function_call(logger)
    def researcher(self) -> Agent:
        self.logger.info("Creating researcher agent with tools")
        return Agent(
            config=self.agents_config["researcher"],  # type: ignore[index]
            tools=[
                self.rag_tool,
                self.serper_tool,
                self.scrape_tool,
                self.ticker_info_tool,
                self.history_tool,
                self.company_info_tool,
                self.etf_holdings_tool,
                self.news_tool,
                self.save_tool,
            ],
            allow_delegation=False,
            verbose=True,
            reasoning=True,
            max_reasoning_attempts=5,
        )

    @agent
    @log_function_call(logger)
    def reporting_analyst(self) -> Agent:
        self.logger.info("Creating reporting analyst agent")
        return Agent(
            config=self.agents_config["reporting_analyst"],  # type: ignore[index]
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
    def script_expert(self) -> Agent:
        self.logger.info("Creating podcast script expert agent")
        return Agent(
            config=self.agents_config["script_expert"],  # type: ignore[index]
            tools=[
                self.rag_tool,
                self.save_tool,
            ],
            allow_delegation=False,
            verbose=True,
            reasoning=True,
            max_reasoning_attempts=5,
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    @log_function_call(logger)
    def research_task(self) -> Task:
        self.logger.info("Creating research task")
        return Task(
            config=self.tasks_config["research_task"],  # type: ignore[index]
        )

    @task
    @log_function_call(logger)
    def reporting_task(self) -> Task:
        # Create the task with the config from YAML
        # We don't need to explicitly set context as the crew is configured with
        # process=Process.sequential and memory=True, which automatically passes
        # context between tasks in sequence
        self.logger.info("Creating reporting task")
        return Task(
            config=self.tasks_config["reporting_task"],  # type: ignore[index]
        )

    @task
    @log_function_call(logger)
    def script_task(self) -> Task:
        self.logger.info("Creating podcast script task")
        return Task(
            config=self.tasks_config["script_task"],  # type: ignore[index]
        )

    @crew
    @log_function_call(logger)
    def crew(self) -> Crew:
        """Creates the ResearchCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        self.logger.info(
            "Creating ResearchCrew with sequential process and memory enabled"
        )
        crew_instance = Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            memory=True,
            cache=True,
            respect_context_limit=True,
        )

        self.logger.info(
            f"ResearchCrew created with {len(self.agents)} agents and {len(self.tasks)} tasks"
        )
        return crew_instance

        # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
