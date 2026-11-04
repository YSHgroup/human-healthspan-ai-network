"use client";

import { useEffect, useState } from "react";
import { Button } from "@healthspan/ui/button";
import { Command } from "@healthspan/ui/command";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@healthspan/ui/dialog";
import {
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandShortcut,
} from "@healthspan/ui/command";
import { toast } from "@healthspan/ui/sonner";
import { Search } from "lucide-react";

const commands = [
  "Open workspace overview",
  "View project access",
  "Browse evidence classes",
  "Review verification status",
];

function ResearcherCommandPalette() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    function handleShortcut(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setOpen((isOpen) => !isOpen);
      }
    }

    window.addEventListener("keydown", handleShortcut);
    return () => window.removeEventListener("keydown", handleShortcut);
  }, []);

  function chooseCommand(command: string) {
    setOpen(false);
    toast.info(`${command} is planned. No research data is connected.`);
  }

  return (
    <>
      <Button
        variant="outline"
        className="w-full justify-between sm:w-auto"
        onClick={() => setOpen(true)}
        aria-keyshortcuts="Control+K Meta+K"
      >
        <span className="inline-flex items-center gap-2">
          <Search aria-hidden="true" />
          Search workspace
        </span>
        <kbd className="hidden rounded border border-border bg-muted px-1.5 py-0.5 text-[0.65rem] font-medium text-muted-foreground sm:inline">
          Ctrl K
        </kbd>
      </Button>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="gap-0 overflow-hidden p-0" showCloseButton={false}>
          <DialogHeader className="sr-only">
            <DialogTitle>Research workspace command palette</DialogTitle>
            <DialogDescription>
              Search planned workspace actions. No project or research data is connected.
            </DialogDescription>
          </DialogHeader>
          <Command>
            <CommandInput placeholder="Search planned actions…" />
            <CommandList>
              <CommandEmpty>No matching workspace actions.</CommandEmpty>
              <CommandGroup heading="Planned workspace actions">
                {commands.map((command) => (
                  <CommandItem key={command} onSelect={() => chooseCommand(command)}>
                    {command}
                    <CommandShortcut>Planned</CommandShortcut>
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
        </DialogContent>
      </Dialog>
    </>
  );
}

export { ResearcherCommandPalette };
