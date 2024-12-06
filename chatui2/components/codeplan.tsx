import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCheckCircle, faSpinner } from '@fortawesome/free-solid-svg-icons';
import { CodingState, CodingStep, Module } from './statetypes'; // Adjust the path as necessary

interface CodingComponentProps {
  codingState: CodingState;
}

const CodingComponent: React.FC<CodingComponentProps> = ({ codingState }) => {
  const [activeTab, setActiveTab] = useState<string>('code_plan');

  return (
    <div style={styles.container}>
      <div style={styles.tabHeader}>
        <button
          style={activeTab === 'code_plan' ? styles.activeTab : styles.tab}
          onClick={() => setActiveTab('code_plan')}
        >
          Code Plan
        </button>
        {codingState.modules.map((module) => (
          <button
            key={module.file_name}
            style={activeTab === module.file_name ? styles.activeTab : styles.tab}
            onClick={() => setActiveTab(module.file_name)}
            disabled={module.status !== 'done'}
          >
            {module.file_name}
          </button>
        ))}
      </div>
      <div style={styles.content}>
        {activeTab === 'code_plan' && (
          <ul style={styles.list}>
            {codingState.code_plan.map((step) => (
              <li key={step.id} style={styles.listItem}>
                {step.name}: {step.description}
                <span style={styles.icon}>
                  {step.status === 'done' && <FontAwesomeIcon icon={faCheckCircle} color="green" />}
                  {step.status === 'inProgress' && <FontAwesomeIcon icon={faSpinner} spin />}
                </span>
              </li>
            ))}
          </ul>
        )}
        {codingState.modules.map((module) => (
          activeTab === module.file_name && (
            <div key={module.file_name} style={styles.moduleContent}>
              <h3>{module.file_name}</h3>
              <pre style={styles.codeBlock}>
                <code>
                  {module.imports}
                  {'\n\n'}
                  {module.code}
                </code>
              </pre>
            </div>
          )
        ))}
      </div>
    </div>
  );
};

const styles = {
  container: {
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
  },
  tabHeader: {
    display: 'flex',
    justifyContent: 'flex-start',
    marginBottom: '10px',
  },
  tab: {
    padding: '10px 20px',
    cursor: 'pointer',
    backgroundColor: '#e0e0e0',
    border: '1px solid #ccc',
    borderBottom: 'none',
    borderRadius: '5px 5px 0 0',
    marginRight: '5px',
  },
  activeTab: {
    padding: '10px 20px',
    cursor: 'pointer',
    backgroundColor: '#f9f9f9',
    border: '1px solid #ccc',
    borderBottom: 'none',
    borderRadius: '5px 5px 0 0',
    fontWeight: 'bold',
    marginRight: '5px',
  },
  content: {
    border: '1px solid #ccc',
    borderRadius: '0 0 5px 5px',
    padding: '10px',
  },
  list: {
    listStyleType: 'none',
    padding: 0,
  },
  listItem: {
    display: 'flex',
    alignItems: 'center',
    marginBottom: '10px',
  },
  icon: {
    marginLeft: '10px',
  },
  moduleContent: {
    padding: '10px',
  },
  codeBlock: {
    backgroundColor: '#f7f7f7',
    padding: '10px',
    borderRadius: '5px',
    overflowX: 'auto',
  },
};

export default CodingComponent;