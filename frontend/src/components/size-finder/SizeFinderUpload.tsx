import { useEffect, useRef, useState } from "react";
import { Camera, RefreshCw, Upload } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { PhotoGuidance } from "@/components/size-finder/PhotoGuidance";
import exampleHandImage from "@/assets/images/size-finder-example.png";

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
        'Camera access is blocked by your browser settings. Please allow camera permissions or use "Browse Images" instead.'
      );
      return;
    }

    try {
      if (cameraInputRef.current) {
        cameraInputRef.current.value = "";
        cameraInputRef.current.click();
      }
    } catch {
      onError?.('Unable to open camera. Please use "Browse Images" instead.');
    }
  };

  return (
    <div className="grid gap-10 lg:grid-cols-[1.2fr_.8fr]">
      <div>
        <div
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          className="relative rounded-3xl border-2 border-dashed border-lavender-deep/35 bg-card/60 p-6 sm:p-8 text-center shadow-soft transition-colors hover:border-lavender-deep/55"
        >
          {!preview ? (
            /* Initial State: No Image Selected — Example Guidance */
            <div className="flex flex-col items-center">
              <div className="flex size-12 items-center justify-center rounded-2xl bg-lavender/40 text-lavender-deep shadow-xs">
                <Upload className="size-6 text-lavender-deep" />
              </div>

              <h2 className="mt-4 font-display text-3xl sm:text-4xl font-medium tracking-tight text-foreground">
                Upload your hand photo
              </h2>

              <p className="mt-2 text-sm text-muted-foreground leading-relaxed max-w-md">
                Place a physical ₹10 coin flat beside your hand under clear lighting.
                <span className="mt-1 block text-xs text-muted-foreground/80">
                  JPG, JPEG, PNG or WEBP · Maximum 15 MB
                </span>
              </p>

              {/* Integrated Example Illustration as a subtle visual guide */}
              <div className="mt-6 w-full max-w-md overflow-hidden rounded-2xl border border-lavender-deep/20 bg-background/50 p-2 shadow-xs transition-transform hover:border-lavender-deep/40">
                <div className="relative overflow-hidden rounded-xl bg-muted/20">
                  <img
                    src={exampleHandImage}
                    alt="Visual guide: Hand placed flat with ₹10 coin reference"
                    className="h-auto max-h-56 sm:max-h-64 w-full object-contain"
                    loading="eager"
                  />
                </div>
              </div>

              {/* Primary Action Buttons */}
              <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleBrowseImages}
                  className="gap-2"
                >
                  <Upload className="size-4" />
                  Browse Images
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleTakePhoto}
                  className="gap-2"
                >
                  <Camera className="size-4" />
                  Take Photo
                </Button>
              </div>
            </div>
          ) : (
            /* Selected State: User's Actual Image Preview */
            <div className="flex flex-col">
              <div className="flex items-center justify-between gap-3 border-b border-border/70 pb-3 text-left">
                <div className="flex items-center gap-2">
                  <span className="size-2 rounded-full bg-emerald-500 animate-pulse" />
                  <span className="text-sm font-medium text-foreground">
                    Photo ready for analysis
                  </span>
                </div>
                <span className="max-w-[160px] sm:max-w-xs truncate text-xs text-muted-foreground">
                  {file?.name || "Uploaded photo"}
                </span>
              </div>

              <div className="mt-4 relative mx-auto w-full overflow-hidden rounded-2xl border border-border/80 bg-background/50 p-2 shadow-xs">
                <div className="flex items-center justify-center overflow-hidden rounded-xl bg-muted/30">
                  <img
                    src={preview}
                    alt="Selected hand preview"
                    className="max-h-80 sm:max-h-96 w-full object-contain rounded-lg"
                  />
                </div>
              </div>

              {/* Action Controls for Selected State */}
              <div className="mt-6 flex flex-wrap items-center justify-between gap-3 pt-2">
                <div className="flex flex-wrap gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={handleBrowseImages}
                    className="gap-1.5"
                  >
                    <RefreshCw className="size-3.5" />
                    Change Photo
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={handleTakePhoto}
                    className="gap-1.5"
                  >
                    <Camera className="size-3.5" />
                    Retake
                  </Button>
                </div>

                <Button
                  type="button"
                  onClick={onAnalyze}
                  className="gap-2 shadow-soft hover:shadow-md"
                >
                  Analyze Nail Sizes
                  <span aria-hidden="true">&rarr;</span>
                </Button>
              </div>
            </div>
          )}
        </div>

        {error && (
          <div
            role="alert"
            className="mt-4 flex items-center gap-2 rounded-xl border border-destructive/20 bg-destructive/10 p-3 text-sm text-destructive"
          >
            <span className="size-1.5 rounded-full bg-destructive shrink-0" />
            <span>{error}</span>
          </div>
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
      </div>

      <PhotoGuidance />
    </div>
  );
}
