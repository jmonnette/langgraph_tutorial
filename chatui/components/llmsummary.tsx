import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faDollarSign, faTimes } from '@fortawesome/free-solid-svg-icons';
import { LLMCost } from './statetypes'; // Adjust the path as necessary

interface LLMSummaryProps {
  llmState: LLMCost[];
}

const modelPrices = {
  "claude-3-5-haiku": { input_tokens: 0.000001, output_tokens: 0.000005 },
  "claude-3-5-sonnet": { input_tokens: 0.000003, output_tokens: 0.000015 },
};

const LLMSummary: React.FC<LLMSummaryProps> = ({ llmState }) => {
  const [showPopup, setShowPopup] = useState<boolean>(false);

  // Helper function to trim model name
  const getModelKey = (model: string) => {
    const parts = model.split('-');
    return parts.slice(0, parts.length - 1).join('-');
  };

  // Aggregate costs by model
  const costsByModel = llmState.reduce((acc, cost) => {
    const modelKey = getModelKey(cost.model);
    if (!acc[modelKey]) {
      acc[modelKey] = { input_tokens: 0, output_tokens: 0, cost: 0 };
    }
    const price = modelPrices[modelKey];
    acc[modelKey].input_tokens += cost.input_tokens;
    acc[modelKey].output_tokens += cost.output_tokens;
    acc[modelKey].cost +=
      cost.input_tokens * price.input_tokens + cost.output_tokens * price.output_tokens;
    return acc;
  }, {} as Record<string, { input_tokens: number; output_tokens: number; cost: number }>);

  // Calculate overall totals
  const totals = Object.values(costsByModel).reduce(
    (acc, modelCost) => {
      acc.input_tokens += modelCost.input_tokens;
      acc.output_tokens += modelCost.output_tokens;
      acc.cost += modelCost.cost;
      return acc;
    },
    { input_tokens: 0, output_tokens: 0, cost: 0 }
  );

  return (
    <div style={styles.container}>
      <div style={styles.iconContainer} onClick={() => setShowPopup(true)}>
        <FontAwesomeIcon icon={faDollarSign} size="1x" />
      </div>
      {showPopup && (
        <div style={styles.popup}>
          <div style={styles.popupContent}>
            <button style={styles.closeButton} onClick={() => setShowPopup(false)}>
              <FontAwesomeIcon icon={faTimes} />
            </button>
            <h3>LLM Cost Summary</h3>
            <ul style={styles.list}>
              {Object.entries(costsByModel).map(([model, cost]) => (
                <li key={model} style={styles.listItem}>
                  <strong>{model}</strong>: ${cost.cost.toFixed(2)}
                  <div>Input Tokens: {cost.input_tokens}</div>
                  <div>Output Tokens: {cost.output_tokens}</div>
                </li>
              ))}
            </ul>
            <div style={styles.total}>
              <strong>Total Cost: {totals.cost.toFixed(2)}$</strong>
              <div>Total Input Tokens: {totals.input_tokens}</div>
              <div>Total Output Tokens: {totals.output_tokens}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    position: 'relative',
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
  },
  iconContainer: {
    cursor: 'pointer',
  },
  popup: {
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
  popupContent: {
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
  list: {
    listStyleType: 'none',
    padding: 0,
  },
  listItem: {
    marginBottom: '10px',
  },
  total: {
    marginTop: '20px',
    fontWeight: 'bold',
  },
};

export default LLMSummary;