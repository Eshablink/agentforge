import { apiClient } from "./services/api/client";
import { HomePage } from "./pages/HomePage";

function App() {
  const apiUrl = apiClient.baseUrl;

  return <HomePage apiUrl={apiUrl} />;
}

export default App;
