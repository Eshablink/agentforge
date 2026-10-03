import type { AppInfo } from "./types/app";
import { HomePage } from "./pages/HomePage";
import { apiClient } from "./services/api/client";

const appInfo: AppInfo = {
  name: "AgentForge",
  description: "PostgreSQL + pgvector document ingestion and RAG foundation",
};

function App() {
  return <HomePage apiUrl={apiClient.baseUrl} appInfo={appInfo} />;
}

export default App;
