import { Search } from "lucide-react";
import PageHeader from "../../components/PageHeader";
import { Card, CardContent } from "@/components/ui/card";

export default function DiscoverPage() {
  return (
    <>
      <PageHeader
        eyebrow="Explore the network"
        title="Discover"
        description="Explore people, conversations, and ideas across the healthspan network."
      />
      <Card className="rounded-2xl border-border py-0 text-center shadow-sm">
        <CardContent className="flex flex-col items-center gap-3 p-10">
          <Search aria-hidden="true" className="size-8 text-primary/70" />
          <h2 className="text-lg font-semibold text-primary">Discovery is coming soon</h2>
          <p className="max-w-lg text-sm text-muted-foreground">
            Search and personalized discovery will be added when the API endpoints are available.
          </p>
        </CardContent>
      </Card>
    </>
  );
}
