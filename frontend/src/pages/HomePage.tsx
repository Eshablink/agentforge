type HomePageProps = {
  apiUrl: string;
};

export function HomePage({ apiUrl }: HomePageProps) {
  return (
    <main>
      <section className="card">
        <h1>AgentForge</h1>
        <p>
          AgentForge is a full-stack agentic AI platform foundation. Phase 1 provides frontend and
          backend scaffolding, health checks, and test-ready structure.
        </p>
        <p className="meta">Configured API base URL: {apiUrl}</p>
      </section>
    </main>
  );
}
