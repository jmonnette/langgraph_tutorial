import streamlit as st
from agent import CodeSolutionAgent
from state import State, StateWrapper
from app import configure_environment, create_llms, build_graph, stream_graph_updates
import logging
import io

from langgraph.graph import StateGraph
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.checkpoint.memory import MemorySaver
from utils import URLRetrievalTool

configure_environment()

# Set up logging to capture logs in a string
log_stream = io.StringIO()
logging.basicConfig(stream=log_stream, level=logging.INFO)


memory_checkpointer = MemorySaver()
graph_builder = StateGraph(State)
researcher_llm, coder_llm, documenter_llm, reviewer_llm = create_llms()
agent = CodeSolutionAgent(researcher_llm, coder_llm, documenter_llm, reviewer_llm)
graph = build_graph(graph_builder, agent, [TavilySearchResults(max_results=2), URLRetrievalTool()], memory_checkpointer)
config = {"configurable": {"thread_id": "1"}}

# Streamlit UI
st.title("Code Solution Agent")

# User input for code solution prompt
prompt = st.text_area("Enter your prompt for the code solution:")

# Button to run the agent
if st.button("Generate Code Solution"):

    # Run the agent
    if prompt:
        stream_graph_updates(graph, prompt, config)

        graph_state = graph.get_state(config=config).values
        state = StateWrapper(graph_state)  # Wrap the state for easier access

        # Display outputs
        st.subheader("Generated Code")
        st.code(state.generated_code.code, language='python')

        st.subheader("Generated Tests")
        st.code(state.generated_tests.code, language='python')

        st.subheader("Documentation")
        st.markdown(state.documentation.markdown)

        st.subheader("Research")
        st.text(state.research)

        st.subheader("Validation")
        st.text("\n".join(state.validation.compile_errors) or "No compile errors found.")
        if state.validation.code_review:
            st.text(state.validation.code_review.feedback)
            st.code(state.validation.code_review.reviewed_code, language='python')

    else:
        st.error("Please enter a prompt to generate a code solution.")

# Display logs
st.subheader("Command Line Logs")
st.text(log_stream.getvalue())

# Assuming llm log is written to a file, read and display it
try:
    with open("logs/llm.log", "r") as llm_log_file:
        llm_logs = llm_log_file.read()
    st.subheader("LLM Logs")
    st.text(llm_logs)
except FileNotFoundError:
    st.error("LLM log file not found.")