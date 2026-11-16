import { Button as ButtonPrimitive } from "@base-ui/react/button";
import { cva, type VariantProps } from "class-variance-authority";
import { LoaderCircle } from "lucide-react";
import type { ComponentProps, ReactNode } from "react";

import { cn } from "./utils";

export const buttonVariants = cva(
  "inline-flex shrink-0 items-center justify-center gap-2 whitespace-nowrap rounded-md border border-transparent text-sm font-medium transition-[color,background-color,box-shadow,transform] duration-200 outline-none hover:-translate-y-0.5 active:translate-y-0 active:scale-[0.98] focus-visible:ring-[3px] focus-visible:ring-ring/40 disabled:pointer-events-none disabled:opacity-55 disabled:hover:translate-y-0 disabled:active:scale-100 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0 motion-reduce:transform-none",
  {
    variants: {
      variant: {
        default:
          "bg-gradient-to-br from-primary to-primary/85 text-primary-foreground shadow-sm hover:shadow-md",
        destructive: "bg-danger text-danger-foreground shadow-sm hover:shadow-md",
        outline: "border-border bg-card text-foreground shadow-xs hover:bg-accent hover:shadow-sm",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/75",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "h-auto p-0 text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "min-h-11 px-4 py-2",
        sm: "min-h-11 rounded-md px-3",
        lg: "min-h-12 rounded-lg px-6 sm:px-8",
        icon: "size-11",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

type ButtonProps = ComponentProps<typeof ButtonPrimitive> &
  VariantProps<typeof buttonVariants> & {
    isLoading?: boolean;
    children?: ReactNode;
  };

function Button({ className, variant, size, isLoading = false, children, ...props }: ButtonProps) {
  return (
    <ButtonPrimitive
      data-slot="button"
      className={cn(buttonVariants({ variant, size }), className)}
      disabled={isLoading || props.disabled}
      aria-busy={isLoading || props["aria-busy"]}
      {...props}
    >
      {isLoading && (
        <LoaderCircle aria-hidden="true" className="animate-spin motion-reduce:animate-none" />
      )}
      {children}
    </ButtonPrimitive>
  );
}

export { Button };
