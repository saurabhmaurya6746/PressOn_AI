# Aura Nails Studio by Khushi

Official website for **AURA NAILS by Khushi** — Luxury nail atelier offering nail extensions, handmade custom press-ons, and personalized nail art.

> **Tagline**: Elevate your nails, Elevate your aura.  
> **Instagram**: [@auranailsbykhushi](https://www.instagram.com/auranailsbykhushi)

## Features

- **Luxury Brand Experience**: Handcrafted editorial design, typography (Cormorant Garamond & Manrope), and soft luxury pastel palette (lavender, blush, mint, ivory, gold).
- **Interactive Routes**:
  - `/` — Home (Hero, Atelier story, Services preview, Featured press-ons, AI Size Finder banner, Why Aura Nails, Studio notes)
  - `/about` — Meet Khushi (Founder story & 4-pillar philosophy)
  - `/services` — Comprehensive services menu & consultation details
  - `/gallery` — Filterable portfolio with high-resolution lightbox modal
  - `/ai-nail-size-finder` — Guided photo sizing flow (Upload → Analyzing → 10-Finger Results & SVG card download)
  - `/faq` — Accessible accordion covering orders, care, sizing & appointments
  - `/contact` — Direct channels and contact message form
  - `/booking` — Multi-field appointment request form with validation & confirmation
- **AI Nail Size Finder Demo**: Simulated computer-vision sizing workflow with photo guidance and downloadable size card profile.
- **Accessible & Responsive**: Fully responsive layout with mobile slide-in drawer navigation and body scroll locking.

## Tech Stack

- **React 19**
- **TypeScript**
- **Vite**
- **Tailwind CSS v4** (OKLCH color system)
- **React Router**
- **Radix UI** primitives (`@radix-ui/react-accordion`, `@radix-ui/react-dialog`, `@radix-ui/react-slot`)
- **Lucide Icons**

## Getting Started

### Prerequisites

- Node.js (v18 or higher recommended)
- npm

### Installation

```sh
npm install
```

### Development Server

```sh
npm run dev
```

Visit `http://localhost:3000` in your browser.

### Production Build

```sh
npm run build
```

The output static files will be generated in `dist/`.

### Preview Production Build

```sh
npm run preview
```
