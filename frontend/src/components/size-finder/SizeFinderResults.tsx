import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Clipboard, Download, Check, Loader2, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { downloadSizeCardPdf, generateClipboardSizeText } from "@/services/sizeFinderService";
import type { NailSizeResult } from "@/types";

export interface SizeFinderResultsProps {
  results: NailSizeResult;
  onReset: () => void;
}

export function SizeFinderResults({ results, onReset }: SizeFinderResultsProps) {
  const navigate = useNavigate();
  const [copied, setCopied] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const handleCopy = async () => {
    const textToCopy = generateClipboardSizeText(results);
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(textToCopy);
      } else {
        const textArea = document.createElement("textarea");
        textArea.value = textToCopy;
        textArea.style.position = "fixed";
        textArea.style.left = "-9999px";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand("copy");
        document.body.removeChild(textArea);
      }
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  const handleDownload = async () => {
    try {
      setDownloading(true);
      await downloadSizeCardPdf(results);
    } catch (err) {
      console.error("Failed to generate and download PDF size card:", err);
    } finally {
      setDownloading(false);
    }
  };

  const handleBookAppointment = () => {
    try {
      sessionStorage.setItem("aura_active_ai_booking", JSON.stringify(results));
    } catch {
      // ignore storage error
    }
    navigate("/booking", {
      state: {
        source: "ai",
        sizeResult: results,
      },
    });
  };

  const fingerItems = results.measurements || results.leftHand || [];

  return (
    <div>
      <div className="text-center">
        <span className="inline-block rounded-full bg-blush px-4 py-2 text-xs font-bold uppercase tracking-[.16em] text-foreground">
          {results.isDemo ? "Demo results · not a measurement" : "AI Verified Measurements"}
        </span>
        <h2 className="mt-7 font-display text-5xl sm:text-6xl">
          Your Recommended Nail Sizes
        </h2>
        <p className="mt-4 text-muted-foreground">
          Precision calibrated with your physical ₹10 reference coin. Use these custom sizes for your press-on order.
        </p>
      </div>

      <div className="mt-10 grid gap-6 lg:grid-cols-2">
        {/* Computer Vision Detection Image */}
        {results.processed_image_url ? (
          <section className="bg-card p-6 shadow-soft">
            <div className="flex items-center justify-between gap-2">
              <div>
                <h3 className="font-display text-3xl">AI Detection View</h3>
                <p className="mt-1 text-xs text-muted-foreground">
                  ₹10 coin scale verification and segmented nail boundaries
                </p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={onReset}
                className="gap-1.5 text-xs shrink-0"
              >
                <RotateCcw className="size-3.5" />
                Retake
              </Button>
            </div>
            <div className="mt-4 flex min-h-72 items-center justify-center overflow-hidden rounded-md bg-lavender/20 p-2">
              <img
                src={results.processed_image_url}
                alt="AI Computer Vision Processed Hand"
                className="max-h-80 w-auto rounded object-contain shadow-sm"
              />
            </div>
            <div className="mt-4 flex flex-wrap items-center justify-center gap-4 text-xs text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <span className="inline-block size-3 rounded-full bg-blue-600"></span>
                ₹10 Reference Coin
              </span>
              <span className="flex items-center gap-1.5">
                <span className="inline-block size-3 rounded-full bg-green-500"></span>
                Green Nail Outlines
              </span>
              <span className="flex items-center gap-1.5">
                <span className="inline-block size-3 rounded-full bg-red-600"></span>
                Measurements
              </span>
            </div>
          </section>
        ) : null}

        {/* Verified Finger Measurements */}
        <section className="bg-card p-6 shadow-soft">
          <h3 className="font-display text-3xl">Hand Measurements</h3>
          <p className="mt-1 text-xs text-muted-foreground">
            Precision width and height calibrated in millimeters
          </p>
          <div className="mt-4 divide-y divide-border">
            {fingerItems.map((item) => {
              const isOutOfRange =
                item.recommended_size === "Outside supported size range" ||
                item.size === "Outside supported size range";
              const displaySize =
                item.recommended_size ||
                (item.size && !isNaN(Number(item.size)) ? `Size ${item.size}` : item.size || "Unknown");

              return (
                <div
                  key={item.finger}
                  className="grid grid-cols-[1.4fr_auto_auto] items-center gap-4 py-3.5"
                >
                  <div>
                    <span className="font-medium text-foreground block">{item.finger}</span>
                    {typeof item.width_mm === "number" && typeof item.height_mm === "number" && (
                      <div className="mt-0.5 space-y-0.5 text-xs text-muted-foreground">
                        <div>
                          {item.width_mm.toFixed(2)} mm × {item.height_mm.toFixed(2)} mm
                        </div>
                        <div className="text-[11px] opacity-75 font-mono">
                          Raw: {typeof item.raw_width === "number" ? `${item.raw_width.toFixed(0)} px` : "—"} → Calibrated: {item.width_mm.toFixed(2)} mm → Mapped: {displaySize}
                        </div>
                      </div>
                    )}
                  </div>
                  <div className="text-right">
                    {isOutOfRange ? (
                      <span className="inline-block rounded-md border border-amber-300 bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-800">
                        Outside supported size range
                      </span>
                    ) : (
                      <b className="font-display text-2xl text-foreground">
                        {displaySize}
                      </b>
                    )}
                  </div>
                  {isOutOfRange ? (
                    <span className="rounded-full bg-amber-100 px-3 py-1 text-[10px] font-bold uppercase text-amber-800">
                      Custom Sizing
                    </span>
                  ) : (
                    <span className="rounded-full bg-mint px-3 py-1 text-[10px] font-bold uppercase text-foreground">
                      AI Fit
                    </span>
                  )}
                </div>
              );
            })}
          </div>
        </section>
      </div>

      {/* Summary Profile & Actions */}
      <div className="mt-8 bg-lavender/25 p-7">
        <h3 className="font-display text-3xl">Your Aura Nails Size Profile</h3>
        <p className="mt-3 break-words font-mono text-sm text-foreground">
          {results.summaryProfile}
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Button variant="outline" onClick={handleCopy}>
            {copied ? <Check className="size-4 text-emerald-600" /> : <Clipboard className="size-4" />}
            {copied ? "Sizes copied!" : "Copy My Sizes"}
          </Button>
          <Button variant="outline" onClick={handleDownload} disabled={downloading}>
            {downloading ? <Loader2 className="size-4 animate-spin" /> : <Download className="size-4" />}
            {downloading ? "Generating PDF..." : "Download Size Card"}
          </Button>
          <Button variant="outline" onClick={onReset}>
            <RotateCcw className="size-4" />
            Retake
          </Button>
          <Button asChild>
            <Link to="/gallery">Shop Custom Press-Ons</Link>
          </Button>
          <Button variant="outline" onClick={handleBookAppointment}>
            Book Appointment
          </Button>
        </div>
      </div>

      {copied && (
        <div
          role="status"
          aria-live="polite"
          className="fixed bottom-6 right-6 z-50 flex items-center gap-2.5 rounded-full bg-foreground px-5 py-3 text-sm font-medium text-background shadow-2xl"
        >
          <Check className="size-4 text-emerald-400" />
          <span>Sizes copied!</span>
        </div>
      )}

      <button
        type="button"
        className="mx-auto mt-8 block cursor-pointer text-sm text-muted-foreground underline transition-colors hover:text-foreground"
        onClick={onReset}
      >
        Try another photo
      </button>
    </div>
  );
}
