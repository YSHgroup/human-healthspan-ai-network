import type { ButtonHTMLAttributes } from "react";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "quiet";
}

export function Button({ variant = "primary", className, ...props }: ButtonProps) {
  const classes = ["healthspan-button", `healthspan-button--${variant}`, className]
    .filter(Boolean)
    .join(" ");

  return <button className={classes} {...props} />;
}
