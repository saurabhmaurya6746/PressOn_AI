# utils/coin_detector.py
import cv2
import numpy as np


def get_pixel_to_mm_ratio(image_path, real_coin_diameter_mm=27.0):
    """
    Robust Indian ₹10 reference coin detection and validation pipeline.
    
    Validates candidates by testing for the distinct bimetallic signature of the ₹10 coin:
    - Outer annular ring (0.68*r to 0.95*r): Nickel-Brass with warm golden/yellow hue (high LAB b* >= 140).
    - Inner disc core (0 to 0.52*r): Nickel-Silver / Stainless Steel with cool/neutral tone.
    - Full 360-degree annular continuity across 8 sectors.
    - Concentric seam boundary at ~0.68*r.
    
    Mono-metallic coins (e.g. ₹2, ₹1, ₹5) and random circular objects are explicitly rejected.
    Default reference diameter: 27.0 mm (Indian ₹10 coin).
    """
    image = cv2.imread(image_path)
    if image is None:
        return 0.0, None

    h, w = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    # Sobel gradients for perimeter edge support and internal seam detection
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    grad_mag = np.sqrt(sobelx**2 + sobely**2)

    # Detect circular candidates using HoughCircles
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=35,
        param1=100,
        param2=25,
        minRadius=20,
        maxRadius=int(min(h, w) * 0.45)
    )

    if circles is None:
        print("\n[COIN DETECTOR] No circular candidates found.")
        return 0.0, None

    raw_candidates = np.uint16(np.around(circles))[0]

    # Deduplicate concentric / overlapping candidates
    candidates = []
    for c in raw_candidates:
        x, y, r = int(c[0]), int(c[1]), int(c[2])
        is_dup = False
        for ox, oy, orad in candidates:
            dist = np.sqrt((x - ox)**2 + (y - oy)**2)
            if dist < max(r, orad) * 0.35 and abs(r - orad) < max(r, orad) * 0.30:
                is_dup = True
                break
        if not is_dup:
            candidates.append((x, y, r))

    diagnostics = []
    best_candidate = None
    highest_confidence = -1.0

    print("\n" + "=" * 50)
    print(f"[COIN DETECTOR] Evaluating {len(candidates)} candidate(s) for Rs. 10 reference...")

    for idx, (x, y, r) in enumerate(candidates):
        # 1. Bounds check
        if x - r < 5 or y - r < 5 or x + r >= w - 5 or y + r >= h - 5 or r < 20:
            diag = {
                "candidate": idx,
                "center": (x, y),
                "radius": r,
                "diameter_px": 2 * r,
                "confidence": 0.0,
                "accepted": False,
                "reason": "Out of image bounds or radius < 20px"
            }
            diagnostics.append(diag)
            print(f"  Candidate #{idx} (center=({x},{y}), r={r}px) -> REJECTED: {diag['reason']}")
            continue

        # 2. Circular edge support along perimeter (36 sampled points)
        angles = np.linspace(0, 2 * np.pi, 36, endpoint=False)
        peri_x = np.clip((x + r * np.cos(angles)).astype(int), 0, w - 1)
        peri_y = np.clip((y + r * np.sin(angles)).astype(int), 0, h - 1)
        edge_vals = grad_mag[peri_y, peri_x]
        edge_support = float(np.sum(edge_vals > 20.0)) / 36.0

        # 3. Inner core (0 to 0.52*r) vs Outer ring (0.70*r to 0.95*r)
        mask_inner = np.zeros((h, w), dtype=np.uint8)
        mask_outer = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(mask_inner, (x, y), int(0.52 * r), 255, -1)
        cv2.circle(mask_outer, (x, y), int(0.95 * r), 255, -1)
        cv2.circle(mask_outer, (x, y), int(0.70 * r), 0, -1)

        mean_bgr_in = cv2.mean(image, mask=mask_inner)[:3]
        mean_bgr_out = cv2.mean(image, mask=mask_outer)[:3]
        mean_lab_in = cv2.mean(lab, mask=mask_inner)[:3]
        mean_lab_out = cv2.mean(lab, mask=mask_outer)[:3]

        b_in = mean_lab_in[2]
        b_out = mean_lab_out[2]
        b_diff = b_out - b_in

        # BGR warmth index: (R + G) / 2 - B
        warmth_in = (mean_bgr_in[2] + mean_bgr_in[1]) / 2.0 - mean_bgr_in[0]
        warmth_out = (mean_bgr_out[2] + mean_bgr_out[1]) / 2.0 - mean_bgr_out[0]
        warmth_diff = warmth_out - warmth_in

        # 4. 8-Sector Annular ring uniformity (360-degree brass ring verification)
        sector_b_vals = []
        sec_angles = np.linspace(0, 360, 9)
        for s in range(8):
            s_mask = np.zeros((h, w), dtype=np.uint8)
            cv2.ellipse(s_mask, (x, y), (int(0.95 * r), int(0.95 * r)), 0, sec_angles[s], sec_angles[s + 1], 255, -1)
            cv2.circle(s_mask, (x, y), int(0.70 * r), 0, -1)
            m = cv2.mean(lab, mask=s_mask)
            sector_b_vals.append(m[2])

        ring_min_b = float(np.min(sector_b_vals))
        ring_std_b = float(np.std(sector_b_vals))

        # 5. Concentric seam edge at 0.68*r
        seam_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(seam_mask, (x, y), int(0.68 * r), 255, 2)
        seam_edge_mean = cv2.mean(grad_mag, mask=seam_mask)[0]

        # Normalized Component Scores
        s_bimetal = min(1.0, max(0.0, b_diff / 20.0)) * 0.5 + min(1.0, max(0.0, warmth_diff / 30.0)) * 0.5
        s_brass = min(1.0, max(0.0, (b_out - 135.0) / 15.0))
        s_ring_uniform = min(1.0, max(0.0, 1.0 - (ring_std_b / 10.0)))
        s_circle = min(1.0, edge_support / 0.5)
        s_seam = min(1.0, seam_edge_mean / 30.0)

        # Weighted overall ₹10 confidence
        confidence = (
            0.35 * s_bimetal +
            0.25 * s_brass +
            0.15 * s_ring_uniform +
            0.15 * s_circle +
            0.10 * s_seam
        )

        # Strict Rejection Criteria
        reasons = []
        if edge_support < 0.35:
            reasons.append(f"Weak perimeter circular edge ({edge_support:.2f} < 0.35)")
        if b_diff < 12.0 and warmth_diff < 18.0:
            reasons.append(f"Mono-metallic coin / no bimetallic contrast (b_diff={b_diff:.1f}, warmth_diff={warmth_diff:.1f})")
        if b_out < 140.0:
            reasons.append(f"Outer ring is not brass/gold (b*={b_out:.1f} < 140.0)")
        if ring_min_b < 138.0:
            reasons.append(f"Outer ring not complete 360 deg brass (min sector b*={ring_min_b:.1f} < 138.0)")
        if ring_std_b > 6.0:
            reasons.append(f"Outer ring irregular/non-uniform (std b*={ring_std_b:.1f} > 6.0)")
        if confidence < 0.70:
            reasons.append(f"Overall confidence {confidence:.2f} < 0.70 threshold")

        accepted = (len(reasons) == 0)
        reason_str = "Verified Rs. 10 bimetallic coin" if accepted else "; ".join(reasons)

        diag = {
            "candidate": idx,
            "center": (x, y),
            "radius": r,
            "diameter_px": 2 * r,
            "confidence": round(confidence, 2),
            "edge_support": round(edge_support, 2),
            "b_diff": round(b_diff, 1),
            "outer_b": round(b_out, 1),
            "accepted": accepted,
            "reason": reason_str
        }
        diagnostics.append(diag)

        status_tag = "[ACCEPTED]" if accepted else "[REJECTED]"
        print(f"  Candidate #{idx}: center=({x},{y}), r={r}px, diam={2*r}px, conf={confidence:.2f} -> {status_tag} {reason_str}")

        if accepted and confidence > highest_confidence:
            highest_confidence = confidence
            best_candidate = {
                "center": (x, y),
                "radius": r,
                "diameter_px": 2 * r,
                "confidence": round(confidence, 2),
                "diagnostics": diagnostics
            }

    if best_candidate is not None:
        pixels_per_mm = best_candidate["diameter_px"] / real_coin_diameter_mm
        print("\n" + "=" * 50)
        print(f"[COIN DETECTOR] Successfully Verified Rs. 10 Coin!")
        print(f"-> Center: {best_candidate['center']}, Radius: {best_candidate['radius']}px")
        print(f"-> Diameter: {best_candidate['diameter_px']}px")
        print(f"-> Calculated Scale: {pixels_per_mm:.4f} px/mm (Ref Diameter: {real_coin_diameter_mm} mm)")
        print(f"-> Confidence: {best_candidate['confidence']}")
        print("=" * 50 + "\n")
        return pixels_per_mm, best_candidate
    else:
        print("\n" + "=" * 50)
        print("[COIN DETECTOR] No candidate verified as a valid Rs. 10 coin.")
        print("=" * 50 + "\n")
        return 0.0, None