import { Check, X } from "lucide-react";

export function PhotoGuidance() {
  const dos = [
    "Place a physical ₹10 coin flat beside your hand",
    "Palm facing down",
    "Fingers naturally separated",
    "Good lighting",
    "Entire hand visible",
    "Camera directly above hand",
  ];

  const donts = [
    "Blurry images",
    "Cropped fingers",
    "Very dark photos",
    "Extreme angles",
  ];

  return (
    <aside className="bg-card p-7 shadow-soft">
      <h2 className="font-display text-3xl">Photo guidance</h2>

      <p className="mt-6 text-xs font-bold uppercase tracking-[.18em] text-lavender-deep">
        For the best view
      </p>
      <ul className="mt-3 space-y-3 text-sm">
        {dos.map((item) => (
          <li key={item} className="flex items-center gap-3">
            <Check className="size-4 shrink-0 text-lavender-deep" />
            <span>{item}</span>
          </li>
        ))}
      </ul>

      <p className="mt-8 text-xs font-bold uppercase tracking-[.18em] text-lavender-deep">
        Avoid
      </p>
      <ul className="mt-3 space-y-3 text-sm">
        {donts.map((item) => (
          <li key={item} className="flex items-center gap-3">
            <X className="size-4 shrink-0 text-destructive" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </aside>
  );
}
