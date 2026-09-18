import { useEffect, useState } from "react";
import { PageIntro } from "@/components/ui/PageIntro";
import { SectionHeading } from "@/components/ui/SectionHeading";
import { FaqAccordion } from "@/components/faq/FaqAccordion";
import { SizeFinderUpload } from "@/components/size-finder/SizeFinderUpload";
import { SizeFinderAnalyzing } from "@/components/size-finder/SizeFinderAnalyzing";
import { SizeFinderResults } from "@/components/size-finder/SizeFinderResults";
import { SEO } from "@/components/common/SEO";
import { sizeFinderFaqs } from "@/data/faq";
import {
  analyzeNailImage,
  validateNailPhoto,
} from "@/services/sizeFinderService";
import type { NailSizeResult } from "@/types";

export function AISizeFinder() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>("");
  const [stage, setStage] = useState<"upload" | "analyzing" | "results">("upload");
  const [error, setError] = useState<string>("");
  const [results, setResults] = useState<NailSizeResult | null>(null);

  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview);
    };
  }, [preview]);

  const handleFileSelect = (selectedFile?: File) => {
    setError("");
    if (!selectedFile) return;

    const validation = validateNailPhoto(selectedFile);
    if (!validation.isValid) {
      setError(validation.error || "Invalid file.");
      return;
    }

    if (preview) URL.revokeObjectURL(preview);
    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
  };

  const handleAnalyze = async () => {
    if (!file) return;

    setError("");
    setStage("analyzing");

    try {
      const data = await analyzeNailImage(file);
      setResults(data);
      setStage("results");
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Failed to analyze photo.";
      setError(message);
      setStage("upload");
    }
  };

  const handleReset = () => {
    if (preview) URL.revokeObjectURL(preview);
    setFile(null);
    setPreview("");
    setError("");
    setResults(null);
    setStage("upload");
  };

  return (
    <>
      <SEO
        title="AI Nail Size Finder"
        description="Upload a hand photo with a ₹10 reference coin and get precision AI recommended sizes for custom press-on nails."
      />

      <PageIntro
        eyebrow="AI size finder"
        title="Find Your Perfect Press-On Nail Size"
      >
        Upload a clear photo of your hand with a ₹10 coin and get your precision
        recommended nail sizes in seconds.
      </PageIntro>

      <section className="section-shell py-20">
        <div className="mx-auto max-w-5xl">
          {stage === "upload" && (
            <SizeFinderUpload
              file={file}
              preview={preview}
              error={error}
              onFileSelect={handleFileSelect}
              onAnalyze={handleAnalyze}
              onError={setError}
            />
          )}

          {stage === "analyzing" && <SizeFinderAnalyzing />}

          {stage === "results" && results && (
            <SizeFinderResults results={results} onReset={handleReset} />
          )}
        </div>
      </section>

      {/* Size Finder FAQ Section */}
      <section className="bg-blush/20 py-20">
        <div className="section-shell">
          <SectionHeading
            centered
            eyebrow="Size finder FAQ"
            title="Before You Measure"
          />
          <div className="mt-10">
            <FaqAccordion items={sizeFinderFaqs} />
          </div>
        </div>
      </section>
    </>
  );
}
