import type { CSSProperties } from "react";

const css = (vars: Record<string, string | number>) => vars as CSSProperties;

/** Animated double helix, drawn in SVG so it stays crisp and light on every screen size. */
export function Helix({ className }: { className?: string }) {
  const height = 480;
  const turns = 3;
  const amplitude = 34;
  const steps = 60;
  const strandA: string[] = [];
  const strandB: string[] = [];
  for (let i = 0; i <= steps; i += 1) {
    const y = (i / steps) * height;
    const angle = (i / steps) * Math.PI * 2 * turns;
    strandA.push(`${i === 0 ? "M" : "L"}${(60 + amplitude * Math.sin(angle)).toFixed(1)} ${y.toFixed(1)}`);
    strandB.push(`${i === 0 ? "M" : "L"}${(60 - amplitude * Math.sin(angle)).toFixed(1)} ${y.toFixed(1)}`);
  }
  const rungs = Array.from({ length: 22 }, (_, i) => {
    const y = 12 + i * 21.5;
    const angle = (y / height) * Math.PI * 2 * turns;
    const x = amplitude * Math.sin(angle);
    return { y, x1: 60 + x, x2: 60 - x, depth: Math.cos(angle) };
  });

  return (
    <svg
      className={className}
      viewBox={`0 0 120 ${height}`}
      aria-hidden="true"
      focusable="false"
      preserveAspectRatio="xMidYMid meet"
    >
      <defs>
        <linearGradient id="hs-helix-a" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#35b6ff" />
          <stop offset="1" stopColor="#3ee0a1" />
        </linearGradient>
        <linearGradient id="hs-helix-b" x1="0" y1="1" x2="0" y2="0">
          <stop offset="0" stopColor="#2f7bff" />
          <stop offset="1" stopColor="#7be3c0" />
        </linearGradient>
      </defs>
      {rungs.map((rung, index) => (
        <line
          key={rung.y}
          className="hs-helix-rung"
          style={css({ "--d": `${(index % 7) * 0.35}s` })}
          x1={rung.x1}
          x2={rung.x2}
          y1={rung.y}
          y2={rung.y}
          stroke="#8fd6ff"
          strokeWidth={2}
          strokeLinecap="round"
          opacity={0.35 + Math.abs(rung.depth) * 0.45}
        />
      ))}
      <path d={strandB.join(" ")} fill="none" stroke="url(#hs-helix-b)" strokeWidth={5} strokeLinecap="round" />
      <path d={strandA.join(" ")} fill="none" stroke="url(#hs-helix-a)" strokeWidth={5} strokeLinecap="round" />
      <path
        className="hs-helix-flow"
        d={strandA.join(" ")}
        fill="none"
        stroke="#ffffff"
        strokeWidth={2}
        strokeLinecap="round"
        pathLength={100}
      />
    </svg>
  );
}

/** A leafy sprig that sways slowly from its base. */
export function Leaf({ className, flip = false }: { className?: string; flip?: boolean }) {
  return (
    <svg
      className={className}
      viewBox="0 0 160 110"
      aria-hidden="true"
      focusable="false"
      style={flip ? { scale: "-1 1" } : undefined}
    >
      <defs>
        <linearGradient id={`hs-leaf-${flip ? "b" : "a"}`} x1="0" y1="1" x2="1" y2="0">
          <stop offset="0" stopColor="#0f8a4a" />
          <stop offset="1" stopColor="#8fdc6b" />
        </linearGradient>
      </defs>
      <path
        d="M4 98C8 44 54 6 156 8c-4 56-50 96-152 90Z"
        fill={`url(#hs-leaf-${flip ? "b" : "a"})`}
      />
      <path d="M8 96C54 70 96 44 146 14" fill="none" stroke="#e9ffd9" strokeOpacity={0.6} strokeWidth={2} />
    </svg>
  );
}

export function Bubble({
  size,
  className,
  delay = 0,
}: {
  size: number;
  className?: string;
  delay?: number;
}) {
  return (
    <span
      aria-hidden="true"
      className={`hs-bubble ${className ?? ""}`}
      style={css({ "--s": `${size}px`, "--delay": `${delay}s` })}
    />
  );
}
