import type { SVGProps } from "react";

export type IconName =
  | "arrow"
  | "bot"
  | "check"
  | "chevron"
  | "close"
  | "copy"
  | "file"
  | "grid"
  | "logout"
  | "moon"
  | "plus"
  | "search"
  | "send"
  | "settings"
  | "spark"
  | "sun"
  | "trash"
  | "upload"
  | "user"
  | "wand";

type Props = SVGProps<SVGSVGElement> & { name: IconName };

export function Icon({ name, ...props }: Props) {
  const common = {
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.8,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    "aria-hidden": true,
    ...props,
  };

  switch (name) {
    case "arrow":
      return <svg {...common}><path d="M5 12h13" /><path d="m13 6 6 6-6 6" /></svg>;
    case "bot":
      return <svg {...common}><rect x="4" y="7" width="16" height="12" rx="3" /><path d="M12 4v3" /><circle cx="9" cy="12" r="1" /><circle cx="15" cy="12" r="1" /><path d="M9 16h6" /></svg>;
    case "check":
      return <svg {...common}><path d="m5 12 4 4L19 6" /></svg>;
    case "chevron":
      return <svg {...common}><path d="m6 9 6 6 6-6" /></svg>;
    case "close":
      return <svg {...common}><path d="m6 6 12 12M18 6 6 18" /></svg>;
    case "copy":
      return <svg {...common}><rect x="9" y="9" width="10" height="10" rx="2" /><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" /></svg>;
    case "file":
      return <svg {...common}><path d="M6 3h8l4 4v14H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z" /><path d="M14 3v5h5" /><path d="M8 13h6M8 17h4" /></svg>;
    case "grid":
      return <svg {...common}><rect x="4" y="4" width="6" height="6" rx="1" /><rect x="14" y="4" width="6" height="6" rx="1" /><rect x="4" y="14" width="6" height="6" rx="1" /><rect x="14" y="14" width="6" height="6" rx="1" /></svg>;
    case "logout":
      return <svg {...common}><path d="M10 4H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h4" /><path d="m14 16 4-4-4-4M9 12h9" /></svg>;
    case "moon":
      return <svg {...common}><path d="M20 15.5A8.5 8.5 0 0 1 8.5 4a8.5 8.5 0 1 0 11.5 11.5Z" /></svg>;
    case "plus":
      return <svg {...common}><path d="M12 5v14M5 12h14" /></svg>;
    case "search":
      return <svg {...common}><circle cx="10.8" cy="10.8" r="6.3" /><path d="m16 16 4.2 4.2" /></svg>;
    case "send":
      return <svg {...common}><path d="m4 5 16 7-16 7 3-7-3-7Z" /><path d="M7 12h7" /></svg>;
    case "settings":
      return <svg {...common}><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-1.8 1.8-.1-.1a1.7 1.7 0 0 0-1.9-.3l-.2.1a1.7 1.7 0 0 0-1 1.5v.1h-2.5V20a1.7 1.7 0 0 0-1-1.5l-.2-.1a1.7 1.7 0 0 0-1.9.3l-.1.1-1.8-1.8.1-.1a1.7 1.7 0 0 0 .3-1.9l-.1-.2a1.7 1.7 0 0 0-1.5-1H5.1v-2.5h.1a1.7 1.7 0 0 0 1.5-1l.1-.2a1.7 1.7 0 0 0-.3-1.9l-.1-.1 1.8-1.8.1.1a1.7 1.7 0 0 0 1.9.3l.2-.1a1.7 1.7 0 0 0 1-1.5V4.9h2.5V5a1.7 1.7 0 0 0 1 1.5l.2.1a1.7 1.7 0 0 0 1.9-.3l.1-.1 1.8 1.8-.1.1a1.7 1.7 0 0 0-.3 1.9l.1.2a1.7 1.7 0 0 0 1.5 1h.1v2.5h-.1a1.7 1.7 0 0 0-1.5 1Z" /></svg>;
    case "spark":
      return <svg {...common}><path d="m12 3 1.6 5.4L19 10l-5.4 1.6L12 17l-1.6-5.4L5 10l5.4-1.6L12 3Z" /><path d="m19 16 .7 2.3L22 19l-2.3.7L19 22l-.7-2.3L16 19l2.3-.7L19 16Z" /></svg>;
    case "sun":
      return <svg {...common}><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></svg>;
    case "trash":
      return <svg {...common}><path d="M4 7h16M10 11v6M14 11v6M9 7V4h6v3M6 7l1 14h10l1-14" /></svg>;
    case "upload":
      return <svg {...common}><path d="M12 16V4" /><path d="m8 8 4-4 4 4" /><path d="M5 14v5h14v-5" /></svg>;
    case "user":
      return <svg {...common}><circle cx="12" cy="8" r="3" /><path d="M5 20a7 7 0 0 1 14 0" /></svg>;
    case "wand":
      return <svg {...common}><path d="m15 4 5 5M7 17l9-9" /><path d="m5 5 .6 2.2L8 8l-2.4.8L5 11l-.6-2.2L2 8l2.4-.8L5 5Z" /><path d="m19 15 .4 1.6L21 17l-1.6.4L19 19l-.4-1.6L17 17l1.6-.4L19 15Z" /></svg>;
    default:
      return null;
  }
}
