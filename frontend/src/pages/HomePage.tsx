import type { AppInfo } from "../types/app";

type HomePageProps = {
  apiUrl: string;
  appInfo: AppInfo;
};

export function HomePage({ apiUrl, appInfo }: HomePageProps) {
  return (
    <main>
      <section className="card">
        <h1>{appInfo.name}</h1>
        <p>{appInfo.description}</p>
        <p>
          Phase 1 delivers a clean React + TypeScript + Vite frontend, FastAPI backend foundation,
          and health-check testing.
        </p>
        <p className="meta">Configured API base URL: {apiUrl}</p>
      </section>
    </main>
  );
}
