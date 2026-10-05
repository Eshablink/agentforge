import type { AppInfo } from "./types/app";
import { HomePage } from "./pages/HomePage";
import { apiClient } from "./services/api/client";

const appInfo: AppInfo = {
  name: "AgentForge",
  description: "Secure document RAG with agent tools and conversations",
};

function App() {
  return <HomePage apiUrl={apiClient.baseUrl || "same origin"} appInfo={appInfo} />;
}

export default App;
