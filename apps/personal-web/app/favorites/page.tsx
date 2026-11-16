import type { Metadata } from "next";

import { FavoritesPage } from "../../components/portal/favorites-page";

export const metadata: Metadata = { title: "Favorites" };

export default function Page() {
  return <FavoritesPage />;
}
