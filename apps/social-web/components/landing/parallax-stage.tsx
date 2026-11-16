"use client";

import { useEffect, useRef, type ReactNode } from "react";

/**
 * Gives children with the `.hs-layer` class a gentle pointer parallax. Each layer sets its own
 * `--depth`. Disabled for touch input and when the visitor prefers reduced motion.
 */
export function ParallaxStage({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    const query = window.matchMedia("(prefers-reduced-motion: reduce)");
    let frame = 0;

    function setPosition(x: number, y: number) {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        node?.style.setProperty("--px", x.toFixed(3));
        node?.style.setProperty("--py", y.toFixed(3));
      });
    }

    function onMove(event: PointerEvent) {
      if (query.matches || event.pointerType !== "mouse" || !node) return;
      const rect = node.getBoundingClientRect();
      setPosition(
        ((event.clientX - rect.left) / rect.width - 0.5) * 2,
        ((event.clientY - rect.top) / rect.height - 0.5) * 2,
      );
    }

    const onLeave = () => setPosition(0, 0);
    node.addEventListener("pointermove", onMove);
    node.addEventListener("pointerleave", onLeave);
    return () => {
      cancelAnimationFrame(frame);
      node.removeEventListener("pointermove", onMove);
      node.removeEventListener("pointerleave", onLeave);
    };
  }, []);

  return (
    <div ref={ref} className={className}>
      {children}
    </div>
  );
}
