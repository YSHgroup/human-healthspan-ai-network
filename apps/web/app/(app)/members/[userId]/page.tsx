"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import PageHeader from "@/app/components/PageHeader";
import { Button } from "@healthspan/ui/button";
import { Badge } from "@healthspan/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { followMember, getPublicMember, unfollowMember, type PublicMember } from "@/lib/api";
import { useSession } from "@/lib/session";

export default function PublicMemberPage() {
  const { userId } = useParams<{ userId: string }>();
  const { user } = useSession();
  const [member, setMember] = useState<PublicMember | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const loadMember = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setMember(await getPublicMember(userId));
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "Unable to load this public profile.");
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    void loadMember();
  }, [loadMember]);

  async function toggleFollow() {
    if (!member) return;
    setBusy(true);
    setError("");
    try {
      if (member.is_following) await unfollowMember(member.id);
      else await followMember(member.id);
      setMember({ ...member, is_following: !member.is_following });
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "Unable to update your follow.");
    } finally {
      setBusy(false);
    }
  }

  if (loading) return <p className="text-sm text-muted-foreground">Loading public profile…</p>;
  if (!member) return <p className="text-sm text-destructive" role="alert">{error || "This public profile is unavailable."}</p>;
  const { profile } = member;
  const isOwnProfile = user?.id === member.id;

  return (
    <>
      <PageHeader eyebrow="Member profile" title={profile.display_name} description={profile.bio || "A member of the Healthspan Network."} />
      {error && <p className="mb-4 text-sm text-destructive" role="alert">{error}</p>}
      <Card className="rounded-2xl shadow-sm">
        <CardContent className="space-y-5 p-6">
          {!isOwnProfile && user && (
            <Button disabled={busy} onClick={() => void toggleFollow()} type="button" variant={member.is_following ? "outline" : "default"}>
              {busy ? "Updating…" : member.is_following ? "Following" : "Follow"}
            </Button>
          )}
          {(profile.location || profile.timezone || profile.organization_affiliation) && (
            <dl className="grid gap-3 text-sm sm:grid-cols-2">
              {profile.location && <div><dt className="font-medium">Location</dt><dd className="text-muted-foreground">{profile.location}</dd></div>}
              {profile.timezone && <div><dt className="font-medium">Time zone</dt><dd className="text-muted-foreground">{profile.timezone}</dd></div>}
              {profile.organization_affiliation && <div><dt className="font-medium">Affiliation</dt><dd className="text-muted-foreground">{profile.organization_affiliation}</dd></div>}
              {profile.researcher_identifier && <div><dt className="font-medium">Researcher identifier</dt><dd className="text-muted-foreground">{profile.researcher_identifier}</dd></div>}
            </dl>
          )}
          {[
            ["Interests", profile.interests],
            ["Topics", profile.topics],
            ["Expertise", profile.expertise],
          ].map(([label, values]) => (
            Array.isArray(values) && values.length > 0 && (
              <div key={String(label)}>
                <h2 className="mb-2 text-sm font-medium">{label}</h2>
                <div className="flex flex-wrap gap-2">
                  {values.map((value) => <Badge key={value} variant="secondary">{value}</Badge>)}
                </div>
              </div>
            )
          ))}
        </CardContent>
      </Card>
    </>
  );
}
