import { useEffect, useState } from "react";

const ROTATING_MESSAGES = [
  {
    title: "Preparing your image...",
    detail: "Standardizing resolution and color space for detection",
  },
  {
    title: "Verifying the ₹10 reference coin...",
    detail: "Calibrating 27.0 mm diameter pixel-to-metric ratio",
  },
  {
    title: "Detecting nail contours...",
    detail: "Segmenting individual nail bed boundaries",
  },
  {
    title: "Measuring nail dimensions...",
    detail: "Calculating precision millimeter width and length per finger",
  },
  {
    title: "Calculating your best fit...",
    detail: "Matching contour dimensions with press-on sizing standards",
  },
  {
    title: "Preparing your personalized size profile...",
    detail: "Finalizing custom Aura Nails fit recommendations",
  },
];

export function SizeFinderAnalyzing() {
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % ROTATING_MESSAGES.length);
    }, 1800);
    return () => clearInterval(timer);
  }, []);

  const currentMsg = ROTATING_MESSAGES[currentIndex];

  return (
    <div className="grid min-h-[540px] place-items-center rounded-xl bg-lavender/25 p-8 text-center sm:p-12">
      <div className="mx-auto flex max-w-lg flex-col items-center">
        {/* Luxury AI Scanning Ring with Glow */}
        <div className="relative flex size-36 items-center justify-center">
          {/* Soft pulsing ambient halo */}
          <div
            className="absolute -inset-2 rounded-full bg-lavender/40 blur-xl animate-pulse motion-reduce:hidden"
            aria-hidden="true"
          />

          {/* Outer rotating dashed ring */}
          <svg
            className="absolute inset-0 size-full animate-spin [animation-duration:10s] motion-reduce:hidden"
            viewBox="0 0 100 100"
            fill="none"
            aria-hidden="true"
          >
            <circle
              cx="50"
              cy="50"
              r="46"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeDasharray="6 8"
              className="text-lavender-deep/60"
            />
          </svg>

          {/* Inner counter-rotating ring with orbital bead */}
          <svg
            className="absolute inset-2 size-[calc(100%-16px)] animate-spin [animation-duration:14s] [animation-direction:reverse] motion-reduce:hidden"
            viewBox="0 0 100 100"
            fill="none"
            aria-hidden="true"
          >
            <circle
              cx="50"
              cy="50"
              r="44"
              stroke="currentColor"
              strokeWidth="1"
              strokeDasharray="2 12"
              className="text-primary/40"
            />
            <circle cx="50" cy="6" r="3.5" className="fill-primary" />
          </svg>

          {/* Center Brand Orb */}
          <div className="relative flex size-24 items-center justify-center overflow-hidden rounded-full border border-lavender-deep/40 bg-card shadow-soft">
            <span className="font-display text-4xl font-semibold tracking-wider text-foreground select-none">
              AI
            </span>

            {/* Scanning Light Beam (moves across the center) */}
            <div
              className="pointer-events-none absolute inset-0 overflow-hidden motion-reduce:hidden"
              aria-hidden="true"
            >
              <div className="h-0.5 w-full bg-gradient-to-r from-transparent via-primary to-transparent opacity-80 shadow-xs animate-[bounce_2.4s_ease-in-out_infinite]" />
            </div>
          </div>
        </div>

        {/* Rotating Status Messages with aria-live for accessibility */}
        <div
          aria-live="polite"
          aria-atomic="true"
          className="mt-8 min-h-[96px] transition-all duration-300"
        >
          <h2
            key={currentMsg.title}
            className="font-display text-3xl text-foreground sm:text-4xl animate-in fade-in slide-in-from-bottom-2 duration-300"
          >
            {currentMsg.title}
          </h2>
          <p
            key={currentMsg.detail}
            className="mt-2 text-sm text-muted-foreground animate-in fade-in duration-300"
          >
            {currentMsg.detail}
          </p>
        </div>

        {/* Subtle Animated Progress Shimmer */}
        <div className="mt-5 w-48 overflow-hidden rounded-full bg-lavender/40 p-0.5" aria-hidden="true">
          <div className="h-1 w-20 rounded-full bg-gradient-to-r from-transparent via-primary to-transparent animate-[shimmer_2s_ease-in-out_infinite] motion-reduce:w-full motion-reduce:bg-primary/50" />
        </div>

        {/* Rotating Indicator Dots */}
        <div className="mt-4 flex items-center justify-center gap-1.5" aria-hidden="true">
          {ROTATING_MESSAGES.map((_, i) => (
            <span
              key={i}
              className={`h-1.5 rounded-full transition-all duration-300 ${
                i === currentIndex
                  ? "w-5 bg-primary"
                  : "w-1.5 bg-border/80"
              }`}
            />
          ))}
        </div>

        {/* Section Badge */}
        <span className="mt-7 inline-block rounded-full bg-card/80 px-4 py-1.5 text-[11px] font-bold uppercase tracking-[.18em] text-lavender-deep shadow-xs border border-border/50">
          AI Computer Vision Analysis
        </span>
      </div>
    </div>
  );
}
