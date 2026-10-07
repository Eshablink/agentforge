import { Icon } from "./Icon";

type RuntimeStage = "understand" | "ground" | "act" | "verify";

type Props = {
  stage?: RuntimeStage;
  busy?: boolean;
};

const stages: Array<{ id: RuntimeStage; label: string; caption: string; icon: "spark" | "search" | "wand" | "check" }> = [
  { id: "understand", label: "Understand", caption: "Intent", icon: "spark" },
  { id: "ground", label: "Ground", caption: "Evidence", icon: "search" },
  { id: "act", label: "Act", caption: "Tools", icon: "wand" },
  { id: "verify", label: "Verify", caption: "Result", icon: "check" },
];

export function RuntimePulse({ stage = "understand", busy = false }: Props) {
  const activeIndex = stages.findIndex((item) => item.id === stage);

  return (
    <div
      className={"runtime-pulse " + (busy ? "is-live" : "is-idle")}
      aria-label={busy ? "Agent runtime is active" : "Agent runtime is ready"}
    >
      <div className="runtime-pulse-halo" aria-hidden="true" />
      <div className="runtime-pulse-track" aria-hidden="true">
        {stages.slice(0, -1).map((item, index) => (
          <span
            className={index < activeIndex ? "is-complete" : index === activeIndex ? "is-active" : ""}
            key={item.id}
          />
        ))}
      </div>

      <div className="runtime-pulse-head">
        <span className="runtime-pulse-eyebrow">
          <i className="runtime-pulse-dot" />
          {busy ? "Runtime in motion" : "Runtime ready"}
        </span>
        <span className="runtime-pulse-meta">
          {busy ? "bounded execution" : "safe by design"}
        </span>
      </div>

      <div className="runtime-pulse-grid">
        {stages.map((item, index) => {
          const isActive = index === activeIndex;
          const isComplete = index < activeIndex;

          return (
            <div
              className={
                "runtime-pulse-step" +
                (isActive ? " is-active" : "") +
                (isComplete ? " is-complete" : "")
              }
              key={item.id}
            >
              <span className="runtime-pulse-icon">
                <Icon name={item.icon} />
              </span>
              <span className="runtime-pulse-copy">
                <strong>{item.label}</strong>
                <small>{item.caption}</small>
              </span>
              <span className="runtime-pulse-index">0{index + 1}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
