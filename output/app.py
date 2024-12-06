#Prefix:
"""LangGraph State Management Example: Demonstrating how to create and update state in a workflow using LangGraph. This example shows different ways of modifying the graph state across multiple nodes."""

import operator
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

# Define a custom state type with different update behaviors
class WorkflowState(TypedDict):
    # Messages will be accumulated (appended)
    messages: Annotated[list, operator.add]
    
    # User information can be completely replaced
    user_info: dict
    
    # Numeric state can be updated incrementally
    task_count: int

# Initialize the language model
model = ChatOpenAI(model="gpt-4o")

# Node function for initializing the workflow
def initial_node(state: WorkflowState):
    """Initialize the workflow and set initial state"""
    return {
        "messages": [HumanMessage(content="Welcome to the state update demonstration!")],
        "user_info": {},
        "task_count": 0
    }

# Node function to collect and update user information
def collect_user_info(state: WorkflowState):
    """Collect and update user information in the state"""
    current_messages = state["messages"]
    
    # Simulate collecting user details
    response = model.invoke([
        *current_messages, 
        HumanMessage(content="Please provide your name and age.")
    ])
    
    # Update state with new user information
    return {
        "messages": [response],
        "user_info": {
            "name": "Alice Smith",  # In a real scenario, this would be extracted from the response
            "age": 35,
            "email": "alice@example.com"
        },
        "task_count": state["task_count"] + 1
    }

# Node function to process a task based on user information
def process_task(state: WorkflowState):
    """Process a task and update the state accordingly"""
    current_messages = state["messages"]
    user_info = state["user_info"]
    
    # Generate a personalized task response
    response = model.invoke([
        *current_messages,
        HumanMessage(content=f"Create a personalized task plan for {user_info['name']} aged {user_info['age']}")
    ])
    
    # Update state with new task and increment task count
    return {
        "messages": [response],
        "user_info": {
            **user_info,  # Preserve existing user info
            "task_status": "in_progress"
        },
        "task_count": state["task_count"] + 1
    }

# Create the workflow graph
workflow = StateGraph(WorkflowState)

# Add nodes to the workflow
workflow.add_node("start", initial_node)
workflow.add_node("collect_info", collect_user_info)
workflow.add_node("process_task", process_task)

# Define the workflow edges
workflow.add_edge(START, "start")
workflow.add_edge("start", "collect_info")
workflow.add_edge("collect_info", "process_task")
workflow.add_edge("process_task", END)

# Compile the workflow
app = workflow.compile()

# Run the workflow and print the final state
result = app.invoke({})
print("Final Workflow State:")
print(result)