import { Microscope } from "lucide-react";
import PageHeader from "../../components/PageHeader";
import { Card, CardContent } from "@/components/ui/card";

export default function SciencePage() {
  return (
    <>
      <PageHeader
        eyebrow="Evidence and knowledge"
        title="Science"
        description="Explore evidence, papers, and scientific discussions."
      />
      <Card className="rounded-2xl border-border py-0 text-center shadow-sm">
        <CardContent className="flex flex-col items-center gap-3 p-10">
          <Microscope aria-hidden="true" className="size-8 text-primary/70" />
          <h2 className="text-lg font-semibold text-primary">Science tools are coming soon</h2>
          <p className="max-w-lg text-sm text-muted-foreground">
            Evidence and literature features will follow as the API grows.
          </p>
        </CardContent>
      </Card>
    </>
  );
}
