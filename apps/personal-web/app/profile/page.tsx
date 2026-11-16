import type { Metadata } from "next";

import { ProfilePage } from "../../components/portal/profile-page";

export const metadata: Metadata = { title: "Profile" };

export default function Page() {
  return <ProfilePage />;
}
