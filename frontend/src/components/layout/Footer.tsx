import { Link } from "react-router-dom";
import { Instagram } from "lucide-react";
import { Button } from "@/components/ui/Button";
import logo from "@/assets/logo/aura-nails-logo.png";
import { siteConfig } from "@/data/siteConfig";
import { navLinks } from "@/components/layout/Header";

export function Footer() {
  const exploreLinks = [...navLinks, { label: "Booking", to: "/booking" }];

  return (
    <footer className="border-t border-border bg-primary text-primary-foreground">
      <div className="section-shell grid gap-12 py-16 md:grid-cols-[1.2fr_1fr_1fr]">
        <div>
          <img
            src={logo}
            alt="Aura Nails by Khushi"
            className="size-24 rounded-full object-cover"
          />
          <p className="mt-5 font-display text-2xl leading-snug">
            Elevate your nails,
            <br />
            Elevate your aura.
          </p>
        </div>

        <div>
          <p className="mb-4 text-xs font-bold uppercase tracking-[.18em]">
            Explore
          </p>
          <nav className="grid grid-cols-2 gap-3 text-sm text-primary-foreground/75">
            {exploreLinks.map(({ label, to }) => (
              <Link
                key={to}
                to={to}
                className="transition-colors hover:text-primary-foreground"
              >
                {label}
              </Link>
            ))}
          </nav>
        </div>

        <div>
          <p className="font-display text-3xl">Ready for your next set?</p>
          <Button asChild variant="blush" className="mt-5">
            <Link to="/booking">Book Appointment</Link>
          </Button>
          <a
            href={siteConfig.instagramUrl}
            target="_blank"
            rel="noreferrer"
            className="mt-6 flex items-center gap-2 text-sm text-primary-foreground/90 transition-colors hover:text-primary-foreground"
          >
            <Instagram className="size-4" />
            {siteConfig.instagram}
          </a>
        </div>
      </div>

      <div className="border-t border-primary-foreground/15 py-5 text-center text-xs text-primary-foreground/60">
        © 2026 Aura Nails by Khushi. All rights reserved.
      </div>
    </footer>
  );
}
