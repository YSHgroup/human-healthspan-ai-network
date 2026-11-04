"use client";

import {
  motion,
  useInView,
  useMotionValue,
  useReducedMotion,
  useTransform,
  animate,
} from "motion/react";
import type { ComponentProps, ReactNode } from "react";
import { useEffect, useRef } from "react";

import { cn } from "./utils";

function Reveal({
  className,
  delay = 0,
  children,
  ...props
}: ComponentProps<typeof motion.div> & { delay?: number; children: ReactNode }) {
  const reduceMotion = useReducedMotion();

  return (
    <motion.div
      initial={reduceMotion ? false : { opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.15 }}
      transition={{ duration: reduceMotion ? 0 : 0.34, delay, ease: [0.22, 1, 0.36, 1] }}
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  );
}

function StatCard({
  label,
  value,
  detail,
  className,
}: {
  label: string;
  value: number;
  detail: string;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, amount: 0.6 });
  const reduceMotion = useReducedMotion();
  const count = useMotionValue(reduceMotion ? value : 0);
  const formatted = useTransform(count, (latest) => Math.round(latest).toLocaleString());

  useEffect(() => {
    if (!inView || reduceMotion) return;
    const controls = animate(count, value, { duration: 0.4, ease: "easeOut" });
    return () => controls.stop();
  }, [count, inView, reduceMotion, value]);

  return (
    <div
      ref={ref}
      className={cn("rounded-xl border border-border/80 bg-card/80 p-5 shadow-xs", className)}
    >
      <p className="text-sm font-medium text-muted-foreground">{label}</p>
      <motion.p className="mt-2 font-display text-3xl tracking-tight text-foreground">
        {reduceMotion ? value.toLocaleString() : formatted}
      </motion.p>
      <p className="mt-1 text-xs text-muted-foreground">{detail}</p>
    </div>
  );
}

export { Reveal, StatCard };
