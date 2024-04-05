import logging
from openagi.agent import Agent
from openagi.init_agent import kickOffAgents
from openagi.llms.azure import AzureChatOpenAIModel
from openagi.llms.openai import OpenAIModel
from openagi.tools.integrations import DuckDuckGoSearchTool

# human tool integration
def onResultHGI(agentName, result, consumerAgent):
    feedback = "Pass"
    action = "None"
    logging.debug(f"{agentName}:TO:{consumerAgent}-> {result}")
    return result, feedback, action

# control for the user to perform aggregation
def onAggregationAction(agentName, consumerAgent, aggrSourceAgentList, aggrResultsList):
    result = ""
    for string in aggrResultsList:
        result += string.body + " "
    logging.debug(f"aggregation of messages::of {agentName} to {consumerAgent} {result}")
    return result

if __name__ == "__main__":
    agent_name = ["RESEARCHER1", "RESEARCHER2", "WRITER", "EMAILER"]
    config_azure = AzureChatOpenAIModel.load_from_yml_config()
    llm_azure = AzureChatOpenAIModel(config=config_azure)
    config_openai = OpenAIModel.load_from_yml_config()
    llm_openai = OpenAIModel(config=config_openai)
    agent_list = [
        Agent(
            agentName=agent_name[0],
            aggregator=0,
            onAggregationAction=None,
            creator=None,
            role="RESEARCHER",
            feedback=False,
            goal="search for latest trends in Carona treatment that includes medicines, physical exercises, overall management and prevention aspects",
            backstory="backstory",
            capability="search_executor",
            agent_type="STATIC",
            multiplicity=0,
            task="search internet for the goal for the trends in 2H 2023 onwards",
            output_consumer_agent=[agent_name[2]],
            HGI_Intf=onResultHGI,
            llm=llm_azure,
            llm_resp_timer_value=20,
            tools_list=[DuckDuckGoSearchTool],
        ),
        Agent(
            agentName=agent_name[1],
            aggregator=0,
            onAggregationAction=None,
            creator=None,
            role="RESEARCHER",
            feedback=False,
            goal="search for latest trends in Cancer treatment that includes medicines, physical exercises, overall management and prevention aspects",
            backstory="backstory",
            capability="search_executor",
            agent_type="STATIC",
            multiplicity=0,
            task="search internet for the goal for the trends in 2H 2023 onwards",
            output_consumer_agent=[agent_name[2]],
            HGI_Intf=onResultHGI,
            llm=llm_openai,
            llm_resp_timer_value=20,
            tools_list=[DuckDuckGoSearchTool],
        ),
        Agent(
            agentName=agent_name[2],
            aggregator=2,
            onAggregationAction=onAggregationAction,
            creator=None,
            role="SUMMARISER",
            feedback=False,
            goal="summarize input into presentable points",
            backstory="backstory",
            capability="llm_task_executor",
            agent_type="STATIC",
            multiplicity=0,
            task="summarize points to present to health care professionals and general public separately",
            output_consumer_agent=[agent_name[3]],
            HGI_Intf=onResultHGI,
            llm=llm_openai,
            llm_resp_timer_value=130,
            tools_list=[],
        ),
        Agent(
            agentName=agent_name[3],
            aggregator=0,
            onAggregationAction=None,
            creator=None,
            role="EMAILER",
            feedback=False,
            goal="composes the email based on the contenct",
            backstory="backstory",
            capability="llm_task_executor",
            agent_type="STATIC",
            multiplicity=0,
            task="composes email based on summary to doctors and general public separately into a file with subject-summary and details",
            output_consumer_agent=["HGI"],
            HGI_Intf=onResultHGI,
            llm=llm_azure,
            llm_resp_timer_value=130,
            tools_list=[],
        ),
    ]
    kickOffAgents(agent_list, [agent_list[0], agent_list[1]], llm=llm_azure)
