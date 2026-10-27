import { Sparkles } from "lucide-react";
import PageHeader from "../../components/PageHeader";
import { Card, CardContent } from "@/components/ui/card";

export default function AiPage() {
  return (
    <>
      <PageHeader
        eyebrow="Intelligence layer"
        title="AI"
        description="AI features are designed to support research with transparent, grounded evidence."
      />
      <Card className="rounded-2xl border-border py-0 text-center shadow-sm">
        <CardContent className="flex flex-col items-center gap-3 p-10">
          <Sparkles aria-hidden="true" className="size-8 text-primary/70" />
          <h2 className="text-lg font-semibold text-primary">AI tools are coming soon</h2>
          <p className="max-w-lg text-sm text-muted-foreground">
            AI endpoints are planned for a later API round.
          </p>
        </CardContent>
      </Card>
    </>
  );
}
