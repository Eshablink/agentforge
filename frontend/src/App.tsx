import type { AppInfo } from "./types/app";
import { HomePage } from "./pages/HomePage";
import { apiClient } from "./services/api/client";

const appInfo: AppInfo = {
  name: "AgentForge",
  description: "Production-style agentic AI platform foundation",
};

function App() {
  return <HomePage apiUrl={apiClient.baseUrl} appInfo={appInfo} />;
}

export default App;
