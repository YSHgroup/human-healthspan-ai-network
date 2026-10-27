import { getCommunities } from "../../../lib/data";
import PageHeader from "../../components/PageHeader";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default async function CommunitiesPage() {
  const allCommunities = await getCommunities();

  return (
    <>
      <PageHeader
        eyebrow="Find your people"
        title="Communities"
        description="Starter communities are sample data while the communities API is being built."
      />
      <section className="grid gap-4 md:grid-cols-2" aria-label="Starter communities">
        {allCommunities.map((community) => (
          <Card className="gap-0 rounded-2xl border-border py-0 shadow-sm" key={community.id}>
            <CardHeader className="gap-3 px-5 pt-5 sm:px-6 sm:pt-6">
              <Badge className="font-medium" variant="secondary">{community.topic}</Badge>
              <CardTitle className="text-lg text-primary">{community.name}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 p-5 pt-3 sm:px-6 sm:pb-6">
              <p className="text-sm leading-6 text-muted-foreground">{community.description}</p>
              <p className="text-xs text-muted-foreground">
                {community.members.toLocaleString()} sample members
              </p>
            </CardContent>
          </Card>
        ))}
      </section>
    </>
  );
}
