import React from 'react';
import MarkdownRenderer from './markdownrenderer';
import CodeBlock from './codeblock';
import { CodingState, ResearchState } from './statetypes';
import ResearchPlan from './researchplan';
import CodePlan from './codeplan';

interface TabContentProps {
  activeTab: string;
  research: ResearchState;
  code: CodingState;
  tests: string;
  documentation: string;
  feedback: string;
  reviewed_code: string;
}

const TabContent: React.FC<TabContentProps> = ({ activeTab, research, code, tests, documentation, feedback, reviewed_code }) => (
  <div style={styles.content}>
    {activeTab === 'research' && (
      <div style={styles.markdownBox}>
        <ResearchPlan researchState={research} />
      </div>
    )}
    {activeTab === 'code' && (
      <div style={styles.markdownBox}>
        <CodePlan codingState={code} />
      </div>
    )}
    {activeTab === 'documentation' && (
      <div style={styles.markdownBox}>
        <MarkdownRenderer content={documentation} />
      </div>
    )}
    {activeTab === 'tests' && (
      <div style={styles.markdownBox}>
        <CodeBlock language="python" value={tests} />
      </div>
    )}
    {activeTab === 'validation' && (
      <div style={styles.markdownBox}>
        <MarkdownRenderer content={feedback} />
      </div>
    )}
  </div>
);

const styles = {
  content: {
    width: '100%',
    maxWidth: '950px',
    border: '1px solid #ccc',
    borderRadius: '0 0 5px 5px',
    overflow: 'hidden',
  },
  markdownBox: {
    padding: '10px',
    height: '500px',
    width: '100%',
    overflowY: 'scroll',
    overflowX: 'hidden',
    backgroundColor: '#f9f9f9',
  },
};

export default TabContent;