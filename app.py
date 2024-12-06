from dotenv import load_dotenv
import time, pickle, logging, argparse, os, pprint

import langchain
from langgraph.graph import StateGraph, START, END
from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from state import State, CodeSolution, Documentation, CodeReview, StateWrapper
from utils import URLRetrievalTool, set_env, configure_logging
from agent import CodeSolutionAgent

# Define model constants for easy configuration and reuse
HAIKU_MODEL = "claude-3-5-haiku-latest"
SONNET_MODEL = "claude-3-5-sonnet-latest"

def configure_environment():
    """Load environment variables from a .env file and set necessary API keys."""
    load_dotenv()
    set_env("ANTHROPIC_API_KEY")
    set_env("TAVILY_API_KEY")
    #langchain.debug = True

def create_llms(search_tool, url_tool):
    """Create and configure the language models with necessary tools and structured outputs."""
    base_llm = ChatAnthropic(model=HAIKU_MODEL)
    planner_llm = base_llm
    researcher_llm = base_llm.bind_tools([url_tool])
    summary_llm = ChatAnthropic(model=HAIKU_MODEL, max_tokens=4096)
    documenter_llm = base_llm.with_structured_output(Documentation, include_raw=True)
    coder_llm = ChatAnthropic(model=HAIKU_MODEL, max_tokens=4096).with_structured_output(CodeSolution, include_raw=True)
    reviewer_llm = ChatAnthropic(model=SONNET_MODEL, max_tokens=4096).with_structured_output(CodeReview, include_raw=True)
    return planner_llm, researcher_llm, summary_llm, coder_llm, documenter_llm, reviewer_llm

def build_graph(graph_builder, agent, tools, checkpointer=None):
    """Construct the state graph with nodes and edges for the code solution process."""
    graph_builder.add_node("research_planner", agent.research_planner)    
    graph_builder.add_node("researcher", agent.researcher)
    tool_node = ToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_node("research_summarizer", agent.research_summarizer)
    graph_builder.add_node("code_planner", agent.code_planner)
    graph_builder.add_node("coder", agent.coder)
    #graph_builder.add_node("documenter", agent.documenter)
    graph_builder.add_node("tester", agent.tester)
    #graph_builder.add_node("validator", agent.validator)

    def research_condition(state):
        if tools_condition(state) == END:
            if state["research"]["is_complete"]:
                return END
            return "loop"
        return "tools"
    
    # Define conditional and direct edges between nodes
    graph_builder.add_conditional_edges(
        "researcher",
        research_condition,
        {"tools": "tools", "loop":"researcher", END: "research_summarizer"},
    )

    graph_builder.add_conditional_edges("coder", 
                                        (lambda state: END if state["generated_code"]["is_complete"] else "loop"), 
                                        {"loop": "coder", END: "tester"})

    graph_builder.add_edge(START, "research_planner")
    graph_builder.add_edge("research_planner", "researcher")
    graph_builder.add_edge("tools", "researcher")
    graph_builder.add_edge("research_summarizer", "code_planner")
    #graph_builder.add_edge("tester", "documenter")
    #graph_builder.add_edge("tester", "validator")
    #graph_builder.add_edge("documenter", END)
    #graph_builder.add_edge("validator", END)

    return graph_builder.compile(checkpointer=checkpointer)

def output_results(graph, config, output_dir="output"):
    """Write the results of the graph execution to output files."""
    graph_state = graph.get_state(config=config).values
    state_wrapper = StateWrapper(graph_state)  # Wrap the state for easier access

    os.makedirs(output_dir, exist_ok=True)

    def write_to_file(filename, content):
        """Helper function to write content to a specified file."""
        with open(os.path.join(output_dir, filename), "w") as file:
            file.write(content)

    # Use the state wrapper to access properties and write to files
    write_to_file("app.py", f'#Prefix:\n"""{state_wrapper.generated_code.prefix}"""\n\n' +
                  f'{state_wrapper.generated_code.imports}\n\n' +
                  f'{state_wrapper.generated_code.code}')
    write_to_file("tests.py", f'#Prefix:\n"""{state_wrapper.generated_tests.prefix}"""\n\n' +
                  f'{state_wrapper.generated_tests.imports}\n\n' +
                  f'{state_wrapper.generated_tests.code}')
    write_to_file("documentation.md", state_wrapper.documentation.markdown)
    write_to_file("research.md", state_wrapper.research)
    write_to_file("review.md", "# Code Review Notes and Suggestions\n\n" +
                  "## Compile Errors:\n\n" +
                  "\n".join(state_wrapper.validation.compile_errors) or "No compile errors found." +
                  (f"\n\n## Feedback:\n\n{state_wrapper.validation.code_review.feedback}" +
                   f"\n\n```python\n\n{state_wrapper.validation.code_review.reviewed_code}\n```"
                   if state_wrapper.validation.code_review else ""))

# Function to output the graph state to a pickle file at each step of execution
# Use a timestamp to ensure unique filenames
def output_state(eventName, graph, config, output_dir="output/state"):
    """Write the state of the graph execution to a pickle file."""

    graph_state = graph.get_state(config=config).values

    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, f"{eventName}_{time.time()}.pkl"), "wb") as file:
        pickle.dump(graph_state, file)


def stream_graph_updates(graph, user_input: str, config, log_file="logs/llm.log"):
    """Stream updates from the graph execution and log the LLM interactions."""
    for event in graph.stream({"messages": [("user", user_input)]}, config=config):
        eventName = list(event.keys())[0]
        print(f"Saving post event state file from {eventName}")
        #pprint.pprint(event)
        output_state(eventName, graph, config)

def parse_args():
    """Parse command-line arguments for configuring the assistant run."""
    parser = argparse.ArgumentParser(description="Run the code solution assistant")
    parser.add_argument("--user-input", type=str, help="The user input to provide to the assistant", dest="input")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--show-graph", action="store_true", help="Show the graph instead of running the assistant")
    return parser.parse_args()

def main():
    """Main function to run the code solution assistant."""
    args = parse_args()
    configure_environment()

    # Set up the graph and agents
    logger = configure_logging()
    memory_checkpointer = MemorySaver()
    search_tool = TavilySearchResults(max_results=2)
    url_tool = URLRetrievalTool()
    tools = [search_tool, url_tool]
    graph_builder = StateGraph(State)
    planner_llm, researcher_llm, summarizer_llm, coder_llm, documenter_llm, reviewer_llm = create_llms(search_tool, url_tool)
    agent = CodeSolutionAgent(planner_llm, researcher_llm, summarizer_llm, coder_llm, documenter_llm, reviewer_llm, search_tool, logger)
    graph = build_graph(graph_builder, agent, tools , memory_checkpointer)
    config = {"configurable": {"thread_id": "1"}}

    # Display the graph if requested, otherwise run the assistant
    if args.show_graph:
        display_graph(graph)
        return

    # Execute the graph with user input
    user_input = args.input or input("User: ")
    stream_graph_updates(graph, user_input, config)
    #output_results(graph, config)

def display_graph(graph):
    """Display the graph as an image."""
    image_path = 'graph.png'
    with open(image_path, 'wb') as f:
        f.write(graph.get_graph().draw_mermaid_png())

if __name__ == "__main__":
    main()