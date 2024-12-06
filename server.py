import logging
from fastapi import FastAPI 
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from copilotkit import CopilotKitSDK, Action as CopilotAction, LangGraphAgent

from agent import CodeSolutionAgent
from state import State
from app import configure_environment, create_llms, build_graph, stream_graph_updates

from langgraph.graph import StateGraph
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.checkpoint.memory import MemorySaver
from utils import URLRetrievalTool, configure_logging
 
configure_environment()
logger = configure_logging()
memory_checkpointer = MemorySaver()
graph_builder = StateGraph(State)
url_tool = URLRetrievalTool()
search_tool = TavilySearchResults(max_results=2)
tools = [url_tool, search_tool]
planner_llm, researcher_llm, summarizer_llm, coder_llm, documenter_llm, reviewer_llm = create_llms(search_tool, url_tool)
agent = CodeSolutionAgent(planner_llm, researcher_llm, summarizer_llm, coder_llm, documenter_llm, reviewer_llm, search_tool, logger)
graph = build_graph(graph_builder, agent, tools , memory_checkpointer)

app = FastAPI()
 
# Define your backend action
async def fetch_name_for_user_id(userId: str):
    # Replace with your database logic
    return {"name": "User_" + userId}
 
# this is a dummy action for demonstration purposes
action = CopilotAction(
    name="fetchNameForUserId",
    description="Fetches user name from the database for a given ID.",
    parameters=[
        {
            "name": "userId",
            "type": "string",
            "description": "The ID of the user to fetch data for.",
            "required": True,
        }
    ],
    handler=fetch_name_for_user_id
)

agent = LangGraphAgent(
    name="code-solution-agent",
    description="Generate a code solution based on a prompt.",
    graph=graph,
)
 
# Initialize the CopilotKit SDK
sdk = CopilotKitSDK(actions=[action], agents=[agent])
 
# Add the CopilotKit endpoint to your FastAPI app
add_fastapi_endpoint(app, sdk, "/copilotkit_remote/")
 
def main():
    """Run the uvicorn server."""
    logger.debug("Starting server")
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8127, reload=True)
 
if __name__ == "__main__":
    main()
