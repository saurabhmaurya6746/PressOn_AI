import { useRef } from "react";
import { Camera, Upload } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { PhotoGuidance } from "@/components/size-finder/PhotoGuidance";

export interface SizeFinderUploadProps {
  file: File | null;
  preview: string;
  error: string;
  onFileSelect: (file?: File) => void;
  onAnalyze: () => void;
}

export function SizeFinderUpload({
  file,
  preview,
  error,
  onFileSelect,
  onAnalyze,
}: SizeFinderUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
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
          hidden
          type="file"
          accept="image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp"
          onChange={(e) => onFileSelect(e.target.files?.[0])}
        />
        <input
          ref={cameraInputRef}
          hidden
          type="file"
          accept="image/*"
          capture="environment"
          onChange={(e) => onFileSelect(e.target.files?.[0])}
        />

        <div className="mt-5 flex flex-wrap gap-3">
          <Button
            type="button"
            variant="outline"
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload className="size-4" />
            Browse Image
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => cameraInputRef.current?.click()}
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
      </div>

      <PhotoGuidance />
    </div>
  );
}
