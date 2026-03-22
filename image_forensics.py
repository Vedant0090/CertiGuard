# ============================================================
# CertiGuard — Phase 3 · Image Forensics
# image_forensics.py  ·  Seal detection & layout analysis
# ============================================================
# What this file does:
#   - Uses OpenCV to detect circular seals/stamps
#   - Checks for signature-like regions (horizontal dark strokes)
#   - Analyses layout: border presence, text density zones
#   - Detects copy-paste artifacts (noise patterns)
#   - Works on PNG/JPG images AND PDF-converted images
# ============================================================

import os

# ── Try importing computer vision libraries ───────────────
try:
    import cv2          # OpenCV — the image processing library
    import numpy as np  # NumPy — math for image arrays
    CV2_SUPPORT = True
except ImportError:
    CV2_SUPPORT = False

try:
    from PIL import Image
    PIL_SUPPORT = True
except ImportError:
    PIL_SUPPORT = False


def load_image_as_cv2(filepath):
    """
    Load any image (PNG/JPG) as an OpenCV array.
    Returns (image_array, grayscale_array, error_message).
    """
    if not CV2_SUPPORT:
        return None, None, "opencv-python not installed"

    try:
        img = cv2.imread(filepath)
        if img is None:
            return None, None, "Could not read image file"
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img, gray, None
    except Exception as e:
        return None, None, str(e)


def detect_circular_seal(gray_img):
    """
    Detect circular stamps/seals using Hough Circle Transform.

    How it works:
      - Converts image to grayscale (already done)
      - Blurs it slightly to reduce noise
      - Looks for circular patterns of any size
      - Returns (found: bool, count: int, detail: str)
    """
    if gray_img is None:
        return False, 0, "No image"

    try:
        # Blur to reduce noise (makes circle detection more reliable)
        blurred = cv2.GaussianBlur(gray_img, (9, 9), 2)

        height, width = gray_img.shape
        min_r = min(width, height) // 30   # minimum circle radius
        max_r = min(width, height) // 4    # maximum circle radius

        # HoughCircles: finds circles in the image
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1.2,           # resolution ratio
            minDist=50,       # min distance between circle centers
            param1=80,        # Canny edge threshold
            param2=30,        # accumulator threshold (lower = more circles found)
            minRadius=min_r,
            maxRadius=max_r
        )

        if circles is not None:
            count = len(circles[0])
            return True, count, f"{count} circular seal(s) detected"
        else:
            return False, 0, "No circular seals detected"

    except Exception as e:
        return False, 0, f"Detection error: {e}"


def detect_signature_region(gray_img):
    """
    Look for signature-like regions.

    Signatures are typically:
      - Dark strokes on white/light background
      - In the lower half of the certificate
      - Irregular, flowing patterns (not straight lines)

    Returns (found: bool, detail: str)
    """
    if gray_img is None:
        return False, "No image"

    try:
        height, width = gray_img.shape

        # Focus on bottom 40% of image (where signatures usually are)
        bottom_region = gray_img[int(height * 0.6):, :]

        # Threshold: turn into black & white
        _, thresh = cv2.threshold(bottom_region, 180, 255, cv2.THRESH_BINARY_INV)

        # Find contours (outlines of dark shapes)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter for signature-sized contours
        # Signatures are medium-sized, wider than tall
        sig_candidates = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = cv2.contourArea(cnt)
            aspect_ratio = w / max(h, 1)

            # Signature-like: wider than tall, medium size, not too small
            if (aspect_ratio > 1.5 and
                area > 200 and
                w > width * 0.05 and
                w < width * 0.5):
                sig_candidates.append((w, h, area))

        if len(sig_candidates) >= 1:
            return True, f"Signature region detected in lower section"
        else:
            return False, "No clear signature region found"

    except Exception as e:
        return False, f"Detection error: {e}"


def detect_border(gray_img):
    """
    Check if the certificate has a border frame.
    Most official certificates have decorative or plain borders.

    Returns (found: bool, detail: str)
    """
    if gray_img is None:
        return False, "No image"

    try:
        height, width = gray_img.shape

        # Sample pixels along the edges (5% margin)
        margin = int(min(height, width) * 0.05)

        # Get edge strips
        top_strip    = gray_img[:margin, :]
        bottom_strip = gray_img[height-margin:, :]
        left_strip   = gray_img[:, :margin]
        right_strip  = gray_img[:, width-margin:]

        # A border shows up as darker pixels along the edges
        # Compare edge darkness vs center
        edge_mean = (top_strip.mean() + bottom_strip.mean() +
                     left_strip.mean() + right_strip.mean()) / 4
        center = gray_img[margin:height-margin, margin:width-margin]
        center_mean = center.mean()

        # If edges are significantly darker than center = border present
        if edge_mean < center_mean - 20:
            return True, "Decorative border detected"
        else:
            return False, "No border frame detected"

    except Exception as e:
        return False, f"Detection error: {e}"


def check_noise_artifacts(gray_img):
    """
    Check for copy-paste or JPEG compression artifacts.

    Real certificates scanned cleanly have smooth noise.
    Tampered/composited images often have inconsistent noise patterns.

    Returns (clean: bool, detail: str)
    """
    if gray_img is None:
        return True, "No image"

    try:
        # Calculate local standard deviation (measure of noise)
        # Divide image into a 4x4 grid
        height, width = gray_img.shape
        grid_h = height // 4
        grid_w = width // 4

        std_values = []
        for row in range(4):
            for col in range(4):
                cell = gray_img[
                    row*grid_h : (row+1)*grid_h,
                    col*grid_w : (col+1)*grid_w
                ]
                std_values.append(float(np.std(cell)))

        # If noise is very inconsistent across regions = possible tampering
        noise_std = float(np.std(std_values))   # variation of variation

        if noise_std > 25:
            return False, f"Inconsistent noise pattern detected (score: {noise_std:.1f})"
        else:
            return True, f"Noise pattern consistent (score: {noise_std:.1f})"

    except Exception as e:
        return True, f"Could not analyse noise: {e}"


def analyze_image_forensics(filepath):
    """
    Main forensics function — runs all image checks.

    Returns:
      checks (list): list of check result dicts
      confidence_delta (int): how much to adjust confidence score
    """
    checks = []
    confidence_delta = 0
    ext = filepath.rsplit(".", 1)[-1].lower()

    # Only run on image files
    if ext not in ("png", "jpg", "jpeg"):
        checks.append({
            "name": "Image forensics",
            "detail": "Forensic analysis runs on image files (PNG/JPG)",
            "status": "warn"
        })
        return checks, 0

    if not CV2_SUPPORT:
        checks.append({
            "name": "Image forensics",
            "detail": "opencv-python not installed — run: pip install opencv-python",
            "status": "warn"
        })
        return checks, 0

    # Load the image
    img, gray, error = load_image_as_cv2(filepath)
    if error:
        checks.append({
            "name": "Image forensics",
            "detail": f"Could not load image: {error}",
            "status": "fail"
        })
        return checks, -10

    # ── Check 1: Seal detection ───────────────────────────
    seal_found, seal_count, seal_detail = detect_circular_seal(gray)
    if seal_found:
        checks.append({
            "name": "Seal / stamp",
            "detail": seal_detail,
            "status": "pass"
        })
        confidence_delta += 15
    else:
        checks.append({
            "name": "Seal / stamp",
            "detail": seal_detail,
            "status": "warn"
        })
        confidence_delta -= 5

    # ── Check 2: Signature detection ─────────────────────
    sig_found, sig_detail = detect_signature_region(gray)
    if sig_found:
        checks.append({
            "name": "Signature region",
            "detail": sig_detail,
            "status": "pass"
        })
        confidence_delta += 10
    else:
        checks.append({
            "name": "Signature region",
            "detail": sig_detail,
            "status": "warn"
        })
        confidence_delta -= 5

    # ── Check 3: Border detection ─────────────────────────
    border_found, border_detail = detect_border(gray)
    if border_found:
        checks.append({
            "name": "Border / frame",
            "detail": border_detail,
            "status": "pass"
        })
        confidence_delta += 5
    else:
        checks.append({
            "name": "Border / frame",
            "detail": border_detail,
            "status": "warn"
        })

    # ── Check 4: Noise / tampering artifacts ─────────────
    clean, noise_detail = check_noise_artifacts(gray)
    if clean:
        checks.append({
            "name": "Tampering check",
            "detail": noise_detail,
            "status": "pass"
        })
        confidence_delta += 10
    else:
        checks.append({
            "name": "Tampering check",
            "detail": noise_detail,
            "status": "fail"
        })
        confidence_delta -= 20

    return checks, confidence_delta
