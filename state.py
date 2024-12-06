from typing import Any, Dict, TypedDict, Annotated
from langgraph.graph.message import MessagesState
from pydantic import BaseModel, Field

# Data model
class CodeSolution(BaseModel):
    """Schema for code solutions"""

    prefix: str = Field(description="Description of the problem and approach")
    language: str = Field(description="Programming language of the code solution")
    imports: str = Field(description="Code block import statements")
    code: str = Field(description="Code block not including import statements")

class Documentation(BaseModel):
    """Schema for documentation"""

    prefix: str = Field(description="Description of the problem and approach")
    markdown: str = Field(description="Markdown documentation for the code solution")

class CodeReview(BaseModel):
    """Schema for code review"""

    feedback: str = Field(description="Feedback on the code solution")
    reviewed_code: str = Field(description="Reviewed code annotated with reviewer comments")

# TypedDict classes are used to track state because CoAgent does not support Pydantic models
class Validation(TypedDict):
    compile_errors: list[str] = []
    feedback: str
    reviewed_code: str

class ResearchStep(TypedDict):
    """Define a step in the research process."""
    id: int
    query: str
    status: str

class ResearchState(TypedDict):
    """Define the state for the research agent."""
    problem_statement: str
    research_plan: list[ResearchStep]
    current_step: int
    research_results: list[str]
    final_research: str
    is_complete: bool

class ResearchStateManager():
    def __init__(self, state: ResearchState):
        self._state = state

    def getStep(self, step_id: int) -> ResearchStep:
        return self._state["research_plan"][step_id]

    def getCurrentStep(self) -> ResearchStep:
        return self.getStep(self._state["current_step"])


class CodingStep(TypedDict):
    """Define a step in the coding process."""
    id: int
    name: str
    description: str
    file_name: str
    status: str

class Module(TypedDict):
    prefix: str
    language: str
    imports: str
    code: str
    file_name: str

class CodingState(TypedDict):
    """Define the state for the coding agent."""
    code_plan: list[CodingStep]
    current_step: int
    modules: list[Module]
    is_complete: bool

class CodingStateManager():
    def __init__(self, state: CodingState):
        self._state = state

    def getStep(self, step_id: int) -> CodingStep:
        return self._state["code_plan"][step_id]

    def getCurrentStep(self) -> CodingStep:
        return self.getStep(self._state["current_step"])

class DocumentationState(TypedDict):
    prefix: str
    markdown: str

def merge_agent_status(left: Dict[str, str], right: Dict[str,str]) -> Dict[str, str]:
    for key, value in right.items():
        left[key] = value
    return left

class LLMCost(TypedDict):
    model: str
    input_tokens: int
    output_tokens: int

def merge_llm_costs(left: list[LLMCost], right: list[LLMCost]) -> list[LLMCost]:
    return left + right
    
class State(MessagesState):
    research: ResearchState
    generated_code: CodingState
    generated_tests: Module
    documentation: DocumentationState
    validation: Validation
    agentStatus: Annotated[Dict[str, str], merge_agent_status]
    llmCosts: Annotated[list[LLMCost], merge_llm_costs]

class StateWrapper:
    def __init__(self, state: MessagesState):
        self._state = state

    @property
    def research(self) -> str:
        return self._state.research

    @research.setter
    def research(self, value: str):
        self._state.research = value

    @property
    def generated_code(self) -> Dict[str, Any]:
        return self._state.generated_code

    @generated_code.setter
    def generated_code(self, value: Dict[str, Any]):
        self._state.generated_code = value

    @property
    def generated_tests(self) -> Dict[str, Any]:
        return self._state.generated_tests

    @generated_tests.setter
    def generated_tests(self, value: Dict[str, Any]):
        self._state.generated_tests = value

    @property
    def documentation(self) -> Dict[str, Any]:
        return self._state.documentation

    @documentation.setter
    def documentation(self, value: Dict[str, Any]):
        self._state.documentation = value

    @property
    def validation(self) -> Dict[str, Any]:
        return self._state.validation

    @validation.setter
    def validation(self, value: Dict[str, Any]):
        self._state.validation = value