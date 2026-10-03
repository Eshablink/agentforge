import type { AppInfo, ChatResponse, DocumentSummary } from "./types/app";
import { HomePage } from "./pages/HomePage";

const appInfo: AppInfo = {
  name: "AgentForge",
  description: "Secure document RAG with agent tools and conversations",
};

function App() {
  return <HomePage apiUrl={"http://localhost:8000"} appInfo={appInfo} />;
}

export default App;
