"use client";

import Image from "next/image";
import { ArrowRight, ChevronDown, Menu, Search, X } from "lucide-react";
import { useCallback, useEffect, useRef, useState, type ReactNode } from "react";

export type NavItem = { label: string; href: string; hint?: string };
export type NavGroup = { label: string; items: NavItem[] };

export function LandingHeader({
  groups,
  joinHref,
  loginHref,
  searchHref,
  themeToggle,
}: {
  groups: NavGroup[];
  joinHref: string;
  loginHref: string;
  searchHref: string;
  themeToggle: ReactNode;
}) {
  const [openGroup, setOpenGroup] = useState<number | null>(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const navRef = useRef<HTMLElement>(null);
  const headerRef = useRef<HTMLElement>(null);

  const closeAll = useCallback(() => {
    setOpenGroup(null);
    setMobileOpen(false);
  }, []);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    function onPointerDown(event: PointerEvent) {
      if (headerRef.current && !headerRef.current.contains(event.target as Node)) closeAll();
    }
    function onKey(event: KeyboardEvent) {
      if (event.key === "Escape") closeAll();
    }
    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [closeAll]);

  return (
    <header ref={headerRef} className="hs-header" data-scrolled={scrolled || undefined}>
      <div className="hs-header-inner">
        <a href="#top" className="hs-brand" aria-label="Healthspan Network home">
          <Image
            src="/brand/logo.png"
            alt="Healthspan Network"
            width={1112}
            height={385}
            priority
            sizes="(min-width: 640px) 168px, 132px"
            className="hs-brand-logo"
          />
        </a>

        <nav ref={navRef} className="hs-nav" aria-label="Primary navigation">
          {groups.map((group, index) => {
            const open = openGroup === index;
            return (
              <div
                key={group.label}
                className="hs-nav-group"
                onPointerEnter={(event) => event.pointerType === "mouse" && setOpenGroup(index)}
                onPointerLeave={(event) => event.pointerType === "mouse" && setOpenGroup(null)}
                onBlur={(event) => {
                  if (!event.currentTarget.contains(event.relatedTarget)) {
                    setOpenGroup((current) => (current === index ? null : current));
                  }
                }}
              >
                <button
                  type="button"
                  className="hs-nav-trigger"
                  aria-expanded={open}
                  aria-controls={`hs-menu-${index}`}
                  onClick={() => setOpenGroup(open ? null : index)}
                >
                  {group.label}
                  <ChevronDown aria-hidden="true" className="hs-chevron" />
                </button>
                <ul id={`hs-menu-${index}`} className="hs-menu" data-open={open || undefined}>
                  {group.items.map((item) => (
                    <li key={item.label}>
                      <a href={item.href} onClick={closeAll} tabIndex={open ? 0 : -1}>
                        <span>{item.label}</span>
                        {item.hint && <small>{item.hint}</small>}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </nav>

        <div className="hs-header-actions">
          <a href={searchHref} className="hs-icon-btn" aria-label="Browse discussions">
            <Search aria-hidden="true" />
          </a>
          {themeToggle}
          <a href={loginHref} className="hs-btn hs-btn--ghost hs-hide-sm">
            Log in
          </a>
          <a href={joinHref} className="hs-btn hs-btn--green hs-hide-sm">
            Join the Network <ArrowRight aria-hidden="true" />
          </a>
          <button
            type="button"
            className="hs-icon-btn hs-burger"
            aria-label={mobileOpen ? "Close menu" : "Open menu"}
            aria-expanded={mobileOpen}
            aria-controls="hs-mobile-panel"
            onClick={() => setMobileOpen((value) => !value)}
          >
            {mobileOpen ? <X aria-hidden="true" /> : <Menu aria-hidden="true" />}
          </button>
        </div>
      </div>

      <div id="hs-mobile-panel" className="hs-mobile" data-open={mobileOpen || undefined}>
        <div className="hs-mobile-scroll">
          {groups.map((group) => (
            <section key={group.label} className="hs-mobile-group">
              <h2>{group.label}</h2>
              <ul>
                {group.items.map((item) => (
                  <li key={item.label}>
                    <a href={item.href} onClick={closeAll} tabIndex={mobileOpen ? 0 : -1}>
                      {item.label}
                    </a>
                  </li>
                ))}
              </ul>
            </section>
          ))}
          <div className="hs-mobile-cta">
            <a href={loginHref} className="hs-btn hs-btn--outline" onClick={closeAll}>
              Log in
            </a>
            <a href={joinHref} className="hs-btn hs-btn--green" onClick={closeAll}>
              Join the Network <ArrowRight aria-hidden="true" />
            </a>
          </div>
        </div>
      </div>
    </header>
  );
}
