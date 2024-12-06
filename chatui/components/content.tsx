"use client"

import React, { useState, useEffect } from 'react';
import TabHeader from './tabheader';
import TabContent from './tabcontent';
import { useCoAgent } from "@copilotkit/react-core"; 
import { ResearchState, ResearchStep, TabNameEnum, TabStatusEnum, AgentState } from './statetypes';
import { testState } from './statetypes';
import LLMSummary from './llmsummary';


const tabs = [
  { name: TabNameEnum.Research, label: 'Research Results' },
  { name: TabNameEnum.Code, label: 'Code Results' },
  { name: TabNameEnum.Tests, label: 'Test Generation Results' },
  { name: TabNameEnum.Documentation, label: 'Documentation Results' },
  { name: TabNameEnum.Validation, label: 'Validation Results' },
];

const isAvailable = (agentState: AgentState, tabName: TabNameEnum): boolean => {
  return agentState.agentStatus ? agentState.agentStatus[tabName] != TabStatusEnum.NotStarted : false;
};

const ResearchAndCodeViewer: React.FC = () => {

const [state, setAgentState] = useState<AgentState>(testState);

/*   const { state } = useCoAgent<AgentState>({ name: 'code-solution-agent', initialState: { 
    research: { problem_statement: '', research_plan: [], current_step: 0, research_results: [], is_complete: false, final_research: '' } , 
    generated_code: { prefix: '', imports: '', code: '' }, 
    generated_tests: { prefix: '', imports: '', code: '' }, 
    documentation: { prefix: '', markdown: '' }, 
    validation: { compile_errors: [], feedback: '', reviewed_code: '' }, 
    agentStatus: { research: TabStatusEnum.NotStarted, code: TabStatusEnum.NotStarted, tests: TabStatusEnum.NotStarted, documentation: TabStatusEnum.NotStarted }, messages: [] 
  } }); */

  // console.info('state', state);
  
  const [activeTab, setActiveTab] = useState<TabNameEnum>(TabNameEnum.Research);
  const [availableTabs, setAvailableTabs] = useState<Set<TabNameEnum>>(new Set());
  const [tabStatuses, setTabStatuses] = useState<Map<TabNameEnum, TabStatusEnum>>(new Map());


  // Update available tabs based on the state
  useEffect(() => {
    const newAvailableTabs = new Set<TabNameEnum>();
    const newTabStatuses = new Map<TabNameEnum, TabStatusEnum>();
    
    tabs.forEach(({ name }) => {
      if (isAvailable(state, name)) {
        newAvailableTabs.add(name);
      }
      if(state.agentStatus)
        newTabStatuses.set(name, state.agentStatus[name] as TabStatusEnum);
    });

    setAvailableTabs(newAvailableTabs);
    setTabStatuses(newTabStatuses);
  }, [state]);

  return (
    <div style={styles.container}>
      <div style={styles.headerContainer}>
        <TabHeader
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          availableTabs={availableTabs}
          tabs={tabs}
          tabStatuses={tabStatuses}
        />
        <LLMSummary llmState={state.llmCost} />
      </div>
      <TabContent
        activeTab={activeTab}
        research={state.research}
        code={state.generated_code}
        tests={isAvailable(state, TabNameEnum.Tests) ? state.generated_tests.imports + '\n\n' + state.generated_tests.code : ''}
        documentation={isAvailable(state, TabNameEnum.Documentation) ? state.documentation.markdown : ''}
        feedback={isAvailable(state, TabNameEnum.Validation) ? state.validation.feedback : ''}
        reviewed_code={isAvailable(state, TabNameEnum.Validation) ? state.validation.reviewed_code : ''}
      />
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
    maxWidth: '950px',
    width: '100%',
  },
  headerContainer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    width: '100%',
    marginBottom: '-18px',
  },
};

export default ResearchAndCodeViewer;