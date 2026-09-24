# PressOn AI - REST API Documentation

This document describes the external REST API exposed by the PressOn AI Django backend for frontend integration (e.g. Aura Nails website).

---

## Endpoint Specification

### Analyze Hand Image
- **Endpoint URL:** `/api/analyze/`
- **HTTP Method:** `POST`
- **Content-Type:** `multipart/form-data`
- **Authentication:** None (Public API endpoint, CSRF-exempt)

---

## Request Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `image` | File (`multipart/form-data`) | **Yes** | The input photo containing a human hand and a reference ₹10 coin placed flat beside the hand. |

### Supported Image Formats
- **JPG / JPEG:** `image/jpeg`, `.jpg`, `.jpeg`
- **PNG:** `image/png`, `.png`
- **WEBP:** `image/webp`, `.webp`

### File Limits
- Maximum file size: **15 MB**
- Corrupted, truncated, or non-image files are rejected before passing to AI inference.

---

## Response Structure

### 1. Success Response (`200 OK`)
Returned when the image is valid, the ₹10 reference coin is verified, hand landmarks are detected, and nail sizing recommendations are calculated.

```json
{
  "success": true,
  "coin_detected": true,
  "landmark_count": 21,
  "processed_image_url": "http://127.0.0.1:8000/media/processed/processed_sample.png",
  "measurements": [
    {
      "finger": "Thumb",
      "recommended_size": "Outside supported size range",
      "width_mm": 6.68,
      "height_mm": 14.64,
      "raw_width": 47.0,
      "raw_height": 103.0
    },
    {
      "finger": "Index",
      "recommended_size": "Size 5",
      "width_mm": 12.22,
      "height_mm": 13.64,
      "raw_width": 86.0,
      "raw_height": 96.0
    },
    {
      "finger": "Middle",
      "recommended_size": "Size 5",
      "width_mm": 12.79,
      "height_mm": 13.93,
      "raw_width": 90.0,
      "raw_height": 98.0
    },
    {
      "finger": "Ring",
      "recommended_size": "Size 7",
      "width_mm": 10.94,
      "height_mm": 13.93,
      "raw_width": 77.0,
      "raw_height": 98.0
    },
    {
      "finger": "Pinky",
      "recommended_size": "Size 8",
      "width_mm": 9.38,
      "height_mm": 12.65,
      "raw_width": 66.0,
      "raw_height": 89.0
    }
  ]
}
```

### Recommended Nail Size Chart (Sizes 0 to 9)

The API automatically maps detected nail width (in mm) into standard press-on nail sizes:

| Nail Number / Size | Nominal Width | Calibrated Width Range |
|---|---|---|
| **Size 0** | 18 mm | $\ge 17.0\text{ mm}$ |
| **Size 1** | 16 mm | $15.5\text{ mm} \le \text{width} < 17.0\text{ mm}$ |
| **Size 2** | 15 mm | $14.5\text{ mm} \le \text{width} < 15.5\text{ mm}$ |
| **Size 3** | 14 mm | $13.5\text{ mm} \le \text{width} < 14.5\text{ mm}$ |
| **Size 4** | 13 mm | $12.5\text{ mm} \le \text{width} < 13.5\text{ mm}$ |
| **Size 5** | 12 mm | $11.5\text{ mm} \le \text{width} < 12.5\text{ mm}$ |
| **Size 6** | 11 mm | $10.5\text{ mm} \le \text{width} < 11.5\text{ mm}$ |
| **Size 7** | 10 mm | $9.5\text{ mm} \le \text{width} < 10.5\text{ mm}$ |
| **Size 8** | 9 mm | $8.5\text{ mm} \le \text{width} < 9.5\text{ mm}$ |
| **Size 9** | 8 mm | $7.5\text{ mm} \le \text{width} < 8.5\text{ mm}$ |
| **Outside supported size range** | N/A | $< 7.5\text{ mm}$ |

### 2. Error Responses

#### `400 Bad Request`
Returned when the request is malformed, the `image` field is missing, the file is too large (>15MB), or the file format/bytes are invalid.

- **Missing image field:**
```json
{
  "success": false,
  "coin_detected": false,
  "error": "Please provide an image file in the 'image' field."
}
```

- **Unsupported file format:**
```json
{
  "success": false,
  "coin_detected": false,
  "error": "Unsupported image format. Please upload a JPG, JPEG, PNG, or WEBP image."
}
```

- **File exceeding size limit:**
```json
{
  "success": false,
  "coin_detected": false,
  "error": "Image is too large. Please upload a smaller image."
}
```

- **Corrupted / unreadable image:**
```json
{
  "success": false,
  "coin_detected": false,
  "error": "Unable to read this image. Please upload a valid JPG, PNG, or WEBP image."
}
```

#### `422 Unprocessable Entity`
Returned when the uploaded image is valid, but required computer vision references cannot be verified.

- **Reference ₹10 coin missing or not verified:**
```json
{
  "success": false,
  "coin_detected": false,
  "error": "Please upload an image with a clearly visible verified ₹10 coin."
}
```

- **Hand / fingers not detectable:**
```json
{
  "success": false,
  "coin_detected": true,
  "error": "No hand or fingers could be detected in the image. Please retake the photo with your hand clearly visible."
}
```

#### `500 Internal Server Error`
Returned only upon an unexpected internal server exception.
```json
{
  "success": false,
  "coin_detected": false,
  "error": "An error occurred while processing the image. Please try again."
}
```

---

## CORS Configuration

Cross-Origin Resource Sharing (CORS) is enabled via `django-cors-headers`.
- Allowed origins are configured via the `CORS_ALLOWED_ORIGINS` environment variable (comma-separated list of origins).
- For local development, standard frontend ports (`http://localhost:3000`, `http://127.0.0.1:3000`, `http://localhost:5173`, etc.) are permitted.
- `CORS_ALLOW_ALL_ORIGINS = False` ensures strict origin security.

---

## JavaScript Frontend Integration Example

```javascript
async function analyzeHand(file) {
  const formData = new FormData();
  formData.append('image', file);

  const response = await fetch('http://127.0.0.1:8000/api/analyze/', {
    method: 'POST',
    body: formData
  });

  const data = await response.json();

  if (response.ok && data.success) {
    console.log('Measurements:', data.measurements);
    console.log('Annotated Image URL:', data.processed_image_url);
    return data;
  } else {
    console.error('Analysis failed:', data.error);
    throw new Error(data.error);
  }
}
```
