import Image from "next/image";
import Link from "next/link";
import ApiStatus from "./ApiStatus";

const navigation = [
  { href: "/home", label: "Home", icon: "⌂" },
  { href: "/discover", label: "Discover", icon: "⌕" },
  { href: "/communities", label: "Communities", icon: "◉" },
  { href: "/science", label: "Science", icon: "✳" },
  { href: "/research", label: "Research", icon: "⌬" },
  { href: "/ai", label: "AI", icon: "✧" },
];

export default function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="app-shell">
      <aside className="app-sidebar">
        <Link href="/home" className="app-brand" aria-label="Healthspan Network home">
          <Image
            src="/brand/logo.png"
            alt="Healthspan Network"
            width={1112}
            height={385}
            priority
            className="app-brand-logo"
          />
        </Link>
        <nav className="app-navigation" aria-label="App navigation">
          {navigation.map((item) => (
            <Link className="app-nav-link" href={item.href} key={item.href}>
              <span className="app-nav-icon" aria-hidden="true">{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="app-sidebar-footer">
          <ApiStatus />
          <p>Early access · MVP</p>
        </div>
      </aside>
      <main className="app-main">
        <div className="app-topbar">
          <span>Human Healthspan AI Scientific Network</span>
          <Link href="/">About the network</Link>
        </div>
        <div className="app-content">{children}</div>
      </main>
    </div>
  );
}
