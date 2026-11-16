import type { Metadata } from "next";

import { PrivacyPage } from "../../components/portal/privacy-page";

export const metadata: Metadata = { title: "Privacy and consent" };

export default function Page() {
  return <PrivacyPage />;
}
