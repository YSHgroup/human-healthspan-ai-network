import { Field } from "@base-ui/react/field";
import type { ComponentProps } from "react";

import { cn } from "./utils";

function Label({ className, ...props }: ComponentProps<typeof Field.Label>) {
  return (
    <Field.Label
      data-slot="label"
      className={cn(
        "text-sm font-medium leading-none text-foreground peer-disabled:cursor-not-allowed peer-disabled:opacity-60",
        className,
      )}
      {...props}
    />
  );
}

export { Label };
