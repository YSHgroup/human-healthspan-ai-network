import type { Metadata } from "next";

import { MessagingPanel } from "@healthspan/ui/communication";

import { PageHeader } from "../../components/portal/page-header";

export const metadata: Metadata = {
  title: "Chat",
  robots: { index: false, follow: false },
};

export default function PersonalMessagesPage() {
  return (
    <>
      <PageHeader
        eyebrow="Home"
        title="Your conversations."
        description="Shared identity keeps your messages available across the portals. Private messages are not used for AI learning."
      />
      <MessagingPanel apiBaseUrl={process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"} />
    </>
  );
}
