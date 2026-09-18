import { useEffect, useRef, useState } from "react";
import { Camera, Upload } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { PhotoGuidance } from "@/components/size-finder/PhotoGuidance";
import exampleHandImage from "@/assets/images/size-finder-example.jpg";

export interface SizeFinderUploadProps {
  file: File | null;
  preview: string;
  error: string;
  onFileSelect: (file?: File) => void;
  onAnalyze: () => void;
  onError?: (message: string) => void;
}

function normalizeCapturedFile(file: File): File {
  if (file.name && file.name.includes(".")) {
    return file;
  }
  const ext = file.type === "image/png" ? ".png" : file.type === "image/webp" ? ".webp" : ".jpg";
  const name = (file.name || "captured_photo") + ext;
  return new File([file], name, {
    type: file.type || "image/jpeg",
    lastModified: file.lastModified || Date.now(),
  });
}

export function SizeFinderUpload({
  file,
  preview,
  error,
  onFileSelect,
  onAnalyze,
  onError,
}: SizeFinderUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);
  const [cameraPermissionState, setCameraPermissionState] = useState<
    "granted" | "denied" | "prompt" | "unknown"
  >("unknown");

  useEffect(() => {
    let isMounted = true;
    if (typeof navigator !== "undefined" && navigator.permissions?.query) {
      try {
        navigator.permissions
          .query({ name: "camera" as PermissionName })
          .then((status) => {
            if (!isMounted) return;
            setCameraPermissionState(status.state);
            status.onchange = () => {
              if (isMounted) setCameraPermissionState(status.state);
            };
          })
          .catch(() => {
            // Not supported on all browsers (e.g. Safari), proceed gracefully
          });
      } catch {
        // Ignore
      }
    }
    return () => {
      isMounted = false;
    };
  }, []);

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(normalizeCapturedFile(e.dataTransfer.files[0]));
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const handleBrowseImages = () => {
    onError?.("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
      fileInputRef.current.click();
    }
  };

  const handleTakePhoto = () => {
    onError?.("");

    if (cameraPermissionState === "denied") {
      onError?.(
        "Camera access is blocked by your browser settings. Please allow camera permissions or use \"Browse Images\" instead."
      );
      return;
    }

    try {
      if (cameraInputRef.current) {
        cameraInputRef.current.value = "";
        cameraInputRef.current.click();
      }
    } catch {
      onError?.("Unable to open camera. Please use \"Browse Images\" instead.");
    }
  };

  return (
    <div className="grid gap-10 lg:grid-cols-[1.2fr_.8fr]">
      <div>
        <div
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          className="grid min-h-96 place-items-center border border-dashed border-lavender-deep bg-lavender/20 p-8 text-center"
        >
          {preview ? (
            <img
              src={preview}
              alt="Selected hand preview"
              className="max-h-80 w-full object-contain"
            />
          ) : (
            <div>
              <Upload className="mx-auto size-10 text-lavender-deep" />
              <h2 className="mt-5 font-display text-4xl">Upload your hand photo</h2>
              <p className="mt-3 text-sm text-muted-foreground">
                Place a physical ₹10 coin flat beside your hand under clear lighting.
                <br />
                JPG, JPEG, PNG or WEBP · Maximum 15 MB
              </p>
            </div>
          )}
        </div>

        {error && (
          <p role="alert" className="mt-3 text-sm text-destructive">
            {error}
          </p>
        )}

        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp"
          className="sr-only"
          tabIndex={-1}
          aria-hidden="true"
          onChange={(e) => {
            const selected = e.target.files?.[0];
            if (selected) {
              onFileSelect(normalizeCapturedFile(selected));
            }
            e.target.value = "";
          }}
        />
        <input
          ref={cameraInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          className="sr-only"
          tabIndex={-1}
          aria-hidden="true"
          onChange={(e) => {
            const selected = e.target.files?.[0];
            if (selected) {
              onFileSelect(normalizeCapturedFile(selected));
            }
            e.target.value = "";
          }}
        />

        <div className="mt-5 flex flex-wrap gap-3">
          <Button
            type="button"
            variant="outline"
            onClick={handleBrowseImages}
          >
            <Upload className="size-4" />
            Browse Images
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={handleTakePhoto}
          >
            <Camera className="size-4" />
            Take Photo
          </Button>
          {file && (
            <Button onClick={onAnalyze}>
              Analyze Nail Sizes
            </Button>
          )}
        </div>

        {/* Example / Demo Photo Card */}
        <div className="mt-8 rounded-2xl border border-border/80 bg-card p-5 sm:p-6 shadow-soft">
          <div className="flex items-center justify-between gap-3 mb-3">
            <span className="text-xs font-bold uppercase tracking-[.18em] text-lavender-deep">
              Example Photo
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-full bg-blue-50 px-2.5 py-1 text-[11px] font-semibold text-blue-700 ring-1 ring-blue-600/20">
              <span className="size-2 rounded-full bg-blue-600 animate-pulse" />
              ₹10 Reference Coin
            </span>
          </div>

          <div className="relative mx-auto overflow-hidden rounded-xl bg-muted/40 aspect-[4/3] max-w-lg shadow-sm">
            <img
              src={exampleHandImage}
              alt="Example hand photo with ₹10 reference coin"
              className="h-full w-full object-contain"
              loading="lazy"
            />

            {/* Subtle visual indication / highlight around the ₹10 coin */}
            <div
              className="absolute rounded-full border-2 border-blue-600 bg-blue-500/15 shadow-[0_0_14px_rgba(37,99,235,0.45)] pointer-events-none"
              style={{
                left: "70.6%",
                top: "44.9%",
                width: "14.5%",
                aspectRatio: "1 / 1",
                transform: "translate(-50%, -50%)",
              }}
              aria-label="₹10 calibration coin highlight"
            >
              <span className="absolute -inset-1 rounded-full border border-blue-400/50 animate-ping opacity-40" />
              <span className="absolute -top-7 left-1/2 -translate-x-1/2 whitespace-nowrap rounded-full bg-foreground/90 px-2.5 py-0.5 text-[10px] font-medium text-background shadow-md backdrop-blur-xs">
                ₹10 Reference Coin
              </span>
            </div>
          </div>

          <p className="mt-4 text-center text-xs sm:text-sm text-muted-foreground leading-relaxed">
            This is the type of photo you should upload — keep the ₹10 coin flat beside your hand for accurate measurement.
          </p>
        </div>
      </div>

      <PhotoGuidance />
    </div>
  );
}

