"use client";

import { FormEvent, useState } from "react";
import { Search } from "lucide-react";
import PageHeader from "../../components/PageHeader";
import { Badge } from "@healthspan/ui/badge";
import { Button } from "@healthspan/ui/button";
import { Input } from "@healthspan/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { searchLiterature } from "@/lib/api";

type Literature = Awaited<ReturnType<typeof searchLiterature>>[number];

export default function SciencePage() {
  const [query, setQuery] = useState("");
  const [entries, setEntries] = useState<Literature[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      setEntries(await searchLiterature(query.trim()));
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "Unable to search scientific literature.");
      setEntries(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="Evidence and knowledge"
        title="Science"
        description="Search literature metadata attached to public research projects. Documents and full-text indexing are not yet available."
      />
      <form className="mb-6 flex flex-col gap-3 sm:flex-row" onSubmit={submitSearch}>
        <label className="sr-only" htmlFor="science-search">Search literature</label>
        <Input autoComplete="off" id="science-search" maxLength={200} minLength={2} onChange={(event) => setQuery(event.target.value)} placeholder="Search title or author…" required value={query} />
        <Button disabled={loading || query.trim().length < 2} type="submit">
          <Search aria-hidden="true" /> {loading ? "Searching…" : "Search papers"}
        </Button>
      </form>
      {error && <p className="mb-4 text-sm text-destructive" role="alert">{error}</p>}
      {entries && entries.length === 0 && !error && <p className="text-sm text-muted-foreground">No public literature records matched that search.</p>}
      <section className="grid gap-4" aria-label="Scientific literature">
        {entries?.map((entry) => (
          <Card className="rounded-2xl shadow-sm" key={entry.id}>
            <CardHeader>
              <div className="flex flex-wrap items-center justify-between gap-2">
                <Badge variant="secondary">{entry.source_type}</Badge>
                {entry.publication_year && <span className="text-sm text-muted-foreground">{entry.publication_year}</span>}
              </div>
              <CardTitle className="text-lg">{entry.title}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {entry.authors && <p className="text-sm text-muted-foreground">{entry.authors}</p>}
              {entry.doi && <p className="text-sm">DOI: {entry.doi}</p>}
              {entry.source_url && <a className="text-sm text-primary hover:underline" href={entry.source_url} rel="noreferrer" target="_blank">Open source</a>}
            </CardContent>
          </Card>
        ))}
      </section>
      {!entries && !error && <p className="text-sm text-muted-foreground">Search is limited to literature records linked to public research projects.</p>}
    </>
  );
}
