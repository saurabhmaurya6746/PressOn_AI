import { Link, NavLink } from "react-router-dom";
import { Menu } from "lucide-react";
import { Button } from "@/components/ui/Button";
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/Sheet";
import logo from "@/assets/logo/aura-nails-logo.png";
import { cn } from "@/utils/cn";

export const navLinks = [
  { label: "Home", to: "/" },
  { label: "About", to: "/about" },
  { label: "Services", to: "/services" },
  { label: "Gallery", to: "/gallery" },
  { label: "AI Size Finder", to: "/ai-nail-size-finder" },
  { label: "FAQ", to: "/faq" },
  { label: "Contact", to: "/contact" },
] as const;

export function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <Link
      to="/"
      aria-label="Aura Nails home"
      className="flex shrink-0 items-center gap-3"
    >
      <img
        src={logo}
        alt="Aura Nails by Khushi"
        className={
          compact
            ? "size-11 rounded-full object-cover"
            : "size-14 rounded-full object-cover shadow-soft"
        }
      />
      <span className="hidden leading-none sm:block">
        <b className="font-display text-lg font-semibold tracking-wide">
          AURA NAILS
        </b>
        <small className="mt-1 block text-[10px] text-muted-foreground">
          by Khushi
        </small>
      </span>
    </Link>
  );
}

export function Header() {
  return (
    <header className="sticky top-0 z-40 border-b border-border/60 bg-background/90 backdrop-blur-xl">
      <div className="section-shell flex h-20 items-center justify-between gap-6">
        <Brand compact />

        <nav
          aria-label="Main navigation"
          className="hidden items-center gap-6 xl:flex"
        >
          {navLinks.map(({ label, to }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                cn(
                  "text-xs font-semibold transition-colors hover:text-primary",
                  isActive ? "text-primary" : "text-muted-foreground"
                )
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>

        <Button asChild className="hidden lg:inline-flex">
          <Link to="/booking">Book Appointment</Link>
        </Button>

        {/* Mobile Navigation Drawer */}
        <Sheet>
          <SheetTrigger asChild>
            <Button
              aria-label="Open navigation"
              variant="ghost"
              size="icon"
              className="xl:hidden"
            >
              <Menu className="h-6 w-6" />
            </Button>
          </SheetTrigger>
          <SheetContent
            side="right"
            className="w-[88vw] border-lavender bg-background p-8 sm:max-w-md"
          >
            <SheetTitle className="sr-only">Navigation</SheetTitle>
            <SheetDescription className="sr-only">
              Aura Nails site menu
            </SheetDescription>
            <Brand />
            <nav
              className="mt-12 flex flex-col"
              aria-label="Mobile navigation"
            >
              {navLinks.map(({ label, to }) => (
                <SheetClose asChild key={to}>
                  <Link
                    to={to}
                    className="border-b border-border py-4 font-display text-3xl transition-colors hover:text-lavender-deep"
                  >
                    {label}
                  </Link>
                </SheetClose>
              ))}
            </nav>
            <SheetClose asChild>
              <Button asChild size="lg" className="mt-8 w-full">
                <Link to="/booking">Book Appointment</Link>
              </Button>
            </SheetClose>
          </SheetContent>
        </Sheet>
      </div>
    </header>
  );
}
