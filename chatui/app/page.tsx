"use client"

import RootLayout from './layout';
import ResearchAndCodeViewer from "../components/content";
import { CopilotSidebar } from "@copilotkit/react-ui";

function App() {
  return (
    <RootLayout>
      <CopilotSidebar
        defaultOpen={true}
        instructions={"You are assisting the user as best as you can. Answer in the best way possible given the data you have."}
        labels={{
          title: "Assistant",
          initial: "How can I help you today?",
        }}
      >
        <ResearchAndCodeViewer />
      </CopilotSidebar>
    </RootLayout>
  );
}

export default App; 