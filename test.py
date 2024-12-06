from agent import CodeSolutionAgent
from state import State, ResearchState, DocumentationState, Validation, Module, CodeSolution
from langchain_anthropic import ChatAnthropic
from pprint import pprint
import logging
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import HumanMessage
from utils import URLRetrievalTool
from dotenv import load_dotenv
from typing import cast
import pickle

load_dotenv()

HAIKU_MODEL = "claude-3-5-haiku-latest"
SONNET_MODEL = "claude-3-5-sonnet-latest"

# Define a function that will merge the agent output with the current state.  Output and state are dictionaries.
# Output may not contain all of the keys that are in state.
# Messages from output should be appended to messages in state.
# Only update the keys that are in output.
def merge_state(state, output):
    for key, value in output.items():
        if key in ["messages", "llmCosts"]:
            state[key] += value
        else:
            state[key] = value
    return state



planner_llm = ChatAnthropic(model=HAIKU_MODEL)
researcher_llm = ChatAnthropic(model=HAIKU_MODEL).bind_tools([URLRetrievalTool()])
#reviewer_llm = ChatAnthropic(model=HAIKU_MODEL, max_tokens=4096).with_structured_output(CodeReview, include_raw=True)
tester_llm = ChatAnthropic(model=HAIKU_MODEL, max_tokens=4096).with_structured_output(CodeSolution, include_raw=True)
search = TavilySearchResults(max_results=2)
agent = CodeSolutionAgent(planner_llm=planner_llm, researcher_llm=researcher_llm, summarizer_llm=None, coder_llm=tester_llm, documenter_llm=None, reviewer_llm=None, searchTool=search, logger=logging.getLogger())


# research = ResearchState(problem_statement="", research_plan=[], current_step=0, research_results=[], final_research="", is_complete=False)
# code = Module(prefix="", imports="", code="")
# tests = Module(prefix="", imports="", code="")
# documentation = DocumentationState(prefix="", markdown="")
# validation = Validation()
# agentStatus = {}

# state = State(messages=[HumanMessage("Create a langgraph agent to generate unit tests")], research=research, generated_code={}, generated_tests=tests, documentation=documentation, validation=validation, agentStatus=agentStatus)

#load the output from the file
with open("output/state/code_planner.pkl", "rb") as f:
    state = pickle.load(f)

output = agent.coder(state)

pprint(output)

merged_state = merge_state(state, output)

with open("output/state/coder_1.pkl", "wb") as f:
    pickle.dump(merged_state, f)