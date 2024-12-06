from typing import Dict, Any, cast
from state import State, ResearchState, Validation, CodeSolution, CodingState, Module, CodeReview, Documentation, DocumentationState, ResearchStateManager, CodingStateManager, LLMCost
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
import json 

class CodeSolutionAgent:
    """Agent responsible for generating and validating code solutions using LLMs."""

    def __init__(self, planner_llm, researcher_llm, summarizer_llm, coder_llm, documenter_llm, reviewer_llm, searchTool, logger):
        """
        Initialize the CodeSolutionAgent with the necessary language models.
        
        Args:
            researcher_llm: LLM for conducting research.
            coder_llm: LLM for generating code solutions.
            documenter_llm: LLM for generating documentation.
            reviewer_llm: LLM for reviewing and validating code.
        """
        self.planner_llm = planner_llm
        self.researcher_llm = researcher_llm
        self.summarizer_llm = summarizer_llm
        self.coder_llm = coder_llm
        self.documenter_llm = documenter_llm
        self.reviewer_llm = reviewer_llm
        self.searchTool = searchTool
        self.logger = logger

    def merge_llm_cost(response: AIMessage, costs: list[LLMCost] = []) -> list[LLMCost]:
        costs.append({"model": response.response_metadata["model"], "input_tokens": response.response_metadata["usage"]["input_tokens"], "output_tokens": response.response_metadata["usage"]["output_tokens"]})
        return costs

    def research_planner(self, state: State) -> Dict[str, Any]:
        self.logger.info("Planning research")
        system_message = """
            You are part of a team of researchers tasked with gathering information that will be used to generate a code solution.

            The problem will be solved in multiple steps.  Your job is to create the comprehensive research plan to gather the
            information necessary to solve the problem.
            
            Think of different search queries that would identify up-to-date resources that can help solve 
            the problem, but are outside of your existing knowledgebase.

            Your output will be a list of the 3-5 most relevant search queries in JSON format.  Each item in the list will contain
            an integer ID, the search query as a string, and a status of pending.

            Include only the JSON.  Do not include any text before or after the JSON.

            Example: [{{"id": 1, "query": "Python best practices", "status":"pending"}}, {{"id": 2, "query": "Python performance optimization","status":"pending"}}]
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("placeholder", "{messages}"),
        ])

        researcher_chain = prompt | self.planner_llm
        response = researcher_chain.invoke({"messages": state["messages"]})
        cost = CodeSolutionAgent.merge_llm_cost(response)
        

        #print(f"Research Planner Response: {response}")

        researchPlan = json.loads(response.content)
        researchPlan[0]["status"] = "inProgress"
        researchState = ResearchState()
        researchState["problem_statement"] = state["messages"][0].content
        researchState["research_plan"] = researchPlan
        researchState["current_step"] = 0
        researchState["research_results"] = []
        researchState["final_research"] = ""
        researchState["is_complete"] = False
        return {"messages": [response], "agentStatus": {"research": "inProgress"}, "research": researchState, "llmCosts": cost}

    def researcher(self, state: State) -> Dict[str, Any]:
        """Conduct research to gather information for generating a code solution."""
        self.logger.info("Running researcher")

        researchState: ResearchState = state["research"]
        researchStateManager = ResearchStateManager(researchState)

        currentStep = researchStateManager.getCurrentStep()
        query = currentStep["query"]

        search_results = self.searchTool.invoke(query)

        system_message = """
            You are part of a team of researchers tasked with gathering information that will be used to generate a code solution.

            Your teammate has created a comprehensive research plan to gather the information necessary to solve the problem.
            
            Your job is to help execute the research plan by reviewing the search results provided and determining if
            more details should be gathered from the source url.
            
            1) First, review the search results to determine how relevant they are to the research problem. 
            
            2) Next, if a result seems relevant, use the URL retriever tool to get the content of the URL.

            3) Finally, when you have gathered enough information to recommend a solution, you will 
            summarize your research in the form of a Markdown document. The summary should include your key findings,
            recommendations for how to solve the problem, code examples that may be relevant to the solution, and any 
            other relevant information.

            In your summary, be sure to cite the sources of your information including footnotes or references at the end.

            Your final output must be detailed, well-structured Markdown only.  Do not include any prefix or suffix text.
        """

        prompt_message = """
            The research problem statement is: {problem}
            Review the search results for the query: {query}
            {search_results}
        """

        prompt = ChatPromptTemplate.from_messages([
            ("placeholder", "{messages}"),
            ("system", system_message),
            ("human", prompt_message),
        ])

        #self.logger.debug(f"Research State: {state}")
        researcher_chain = prompt | self.researcher_llm
        response: AIMessage = researcher_chain.invoke({"messages": state["messages"], "problem": researchState["problem_statement"], 
                                            "query": query, "search_results": search_results})
        cost = CodeSolutionAgent.merge_llm_cost(response)

        if response.response_metadata["stop_reason"] == "tool_use":
            # LLM decided to use a tool, so we are not ready to save the summarized research
            return {"messages": [response], "llmCosts": cost}
        else:
            content = response.content
            content = content if isinstance(content, str) else content[0]
            researchState["research_results"].append(content)

            researchPlan = researchState["research_plan"]
            currentStep = researchState["current_step"]
            nextStep = currentStep + 1
            isComplete = nextStep >= len(researchPlan)
            researchPlan[currentStep]["status"] = "done"
            if not isComplete:
                researchPlan[nextStep]["status"] = "inProgress"
            researchState["current_step"] = nextStep
            researchState["is_complete"] = isComplete
            return {"messages": [response], "research": researchState, "llmCosts": cost}
        
    def research_summarizer(self, state: State) -> Dict[str, Any]:
        """Summarize the research results into a Markdown document."""
        self.logger.info("Running research_summarizer")

        prompt_message = """
            You are part of a team of researchers tasked with gathering information that will be used to generate a code solution.

            Your teammates have gathered the research results and now it is your turn to summarize the information into a
            well-structured, detailed Markdown document.  The document should include your key findings, recommendations for how to solve the problem,
            code examples that may be relevant to the solution, and any other relevant information.

            In your summary, be sure to cite the sources of your information including footnotes or references at the end.

            Your final output must be detailed, well-structured Markdown only.  Do not include any prefix or suffix text.

            The research results are:

            {research_output}
        """

        researchState: ResearchState = state["research"]
        prompt = ChatPromptTemplate.from_messages([
            ("human", prompt_message),
        ])

        summary_chain = prompt | self.summarizer_llm
        response: AIMessage = summary_chain.invoke({"research_output", "\n".join(researchState["research_results"])})
        researchState["final_research"] = response.content
        return {"messages": [], "agentStatus": {"research": "done", "code":"inProgress"}, "researchState": researchState}
    
    def code_planner(self, state: State) -> Dict[str, Any]:
        self.logger.info("Planning code solution")
        system_message = """
            You are part of a team of researchers tasked with gathering information that will be used to generate a code solution.

            The problem will be solved in multiple steps.  Your job is to plan the code modules that will be needed to solve the problem.
            
            Your teammates have gathered the research results and now it is your turn to plan the code solution.  
            
            You should

            1) Review the research results to understand the problem and the proposed solution.

            2) Identify the key components of the code solution that will be needed to solve the problem.

            3) Plan the code modules that will be needed to implement the solution.  Each module should have a clear purpose.

            4) Output a list of the code modules that will be needed to implement the solution in JSON format.  
            Each item in the list should contain
                - an integer ID
                - the name of the module
                - a brief description of the module including its purpose and what capabilities it will provide to other modules
                - a file name for the module
                - a status of pending

            Be sure to organize the modules in a logical order that will allow your teammates to implement the solution efficiently.

            Include only the JSON.  Do not include any text before or after the JSON.

            Example: [{{"id": 1, "name": "Some module", "description":"A module that does something important", "file_name":"some_module.py", "status":"pending"}}, 
                        {{"id": 2, "name": "another module", "description": "This module does something else", "file_name":"another_module.py", "status":"pending"}}]
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("placeholder", "{messages}"),
        ])

        code_planner_chain = prompt | self.planner_llm
        response = code_planner_chain.invoke({"messages": [HumanMessage(
            f"""
            Plan the code modules that will be needed to implement the solution based on the research.

            Problem Statement: {state["research"]["problem_statement"]} 

            Research Results: {state["research"]["final_research"]}
            """
            )]})
        cost = CodeSolutionAgent.merge_llm_cost(response)
        
        print(f"Code Planner Response: {response}")

        codePlan = json.loads(response.content)
        codePlan[0]["status"] = "inProgress"
        codeState = CodingState()
        codeState["code_plan"] = codePlan
        codeState["current_step"] = 0
        codeState["modules"] = []
        codeState["is_complete"] = False
        return {"messages": [response], "agentStatus": {"code": "inProgress"}, "generated_code": codeState, "llmCosts": cost}

    def coder(self, state: State) -> Dict[str, Any]:
        """Generate a code solution based on the research output."""
        self.logger.info("Running coder")
        #self.logger.debug(f"Research State: {state['research']}")
        system_message = """
            Generate a detailed, well-structured, and well documented module as part of a larger code solution to address the user's input. 
            
            Your teammate has planned the code modules that will be needed to implement the solution.  Your job is to implement the following module.
            {code_step}

            To achieve this task, you should use your knowledge of the topic and the additional information provided in the
            research output:
            {research_output}

            The following modules have already been implemented. You should ensure that your module is compatible with the existing code.
            {implemented_modules}

            Your response should include:
            - Prefix: A brief description of the problem and approach.
            - Imports: Necessary import statements.
            - Code: The main code block.

            Example:
            Prefix: This function calculates the factorial of a number.
            Imports: import math
            Code: def factorial(n): return math.factorial(n)
        """

        code_gen_prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("placeholder", "{messages}"),
        ])

        research_output = state["research"]["final_research"]
        codePlan: CodingState = state["generated_code"]
        currentStep = CodingStateManager(codePlan).getCurrentStep()
        implemented_modules = codePlan["modules"]

        code_gen_chain = code_gen_prompt | self.coder_llm
        response = code_gen_chain.invoke({"research_output": research_output, "messages": [state["messages"][0]],
                                          "code_step": currentStep, "implemented_modules": implemented_modules})
        parsed = cast(CodeSolution, response["parsed"])
        module = Module(prefix=parsed.prefix, imports=parsed.imports, code=parsed.code)

        codePlan["modules"].append(module)
        codePlan["current_step"] += 1
        codePlan["is_complete"] = codePlan["current_step"] >= len(codePlan["code_plan"])
        currentStep["status"] = "done"

        return {"messages": [response["raw"]], "generated_code": codePlan, "agentStatus": {"code": "done", "tests": "inProgress", "documentation": "inProgress"}}
    
    def tester(self, state: State) -> Dict[str, Any]:
        """Generate tests to validate the code solution."""
        self.logger.info("Running tester")
        system_message = """
            Generate a detailed, well-structured, and well documented set of tests to validate the behavior of the code solution provided. 
            
            You can assume that the application code will be in a file called app.py and the test code will be in a file called tests.py.
            
            {code_solution}

            Your response should include:
            - Prefix: A brief description of the problem and approach.
            - Imports: Necessary import statements.
            - Code: The main code block to execute the tests.
        """
        code_gen_prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("placeholder", "{messages}"),
        ])

        code_gen_chain = code_gen_prompt | self.coder_llm
        response = code_gen_chain.invoke({"code_solution": state["generated_code"], "messages": [HumanMessage("Generate a comprehensive suite of tests for the code solution.")]})
        parsed = cast(CodeSolution, response["parsed"])
        module = Module(prefix=parsed.prefix, imports=parsed.imports, code=parsed.code)

        return {"messages": [response["raw"]], "generated_tests": module, "agentStatus": {"tests": "done", "validation": "inProgress"}}

    def documenter(self, state: State) -> Dict[str, Any]:
        """Generate documentation for the code solution."""
        self.logger.info("Running documenter")
        response = self.documenter_llm.invoke(f"Generate markdown documentation for the code solution: {state['generated_code']}")

        parsed = cast(Documentation, response["parsed"])
        documentationState = DocumentationState(prefix=parsed.prefix, markdown=parsed.markdown)
        agentStatus = state.get("agentStatus", {})
        agentStatus["documentation"] = "done"
        return {"messages": [response["raw"]], "documentation": documentationState, "agentStatus": {"documentation": "done"}}

    def validator(self, state: State) -> Dict[str, Any]:
        """Validate the generated code and tests, and provide a code review."""
        self.logger.info("Running validator")
        generated_code = state["generated_code"]
        generated_tests = state["generated_tests"]
        code_to_validate = f"Application Code: {generated_code["imports"]}\n\n{generated_code["code"]} \n\nTest Code: {generated_tests["imports"]}\n\n{generated_tests["code"]}"
        validation = Validation()
        validation["compile_errors"] = []

        try:
            compile(code_to_validate, "<string>", "exec")
        except Exception as e:
            validation["compile_errors"].append(e)

        code_review_prompt = f"""
            You are an expert coder who is adept at finding errors, performance issues, testability issues, and security flaws in code.
            Your task is the review the generated code and provide feedback on its quality and correctness.
            
            Your review will include two parts:
            1) feedback: A brief summary of the code quality and correctness.
            2) reviewed_code: The original code annotated with your comments and suggestions.

            Review the following code:
            {code_to_validate}
        """

        response = self.reviewer_llm.invoke(code_review_prompt)
        code_review = cast(CodeReview, response["parsed"])
        validation["feedback"] =  code_review.feedback
        validation["reviewed_code"] = code_review.reviewed_code

        return {"validation": validation, "messages": [response["raw"]], "agentStatus": {"validation": "done"}}