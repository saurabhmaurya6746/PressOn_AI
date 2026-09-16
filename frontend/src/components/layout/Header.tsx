import { Link, useLocation } from "react-router-dom";
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

export function isLinkActive(linkTo: string, currentPath: string): boolean {
  if (linkTo === "/") {
    return currentPath === "/";
  }
  if (linkTo === "/ai-nail-size-finder" || linkTo === "/ai-size-finder") {
    return (
      currentPath === "/ai-nail-size-finder" ||
      currentPath === "/ai-size-finder" ||
      currentPath.startsWith("/ai-nail-size-finder/") ||
      currentPath.startsWith("/ai-size-finder/")
    );
  }
  return currentPath === linkTo || currentPath.startsWith(`${linkTo}/`);
}

export function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <Link
      to="/"
      aria-label="Aura Nails home"
      className="group flex shrink-0 items-center gap-3.5 transition-opacity hover:opacity-95"
    >
      <img
        src={logo}
        alt="Aura Nails by Khushi"
        className={
          compact
            ? "size-12 sm:size-13 rounded-full object-cover shadow-soft ring-1 ring-border/60 transition-transform duration-300 group-hover:scale-[1.02]"
            : "size-15 sm:size-16 rounded-full object-cover shadow-soft ring-1 ring-border/60"
        }
      />
      <span className="leading-tight block">
        <b className="font-display text-lg sm:text-xl md:text-2xl font-semibold tracking-wider text-foreground block">
          AURA NAILS
        </b>
        <small className="mt-0.5 block text-[10px] sm:text-[11px] font-medium tracking-[0.18em] text-muted-foreground uppercase">
          by Khushi
        </small>
      </span>
    </Link>
  );
}

export function Header() {
  const location = useLocation();

  return (
    <header className="sticky top-0 z-40 border-b border-border/60 bg-background/95 backdrop-blur-xl">
      <div className="mx-auto flex h-22 sm:h-24 w-full max-w-[92rem] items-center justify-between px-5 sm:px-8 lg:px-12 xl:px-16 gap-4 sm:gap-6">
        {/* Brand */}
        <div className="flex shrink-0 items-center">
          <Brand compact />
        </div>

        {/* Centered Desktop Navigation */}
        <nav
          aria-label="Main navigation"
          className="hidden items-center justify-center gap-5 lg:flex xl:gap-8 2xl:gap-9"
        >
          {navLinks.map(({ label, to }) => {
            const active = isLinkActive(to, location.pathname);
            return (
              <Link
                key={to}
                to={to}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "group relative py-2 text-[13.5px] xl:text-sm tracking-wide transition-colors duration-200",
                  active
                    ? "font-semibold text-foreground"
                    : "font-medium text-muted-foreground hover:text-foreground"
                )}
              >
                <span>{label}</span>
                {/* Subtle luxury active indicator */}
                <span
                  aria-hidden="true"
                  className={cn(
                    "absolute -bottom-1 left-0 right-0 h-[2px] rounded-full transition-all duration-300",
                    active
                      ? "bg-lavender-deep opacity-100 scale-x-100"
                      : "bg-lavender-deep/40 opacity-0 scale-x-50 group-hover:opacity-60 group-hover:scale-x-75"
                  )}
                />
              </Link>
            );
          })}
        </nav>

        {/* CTA & Mobile Menu Toggle */}
        <div className="flex items-center gap-3 sm:gap-4">
          <Button
            asChild
            className="hidden px-6 lg:px-7 py-2.5 h-11 text-sm font-semibold tracking-wide shadow-soft hover:shadow-luxe sm:inline-flex"
          >
            <Link to="/booking">Book Appointment</Link>
          </Button>

          {/* Mobile Navigation Drawer */}
          <Sheet>
            <SheetTrigger asChild>
              <Button
                aria-label="Open navigation"
                variant="ghost"
                size="icon"
                className="lg:hidden h-10 w-10 text-foreground hover:bg-accent/80"
              >
                <Menu className="h-6 w-6" />
              </Button>
            </SheetTrigger>
            <SheetContent
              side="right"
              className="w-[88vw] border-lavender bg-background p-6 sm:p-8 sm:max-w-md flex flex-col justify-between"
            >
              <div>
                <SheetTitle className="sr-only">Navigation</SheetTitle>
                <SheetDescription className="sr-only">
                  Aura Nails site menu
                </SheetDescription>
                <Brand />
                <nav
                  className="mt-10 flex flex-col"
                  aria-label="Mobile navigation"
                >
                  {navLinks.map(({ label, to }) => {
                    const active = isLinkActive(to, location.pathname);
                    return (
                      <SheetClose asChild key={to}>
                        <Link
                          to={to}
                          aria-current={active ? "page" : undefined}
                          className={cn(
                            "flex items-center justify-between border-b border-border/60 py-4 font-display text-2xl transition-colors duration-200 sm:text-3xl",
                            active
                              ? "font-semibold text-foreground"
                              : "text-muted-foreground hover:text-foreground"
                          )}
                        >
                          <span className="flex items-center gap-3">
                            {active && (
                              <span
                                aria-hidden="true"
                                className="size-2 rounded-full bg-lavender-deep"
                              />
                            )}
                            {label}
                          </span>
                          {active && (
                            <span className="text-[11px] font-sans font-medium uppercase tracking-[0.2em] text-lavender-deep">
                              Current
                            </span>
                          )}
                        </Link>
                      </SheetClose>
                    );
                  })}
                </nav>
              </div>
              <div className="pt-6 pb-2">
                <SheetClose asChild>
                  <Button
                    asChild
                    size="lg"
                    className="w-full text-base font-semibold tracking-wide shadow-soft hover:shadow-luxe"
                  >
                    <Link to="/booking">Book Appointment</Link>
                  </Button>
                </SheetClose>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
}
