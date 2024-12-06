import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCheckCircle, faSpinner } from '@fortawesome/free-solid-svg-icons';

interface TabHeaderProps<N,S> {
  activeTab: N;
  setActiveTab: (tab: N) => void;
  availableTabs: Set<N>; // Set of available tab names
  tabStatuses: Map<N,S>; // Status of each tab
  tabs: { name: N, label: string }[];
}

const TabHeader = <N, S>({ activeTab, setActiveTab, availableTabs, tabStatuses, tabs }: TabHeaderProps<N, S>): React.ReactElement => {

  return (
    <div style={styles.tabHeader}>
      {tabs.map((tab) => {
        const isActive = activeTab === tab.name;
        const isAvailable = availableTabs.has(tab.name);
        const tabStyle = isActive ? styles.activeTab : isAvailable ? styles.tab : styles.unavailableTab;
        const tabStatus = tabStatuses.get(tab.name);

        return (
          <button
            key={tab.name as string}
            style={tabStyle}
            onClick={() => isAvailable && setActiveTab(tab.name)}
            disabled={!isAvailable}
          >
            {tab.label}
            {
              tabStatus != 'notStarted' && (
              <span style={styles.icon}>
                {tabStatus === 'done' ? (
                  <FontAwesomeIcon icon={faCheckCircle} color="green" />
                ) : (
                  <FontAwesomeIcon icon={faSpinner} spin />
                )}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
};

const styles = {
  tabHeader: {
    display: 'flex',
    justifyContent: 'flex-start',
    marginBottom: '10px',
    width: '100%',
  },
  tab: {
    padding: '10px 20px',
    cursor: 'pointer',
    backgroundColor: '#e0e0e0',
    border: '1px solid #ccc',
    borderBottom: 'none',
    borderRadius: '5px 5px 0 0',
    marginRight: '5px',
    display: 'flex',
    alignItems: 'center',
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
    display: 'flex',
    alignItems: 'center',
  },
  unavailableTab: {
    padding: '10px 20px',
    cursor: 'not-allowed',
    backgroundColor: '#d3d3d3',
    border: '1px solid #aaa',
    borderBottom: 'none',
    borderRadius: '5px 5px 0 0',
    marginRight: '5px',
    color: '#777',
  },
  icon: {
    marginLeft: '10px',
  },
};

export default TabHeader;