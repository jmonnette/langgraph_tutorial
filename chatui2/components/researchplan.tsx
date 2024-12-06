import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCheckCircle, faSpinner, faExpand, faTimes } from '@fortawesome/free-solid-svg-icons';
import MarkdownRenderer from './markdownrenderer';
import { ResearchState } from './statetypes';

interface ResearchPlanProps {
  researchState: ResearchState;
}

const ResearchPlan: React.FC<ResearchPlanProps> = ({ researchState }) => {
  const [hoveredStep, setHoveredStep] = useState<number | null>(null);
  const [isModal, setIsModal] = useState<boolean>(false);

  const toggleModal = () => {
    if (isModal) {
      // Close modal and reset hover state
      setHoveredStep(null);
    }
    setIsModal(!isModal);
  };

  return researchState && researchState.problem_statement !== '' ? (
    <div style={styles.container}>
      <h2>Problem Statement</h2>
      <p>{researchState.problem_statement}</p>
      <h2>Research Plan</h2>
      <ul style={styles.list}>
        {researchState.research_plan ? researchState.research_plan.map((step, index) => (
          <li
            key={step.id}
            style={styles.listItem}
            onMouseEnter={() => setHoveredStep(index)}
            onMouseLeave={() => setHoveredStep(null)}
          >
            {step.query}
            <span style={styles.icon}>
              {step.status === 'done' && <FontAwesomeIcon icon={faCheckCircle} color="green" />}
              {step.status === 'inProgress' && <FontAwesomeIcon icon={faSpinner} spin />}
            </span>
            {hoveredStep === index && !isModal && (
              <div style={styles.popup}>
                <MarkdownRenderer content={researchState.research_results[index] || 'No results'} />
                <button style={styles.toggleButton} onClick={toggleModal}>
                  <FontAwesomeIcon icon={faExpand} />
                </button>
              </div>
            )}
          </li>
        )) : "No research steps defined"}
      </ul>
      {isModal && hoveredStep !== null && (
        <div style={styles.modal}>
          <div style={styles.modalContent}>
            <button style={styles.closeButton} onClick={toggleModal}>
              <FontAwesomeIcon icon={faTimes} />
            </button>
            <MarkdownRenderer content={researchState.research_results[hoveredStep] || 'No results'} />
          </div>
        </div>
      )}
      {researchState.is_complete && researchState.final_research && (
        <div style={styles.finalResearch}>
          <h2>Final Research</h2>
          <MarkdownRenderer content={researchState.final_research} />
        </div>
      )}
    </div>
  ) : (<div/>)
};

const styles = {
  container: {
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
  },
  list: {
    listStyleType: 'none',
    padding: 0,
  },
  listItem: {
    position: 'relative', // Required for positioning the popup
    display: 'flex',
    alignItems: 'center',
    marginBottom: '10px',
  },
  icon: {
    marginLeft: '10px',
  },
  popup: {
    position: 'absolute',
    top: '100%',
    left: '0',
    backgroundColor: '#f9f9f9',
    border: '1px solid #ccc',
    padding: '10px',
    boxShadow: '0 2px 5px rgba(0, 0, 0, 0.1)',
    zIndex: 1,
    width: '300px', // Adjust width as needed
  },
  toggleButton: {
    position: 'absolute',
    top: '5px',
    right: '5px',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
  },
  modal: {
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  modalContent: {
    backgroundColor: '#fff',
    padding: '20px',
    borderRadius: '5px',
    position: 'relative',
    maxWidth: '80%',
    maxHeight: '80%',
    overflowY: 'auto',
  },
  closeButton: {
    position: 'absolute',
    top: '10px',
    right: '10px',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
  },
  finalResearch: {
    marginTop: '20px',
  },
};

export default ResearchPlan;