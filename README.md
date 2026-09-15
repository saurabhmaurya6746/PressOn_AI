# PressOn AI 💅✨

PressOn AI is an end-to-end computer vision nail sizing, analysis, and custom press-on booking platform. It features deep-learning hand segmentation, metric calibration against a physical ₹10 reference coin, real-time millimeter nail sizing recommendations, and a luxury salon frontend for ordering and appointment booking.

---

## 🏗️ Architecture

The repository is organized into two primary components:

- **[`Backend/`](./Backend)**: Django REST-based AI computer vision inference backend powered by YOLOv11 segmentation, OpenCV Hough Circle detection with ₹10 coin diameter verification (27.0 mm), and MediaPipe Hand Landmarking.
- **[`frontend/`](./frontend)**: Modern React 19 + Vite + TypeScript web application for Aura Nails Studio, featuring interactive image upload, AI analyzing screen, dynamic sizing cards, PDF generation, and context-aware booking.

---

## 🚀 Quick Start

### 1. Backend Setup (Django & AI Pipeline)

```bash
cd Backend

# Create & activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start the Django server
python manage.py runserver 127.0.0.1:8000
```

The AI analysis API will be available at:
`POST http://127.0.0.1:8000/api/analyze/`

### 2. Frontend Setup (Aura Nails Studio)

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Ensure VITE_PRESSON_AI_API_URL=http://127.0.0.1:8000

# Start development server
npm run dev

# Or create production build
npm run build
```

The frontend application will run at:
`http://localhost:5173/`

---

## 🌟 Key Features

- **₹10 Coin Reference Metric Calibration**: Detects and verifies the 27.0 mm physical reference coin with Hough Circle transforms and color verification to establish a sub-millimeter pixel-to-metric ratio.
- **YOLO Nail Segmentation**: Fine-tuned YOLOv11 segmentation model (`ai/weights/best.pt`) detecting finger contours with sub-pixel precision.
- **Hand Landmarker & Finger Identification**: MediaPipe Hand Landmarks detecting thumb, index, middle, ring, and pinky nails.
- **AI Size Recommender**: Maps millimeter nail bed dimensions directly to standard press-on tip curves (Size 0 – Size 12).
- **Client-Side PDF Size Card**: Generates print-ready `aura-nails-size-card.pdf` with detected sizes, mm dimensions, and embedded computer vision detection view.
- **Context-Aware Booking**: Connects AI sizing directly to salon appointment requests while supporting manual size entries.
