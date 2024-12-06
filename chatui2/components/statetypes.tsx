import { useCoAgentStateRender } from "@copilotkit/react-core";

export type ResearchStep = {
    id: number;
    query: string;
    status: string;
};

export type ResearchState = {
    problem_statement: string;
    research_plan: ResearchStep[];
    current_step: number;
    research_results: string[];
    final_research: string;
    is_complete: boolean;
};

export type CodingStep = {
    id: number;
    name: string;
    description: string;
    file_name: string;
    status: string;
};

export type Module = {
    prefix: string;
    language: string;
    imports: string;
    code: string;
    file_name: string;
  };

export type CodingState = {
    code_plan: CodingStep[]
    current_step: number
    modules: Module[]
    is_complete: boolean
};

export type DocumentationState = {
  prefix: string;
  markdown: string;
};

export type ValidationState = {
  compile_errors: string[];
  feedback: string;
  reviewed_code: string;
};

export type LLMCost = {
  input_tokens: number;
  output_tokens: number;
  model: string;
};

export type AgentState = {
  research: ResearchState;
  generated_code: CodingState;
  generated_tests: Module;
  documentation: DocumentationState;
  validation: ValidationState;
  agentStatus: { [key: string]: string };
  llmCost: LLMCost[];
  messages: any[];
};

export enum TabStatusEnum {
  Done = 'done',
  InProgress = 'inProgress',
  NotStarted = 'notStarted',
};

export enum TabNameEnum {
  Research = 'research',
  Code = 'code',
  Tests = 'tests',
  Documentation = 'documentation',
Validation = 'validation',
};

export const testState: AgentState = {
    research: { problem_statement: 'This is the problem', research_plan: [{"id":1,"query":"Step 1","status":"done"},{"id":2,"query":"Step 2","status":"done"},{"id":3,"query":"Step 3","status":"inProgress"}], current_step: 0, research_results: [], is_complete: false, final_research: '' } , 
    generated_code: {
      "code_plan": [
        {
          "id": 1,
          "name": "Initialize Project",
          "description": "Set up the initial project structure and dependencies.",
          "file_name": "setup.py",
          "status": "done"
        },
        {
          "id": 2,
          "name": "Create Main Module",
          "description": "Develop the main module of the application.",
          "file_name": "main.py",
          "status": "inProgress"
        },
        {
          "id": 3,
          "name": "Implement Feature X",
          "description": "Add feature X to the application.",
          "file_name": "feature_x.py",
          "status": "notStarted"
        }
      ],
      "current_step": 2,
      "modules": [
        {
          "prefix": "Main Application",
          "language": "Python",
          "imports": "import os\nimport sys",
          "code": "def main():\n    print('Hello, World!')",
          "file_name": "main.py",
        },
        {
          "prefix": "Feature X",
          "language": "Python",
          "imports": "import feature_x",
          "code": "def feature_x():\n    pass",
          "file_name": "feature_x.py",
        }
      ],
      "is_complete": false
    },
    generated_tests: { prefix: '', imports: '', code: '', language: '', file_name: '' },  
    documentation: { prefix: '', markdown: '' },
    validation: { compile_errors: [], feedback: '', reviewed_code: '' },
    agentStatus: {
      research: TabStatusEnum.Done,
      code: TabStatusEnum.InProgress,
      tests: TabStatusEnum.NotStarted,
      documentation: TabStatusEnum.NotStarted,
      validation: TabStatusEnum.NotStarted
    },
    messages: [],
    llmCost: [{"model":"claude-3-5-haiku-latest","input_tokens":1000,"output_tokens":500},{"model":"claude-3-5-haiku-latest ","input_tokens":2000,"output_tokens":1000}]
  };