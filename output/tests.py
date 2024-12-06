#Prefix:
"""Unit and Integration Tests for Multi-Agent Research Assistant

This test suite aims to comprehensively validate the functionality of the LangGraph multi-agent research assistant, covering:
1. Individual node functionality
2. Workflow state management
3. Error handling
4. End-to-end workflow execution"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Import the main application code
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app

# Additional imports for testing
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

class TestResearchAgent(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test method."""
        # Ensure consistent model configuration for testing
        self.test_model = ChatOpenAI(model="gpt-4o", temperature=0)
    
    def test_research_agent_state_initialization(self):
        """Test the initial state of the ResearchAgentState."""
        state = app.ResearchAgentState()
        self.assertEqual(state.messages, [])
        self.assertEqual(state.research_results, [])
        self.assertEqual(state.final_output, "")
    
    def test_researcher_node_creation(self):
        """Test the creation of the researcher node."""
        researcher_node = app.create_researcher_node(self.test_model)
        
        # Simulate initial state
        initial_state = app.ResearchAgentState()
        initial_state.messages = [HumanMessage(content="Test research query")]
        
        # Invoke the researcher node
        result = researcher_node(initial_state)
        
        # Validate node output
        self.assertIn('messages', result)
        self.assertIn('research_results', result)
        self.assertTrue(len(result['messages']) > 0)
        self.assertTrue(len(result['research_results']) > 0)
    
    def test_analyzer_node_creation(self):
        """Test the creation of the analyzer node."""
        analyzer_node = app.create_analyzer_node(self.test_model)
        
        # Simulate state with research results
        initial_state = app.ResearchAgentState()
        initial_state.research_results = ["Initial research finding"]
        
        # Invoke the analyzer node
        result = analyzer_node(initial_state)
        
        # Validate node output
        self.assertIn('messages', result)
        self.assertIn('final_output', result)
        self.assertTrue(result['final_output'] != "")
    
    def test_build_research_agent_workflow(self):
        """Test the construction of the research agent workflow."""
        research_agent = app.build_research_agent()
        
        # Verify graph components
        self.assertIsNotNone(research_agent)
        self.assertTrue(hasattr(research_agent, 'invoke'))
    
    @patch('langchain_openai.ChatOpenAI')
    def test_run_research_agent_happy_path(self, mock_llm):
        """Test successful execution of the research agent."""
        # Mock the LLM to return predictable responses
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = MagicMock(content="Mocked research output")
        mock_llm.return_value = mock_instance
        
        # Run the research agent with a test query
        query = "Test research topic"
        result = app.run_research_agent(query)
        
        # Validate result
        self.assertIsNotNone(result)
        self.assertNotEqual(result, "")
    
    def test_run_research_agent_error_handling(self):
        """Test error handling in the research agent."""
        # Simulate an error condition
        with patch('app.build_research_agent', side_effect=Exception("Test error")):
            result = app.run_research_agent("Error test query")
            self.assertTrue("An error occurred" in result)
    
    def test_main_function_execution(self):
        """Verify that the main function can be called without errors."""
        try:
            app.main()
        except Exception as e:
            self.fail(f"main() raised {type(e).__name__} unexpectedly!")

def run_tests():
    """Execute the test suite."""
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestResearchAgent)
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    return result.wasSuccessful()

if __name__ == '__main__':
    run_tests()