"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { Search } from "lucide-react";
import PageHeader from "../../components/PageHeader";
import { Button } from "@healthspan/ui/button";
import { Input } from "@healthspan/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { searchNetwork, type SearchResults } from "@/lib/api";

export default function DiscoverPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      setResults(await searchNetwork(query.trim()));
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "Unable to search the network.");
      setResults(null);
    } finally {
      setLoading(false);
    }
  }

  const hasResults = results && Object.values(results).some((items) => items.length > 0);

  return (
    <>
      <PageHeader
        eyebrow="Explore the network"
        title="Discover"
        description="Search public conversations, research projects, communities, and member profiles."
      />
      <form className="mb-6 flex flex-col gap-3 sm:flex-row" onSubmit={submitSearch}>
        <label className="sr-only" htmlFor="network-search">Search the network</label>
        <Input autoComplete="off" id="network-search" maxLength={200} minLength={2} onChange={(event) => setQuery(event.target.value)} placeholder="Search at least 2 characters…" required value={query} />
        <Button disabled={loading || query.trim().length < 2} type="submit">
          <Search aria-hidden="true" /> {loading ? "Searching…" : "Search"}
        </Button>
      </form>
      {error && <p className="mb-4 text-sm text-destructive" role="alert">{error}</p>}
      {results && !hasResults && !error && <p className="text-sm text-muted-foreground">No public results matched that search.</p>}
      {results && hasResults && (
        <div className="space-y-5">
          {results.people.length > 0 && (
            <section aria-label="People">
              <h2 className="mb-3 text-lg font-semibold">People</h2>
              <div className="grid gap-3 md:grid-cols-2">
                {results.people.map((person) => (
                  <Link href={`/members/${person.id}`} key={person.id}>
                    <Card className="h-full transition-colors hover:border-primary/40">
                      <CardContent className="p-4">
                        <p className="font-medium">{person.display_name}</p>
                        <p className="text-sm text-muted-foreground">{person.role.replaceAll("_", " ")}</p>
                      </CardContent>
                    </Card>
                  </Link>
                ))}
              </div>
            </section>
          )}
          {results.communities.length > 0 && (
            <section aria-label="Communities">
              <h2 className="mb-3 text-lg font-semibold">Communities</h2>
              <div className="grid gap-3 md:grid-cols-2">
                {results.communities.map((community) => (
                  <Link href={`/communities/${community.id}`} key={community.id}>
                    <Card className="h-full transition-colors hover:border-primary/40">
                      <CardContent className="p-4">
                        <p className="font-medium">{community.name}</p>
                        <p className="text-sm text-muted-foreground">{community.topic}</p>
                      </CardContent>
                    </Card>
                  </Link>
                ))}
              </div>
            </section>
          )}
          {results.projects.length > 0 && (
            <section aria-label="Research projects">
              <h2 className="mb-3 text-lg font-semibold">Research projects</h2>
              <div className="grid gap-3 md:grid-cols-2">
                {results.projects.map((project) => (
                  <Link href={`/research#research-project-${project.id}`} key={project.id}>
                    <Card className="h-full transition-colors hover:border-primary/40">
                      <CardHeader><CardTitle className="text-base">{project.title}</CardTitle></CardHeader>
                      <CardContent><p className="text-sm text-muted-foreground">{project.description}</p></CardContent>
                    </Card>
                  </Link>
                ))}
              </div>
            </section>
          )}
          {results.posts.length > 0 && (
            <section aria-label="Posts">
              <h2 className="mb-3 text-lg font-semibold">Posts</h2>
              <div className="grid gap-3">
                {results.posts.map((post) => (
                  <Link href={`/home#post-${post.id}`} key={post.id}>
                    <Card className="transition-colors hover:border-primary/40">
                      <CardContent className="space-y-2 p-4">
                        <p className="whitespace-pre-wrap text-sm">{post.body}</p>
                        <span className="text-xs text-muted-foreground">{post.classification.replaceAll("_", " ")}</span>
                      </CardContent>
                    </Card>
                  </Link>
                ))}
              </div>
            </section>
          )}
        </div>
      )}
      {!results && !error && <p className="text-sm text-muted-foreground">Results include only public member profiles, posts, projects, and communities.</p>}
    </>
  );
}
