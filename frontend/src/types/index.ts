export interface SiteConfig {
  brandName: string;
  brandSubtitle: string;
  founder: string;
  instagram: string;
  instagramUrl: string;
  whatsappUrl: string;
  whatsappDisplay: string;
  email: string;
  emailDisplay: string;
  tagline: string;
}

export interface ServiceItem {
  id?: string;
  title: string;
  category: string;
  description: string;
  image: string;
  priceNote?: string;
  durationNote?: string;
}

export interface GalleryItem {
  id?: string;
  name: string;
  category: "Extensions" | "Press-On" | "Nail Art" | "Bridal" | "Minimal" | "Statement";
  image: string;
  description: string;
}

export interface FaqItem {
  question: string;
  answer: string;
}

export interface FingerSize {
  finger: string;
  size: number | string;
  recommended_size?: string;
  confidence?: number;
  width_mm?: number;
  height_mm?: number;
  raw_width?: number;
  raw_height?: number;
}

export interface PressOnMeasurement {
  finger: string;
  recommended_size: string;
  width_mm: number;
  height_mm: number;
  raw_width: number;
  raw_height: number;
}

export interface PressOnApiResponse {
  success: boolean;
  coin_detected: boolean;
  landmark_count?: number;
  processed_image_url?: string;
  measurements?: PressOnMeasurement[];
  error?: string;
}

export interface NailSizeResult {
  isDemo: boolean;
  leftHand: FingerSize[];
  rightHand: FingerSize[];
  measurements?: FingerSize[];
  summaryProfile: string;
  processed_image_url?: string;
  coin_detected?: boolean;
  landmark_count?: number;
}

export interface StructuredNailSizes {
  thumb?: string;
  index: string;
  middle: string;
  ring: string;
  pinky: string;
}

export interface BookingNailSizeProfile {
  source: "ai" | "manual";
  sizes: StructuredNailSizes;
  measurements?: FingerSize[];
  summary?: string;
}

export interface BookingFormData {
  name: string;
  phone: string;
  email: string;
  service: string;
  preferredDate: string;
  preferredTime: string;
  nailSizeProfile: BookingNailSizeProfile;
  designPreference: string;
  additionalNotes?: string;
  aiSizeProfile?: string;
  aiMeasurements?: FingerSize[];
}

export interface ContactFormData {
  name: string;
  email: string;
  phone: string;
  message: string;
}
