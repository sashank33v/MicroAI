"""
AI Microstructure Analyzer - God-Level Image Analysis Engine
Advanced grain boundary detection, ASTM E112 grain sizing,
texture-aware multi-phase estimation, and Groq LLM explanations.
"""

import cv2
import numpy as np
from skimage import measure, morphology, filters, feature, segmentation, exposure
from skimage.restoration import denoise_tv_chambolle
from skimage.morphology import disk, remove_small_objects
from skimage.feature import local_binary_pattern
from scipy import ndimage
from scipy.signal import find_peaks
from sklearn.mixture import GaussianMixture
import os, time, base64, io, math, traceback

# Groq LLM for explanations
import os
from dotenv import load_dotenv
load_dotenv()

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════
# 1. IMAGE QUALITY ASSESSMENT
# ═══════════════════════════════════════════════════════════════

def assess_image_quality(gray: np.ndarray) -> dict:
    """Comprehensive image quality assessment."""
    h, w = gray.shape

    # Sharpness via Laplacian variance
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    laplacian_var = lap.var()
    sharpness = min(1.0, laplacian_var / 800.0)

    # Contrast via percentile range
    p2, p98 = np.percentile(gray, [2, 98])
    contrast = min(1.0, (p98 - p2) / 200.0)

    # Noise via median absolute deviation on high-pass
    noise_level = float(np.median(np.abs(lap))) / 80.0
    noise_score = max(0.0, 1.0 - noise_level)

    # Resolution factor
    resolution = min(1.0, (h * w) / (1024 * 1024))

    # Dynamic range
    dynamic_range = (p98 - p2) / 255.0

    # Histogram uniformity (entropy-based)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
    hist_norm = hist / hist.sum()
    entropy = -np.sum(hist_norm[hist_norm > 0] * np.log2(hist_norm[hist_norm > 0]))
    hist_quality = min(1.0, entropy / 7.5)

    overall = (sharpness * 0.25 + contrast * 0.2 + noise_score * 0.2
               + resolution * 0.1 + dynamic_range * 0.1 + hist_quality * 0.15)

    return {
        "sharpness": round(sharpness, 3),
        "contrast": round(contrast, 3),
        "noise_score": round(noise_score, 3),
        "resolution": round(resolution, 3),
        "dynamic_range": round(dynamic_range, 3),
        "histogram_quality": round(hist_quality, 3),
        "overall": round(overall, 3),
    }


# ═══════════════════════════════════════════════════════════════
# 2. ADAPTIVE PREPROCESSING
# ═══════════════════════════════════════════════════════════════

def _detect_image_type(gray: np.ndarray) -> str:
    """Detect if image is optical microscopy or SEM based on histogram."""
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
    hist_smooth = ndimage.gaussian_filter1d(hist, sigma=5)
    peaks, props = find_peaks(hist_smooth, height=gray.size * 0.005, distance=30)
    # SEM images tend to have narrower intensity range and single dominant peak
    p5, p95 = np.percentile(gray, [5, 95])
    if (p95 - p5) < 100 and len(peaks) <= 2:
        return "sem"
    return "optical"


def preprocess_image(image: np.ndarray) -> np.ndarray:
    """Adaptive multi-stage preprocessing based on image characteristics."""
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    img_type = _detect_image_type(gray)
    quality = assess_image_quality(gray)

    # 1. Morphological Illumination Correction (Crucial for varied microscopes)
    # This flattens uneven lighting by estimating the background envelope.
    kernel_bg = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (51, 51))
    background = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel_bg)
    background = cv2.GaussianBlur(background, (25, 25), 0)
    # Add mean back to keep overall brightness
    gray = cv2.subtract(gray, background)
    gray = cv2.add(gray, np.full_like(gray, np.mean(background)))

    # 2. Adaptive denoising strength
    if quality["noise_score"] < 0.5:
        # High noise: strong bilateral + NLMeans
        denoised = cv2.bilateralFilter(gray, d=11, sigmaColor=85, sigmaSpace=85)
        denoised = cv2.fastNlMeansDenoising(denoised, h=12, templateWindowSize=7, searchWindowSize=21)
    elif quality["noise_score"] < 0.75:
        denoised = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
        denoised = cv2.fastNlMeansDenoising(denoised, h=7, templateWindowSize=7, searchWindowSize=21)
    else:
        # Low noise: light bilateral only
        denoised = cv2.bilateralFilter(gray, d=7, sigmaColor=50, sigmaSpace=50)

    # 3. Adaptive CLAHE
    clip_limit = 3.5 if quality["contrast"] < 0.4 else 2.5 if quality["contrast"] < 0.7 else 1.5
    tile_size = 16 if img_type == "sem" else 8
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
    enhanced = clahe.apply(denoised)

    # 4. Unsharp masking for low-sharpness images
    if quality["sharpness"] < 0.4:
        blurred = cv2.GaussianBlur(enhanced, (0, 0), 2.0)
        enhanced = cv2.addWeighted(enhanced, 1.5, blurred, -0.5, 0)

    return enhanced


# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════
# 3. GRAIN BOUNDARY DETECTION (God-Level Ridge Fusion)
# ═══════════════════════════════════════════════════════════════

def _detect_boundaries_god(image):
    """Advanced boundary detection using multi-scale ridge detection."""
    from skimage.filters import meijering, sato
    
    # 1. Ridge detection for thin, faint boundaries
    denoised = denoise_tv_chambolle(image, weight=0.1)
    ridge_m = meijering(denoised, sigmas=[1, 2], black_ridges=True)
    ridge_s = sato(denoised, sigmas=[1, 2], black_ridges=True)
    ridge_map = np.maximum(ridge_m, ridge_s)
    ridge_map = (ridge_map - ridge_map.min()) / (ridge_map.max() - ridge_map.min() + 1e-8)
    
    # 2. Local Gradient for contrast edges
    grad_sobel = filters.sobel(image)
    grad_sobel = (grad_sobel - grad_sobel.min()) / (grad_sobel.max() - grad_sobel.min() + 1e-8)
    
    # 3. Adaptive support
    block_size = max(11, min(51, int(min(image.shape) / 15) | 1))
    adaptive = filters.threshold_local(image, block_size, offset=5)
    binary_adaptive = image < adaptive
    
    # Final Fusion
    fused = (ridge_map * 0.65) + (grad_sobel * 0.25) + (binary_adaptive.astype(float) * 0.1)
    fused = filters.gaussian(fused, sigma=0.5)
    
    return fused, binary_adaptive

def detect_grain_boundaries(preprocessed: np.ndarray) -> tuple:
    """Unified entry point for God-Level boundary detection."""
    from skimage import feature, segmentation
    from skimage.segmentation import find_boundaries
    
    # 1. Boundary Map
    boundary_map, binary_adaptive = _detect_boundaries_god(preprocessed)
    
    # 2. Initial Watershed
    dist = ndimage.distance_transform_edt(boundary_map < 0.15)
    dist = filters.gaussian(dist, sigma=1.0)
    coords = feature.peak_local_max(dist, min_distance=10, labels=binary_adaptive)
    mask = np.zeros(dist.shape, dtype=bool)
    mask[tuple(coords.T)] = True
    markers, _ = ndimage.label(mask)
    labels = segmentation.watershed(boundary_map, markers, mask=binary_adaptive)
    
    # 3. RAG-based Region Merging (Eliminates fragmenting)
    def weight_boundary(graph, src, dst, n):
        return np.mean(boundary_map[n['boundary']])
    
    g = graph.rag_boundary(labels, boundary_map)
    labels_merged = graph.merge_hierarchical(labels, g, thresh=0.08, rag_copy=False,
                                            in_place_merge=True,
                                            merge_func=graph.merge_nodes,
                                            weight_func=weight_boundary)
    
    # 4. Final Masks
    vis_boundaries = find_boundaries(labels_merged, mode='thick')
    boundary_mask = (vis_boundaries * 255).astype(np.uint8)
    
    return boundary_mask, labels_merged


# ═══════════════════════════════════════════════════════════════
# 4. GRAIN SIZE ESTIMATION (ASTM E112)
# ═══════════════════════════════════════════════════════════════

def estimate_grain_sizes(markers: np.ndarray, scale_um_per_px: float = 0.5) -> dict:
    """ASTM E112 grain sizing with planimetric + Heyn intercept cross-validation."""
    props = measure.regionprops(markers)
    h, w = markers.shape

    areas_px = []
    perimeters_px = []
    eccentricities = []
    circularities = []
    diameters_um = []
    aspect_ratios = []

    # Adaptive minimum grain area
    min_grain_area = max(50, int(markers.size * 0.00015))
    max_grain_area = markers.size * 0.15  # no single grain > 15% of image

    for p in props:
        if p.label <= 1:
            continue
        if p.area < min_grain_area or p.area > max_grain_area:
            continue
        # Exclude edge-touching grains
        r0, c0, r1, c1 = p.bbox
        if r0 <= 2 or c0 <= 2 or r1 >= h - 3 or c1 >= w - 3:
            continue

        areas_px.append(p.area)
        perimeters_px.append(p.perimeter)
        eccentricities.append(p.eccentricity)

        circ = (4 * np.pi * p.area) / (p.perimeter ** 2) if p.perimeter > 0 else 0
        circularities.append(min(1.0, circ))

        # Aspect ratio from oriented bounding box
        if p.minor_axis_length > 0:
            aspect_ratios.append(p.major_axis_length / p.minor_axis_length)
        else:
            aspect_ratios.append(1.0)

        area_um2 = p.area * (scale_um_per_px ** 2)
        diameters_um.append(2 * np.sqrt(area_um2 / np.pi))

    if not areas_px:
        return {
            "count": 0, "avg_size_um": 0, "min_size_um": 0, "max_size_um": 0,
            "std_dev": 0, "astm_number": 0, "avg_circularity": 0,
            "avg_eccentricity": 0, "grain_uniformity": 0, "avg_aspect_ratio": 1.0,
            "intercept_grain_size_um": 0,
        }

    avg_d = float(np.mean(diameters_um))
    std_d = float(np.std(diameters_um))
    areas_um2 = [a * (scale_um_per_px ** 2) for a in areas_px]

    # ASTM E112 planimetric: G = (6.643856 × log10(N_A)) - 3.288
    # N_A = number of grains per mm² at 1x magnification
    total_area_mm2 = (h * w * scale_um_per_px**2) / 1e6
    N_A = len(areas_px) / total_area_mm2 if total_area_mm2 > 0 else 0
    if N_A > 0:
        astm_g_plan = 6.643856 * np.log10(N_A) - 3.288
    else:
        astm_g_plan = 0

    # Heyn lineal intercept method (3 orientations)
    intercept_d = _heyn_intercept(markers, scale_um_per_px)

    # Cross-validate: use average of planimetric and intercept
    if intercept_d > 0:
        avg_area_from_intercept = np.pi * (intercept_d / 2) ** 2
        N_A_intercept = 1e6 / avg_area_from_intercept if avg_area_from_intercept > 0 else 0
        astm_g_int = 6.643856 * np.log10(N_A_intercept) - 3.288 if N_A_intercept > 0 else astm_g_plan
        astm_g = (astm_g_plan + astm_g_int) / 2
    else:
        astm_g = astm_g_plan
        intercept_d = avg_d

    astm_g = max(-1.0, min(14.0, astm_g))

    uniformity = 1.0 - min(1.0, std_d / avg_d) if avg_d > 0 else 0

    return {
        "count": len(areas_px),
        "avg_size_um": round(avg_d, 1),
        "min_size_um": round(float(np.min(diameters_um)), 1),
        "max_size_um": round(float(np.max(diameters_um)), 1),
        "std_dev": round(std_d, 1),
        "astm_number": round(float(astm_g), 1),
        "avg_circularity": round(float(np.mean(circularities)), 3),
        "avg_eccentricity": round(float(np.mean(eccentricities)), 3),
        "grain_uniformity": round(uniformity, 3),
        "avg_aspect_ratio": round(float(np.mean(aspect_ratios)), 2),
        "intercept_grain_size_um": round(float(intercept_d), 1),
    }


def _heyn_intercept(markers: np.ndarray, scale: float, n_lines: int = 20) -> float:
    """Heyn lineal intercept method with 3 orientations (0°, 60°, 120°)."""
    h, w = markers.shape
    intercept_lengths = []

    for angle_deg in [0, 60, 120]:
        angle_rad = np.radians(angle_deg)
        cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)

        for i in range(n_lines):
            if angle_deg == 0:
                y = int(h * (i + 1) / (n_lines + 1))
                xs = np.arange(0, w)
                ys = np.full_like(xs, y)
            elif angle_deg == 60:
                t = np.linspace(0, min(h, w) - 1, max(h, w))
                start_y = int(h * (i + 1) / (n_lines + 1))
                xs = (t * cos_a).astype(int)
                ys = (start_y + t * sin_a).astype(int)
                valid = (xs >= 0) & (xs < w) & (ys >= 0) & (ys < h)
                xs, ys = xs[valid], ys[valid]
            else:
                t = np.linspace(0, min(h, w) - 1, max(h, w))
                start_y = int(h * (i + 1) / (n_lines + 1))
                xs = (t * cos_a).astype(int) + w // 2
                ys = (start_y + t * sin_a).astype(int)
                valid = (xs >= 0) & (xs < w) & (ys >= 0) & (ys < h)
                xs, ys = xs[valid], ys[valid]

            if len(xs) < 10:
                continue

            labels_along = markers[ys, xs]
            # Count boundary crossings (label changes, excluding boundaries=-1 and bg=1)
            crossings = 0
            prev = labels_along[0]
            for lbl in labels_along[1:]:
                if lbl != prev and lbl > 1 and prev > 1:
                    crossings += 1
                if lbl > 1:
                    prev = lbl

            line_length_um = len(xs) * scale
            if crossings > 0:
                intercept_lengths.append(line_length_um / crossings)

    if intercept_lengths:
        return float(np.mean(intercept_lengths))
    return 0.0


# ═══════════════════════════════════════════════════════════════
# 8. AI EXPLANATION (Senior Metallurgical Briefing)
# ═══════════════════════════════════════════════════════════════

def generate_explanation(gs, phases, defects, defect_pct, quality):
    """Generate expert engineering briefing via Groq or fallback."""
    if not GROQ_AVAILABLE or not os.environ.get("GROQ_API_KEY"):
        return _template_explanation(gs, phases, defects, defect_pct, quality)
        
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    phase_str = ", ".join([f"{p['name']} ({p['percentage']}%)" for p in phases])
    grain_str = f"Avg: {gs['avg_size_um']}um, G: {gs['astm_number']}, Intercept: {gs['intercept_grain_size_um']}um, Unif: {gs['grain_uniformity']}"
    defect_str = ", ".join([f"{d['type']} ({d['severity']})" for d in defects]) if defects else "None"
    
    prompt = f"""SENIOR METALLURGICAL BRIEFING:
    - PHASES: {phase_str}
    - GRAINS: {grain_str}
    - DEFECTS: {defect_str}
    - IMAGE QUALITY: {quality['overall']*100:.1f}%
    
    PLEASE PROVIDE:
    1. MATERIAL CLASS ID: (e.g. Medium Carbon Steel, Duplex Stainless, Cast Iron)
    2. MECHANICAL PROFILE: (Brinell/Rockwell estimates, Ductility, Tensile Strength expectations)
    3. PROCESSING INFERRENCE: (Thermal history, mechanical working history)
    4. QUALITY GRADE: (Match with technical standards ASTM/AISI)
    5. RECOMMENDATIONS: (Processing adjustments for optimal properties)
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3
        )
        return chat_completion.choices[0].message.content
    except Exception:
        return _template_explanation(gs, phases, defects, defect_pct, quality)


def compute_grain_distribution(markers: np.ndarray, scale: float = 0.5) -> list:
    """Compute grain size distribution histogram for frontend charts."""
    props = measure.regionprops(markers)
    h, w = markers.shape
    min_area = max(50, int(markers.size * 0.00015))

    diameters = []
    for p in props:
        if p.label <= 1 or p.area < min_area:
            continue
        r0, c0, r1, c1 = p.bbox
        if r0 <= 2 or c0 <= 2 or r1 >= h - 3 or c1 >= w - 3:
            continue
        area_um2 = p.area * (scale ** 2)
        diameters.append(2 * np.sqrt(area_um2 / np.pi))

    if not diameters:
        return []

    diameters = np.array(diameters)
    n_bins = min(10, max(4, len(diameters) // 5))
    counts, edges = np.histogram(diameters, bins=n_bins)

    distribution = []
    for i in range(len(counts)):
        distribution.append({
            "range": f"{edges[i]:.0f}-{edges[i+1]:.0f}",
            "count": int(counts[i]),
            "min_um": round(float(edges[i]), 1),
            "max_um": round(float(edges[i+1]), 1),
        })
    return distribution


# ═══════════════════════════════════════════════════════════════
# 5. MULTI-PHASE DETECTION (Texture-aware GMM clustering)
# ═══════════════════════════════════════════════════════════════

def estimate_phases(gray: np.ndarray, markers: np.ndarray = None, bgr_image: np.ndarray = None) -> list:
    """
    Advanced phase detection with Physical Descriptor generation.
    Does NOT hardcode steel phases. Classifies physical attributes for the LLM.
    Uses LAB color space if bgr_image is provided to identify colored phases (Brass/Copper).
    """
    h, w = gray.shape

    # --- Step 1: Histogram analysis ---
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
    hist_smooth = ndimage.gaussian_filter1d(hist.astype(float), sigma=5)

    # Find peaks (potential phase centers)
    peaks, _ = find_peaks(hist_smooth, height=gray.size * 0.003, distance=25, prominence=gray.size * 0.001)

    # --- Step 2: LBP texture features ---
    lbp = local_binary_pattern(gray, P=8, R=1, method='uniform')
    lbp_norm = (lbp / lbp.max() * 255).astype(np.uint8) if lbp.max() > 0 else lbp.astype(np.uint8)

    # --- Step 3: GMM clustering features ---
    step = max(1, int(np.sqrt(h * w / 50000)))
    
    # Base features: Intensity & Texture
    intensity_samples = gray[::step, ::step].ravel().astype(np.float64).reshape(-1, 1)
    texture_samples = lbp_norm[::step, ::step].ravel().astype(np.float64).reshape(-1, 1)
    features = np.hstack([intensity_samples * 2, texture_samples])
    
    # Color features: Support for Cu/Zn/Brass alloys
    if bgr_image is not None and len(bgr_image.shape) == 3:
        lab_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2LAB)
        # Extract A (Green-Red) and B (Blue-Yellow) channels
        a_channel = lab_image[:, :, 1]
        b_channel = lab_image[:, :, 2]
        
        a_samples = a_channel[::step, ::step].ravel().astype(np.float64).reshape(-1, 1)
        b_samples = b_channel[::step, ::step].ravel().astype(np.float64).reshape(-1, 1)
        
        # Heavily weight color variance to separate colored phases
        features = np.hstack([features, a_samples * 1.5, b_samples * 1.5])

    # Determine optimal number of phases (2-4)
    best_n = 2
    best_bic = np.inf
    for n in range(2, min(5, max(3, len(peaks) + 1))):
        try:
            gmm = GaussianMixture(n_components=n, random_state=42, max_iter=100, covariance_type='full')
            gmm.fit(features)
            bic = gmm.bic(features)
            if bic < best_bic:
                best_bic = bic
                best_n = n
        except Exception:
            continue

    # Fit final GMM
    gmm = GaussianMixture(n_components=best_n, random_state=42, max_iter=200, covariance_type='full')
    gmm.fit(features)

    # Predict on full image
    full_intensity = gray.ravel().astype(np.float64).reshape(-1, 1)
    full_texture = lbp_norm.ravel().astype(np.float64).reshape(-1, 1)
    full_features = np.hstack([full_intensity * 2, full_texture])
    
    if bgr_image is not None and len(bgr_image.shape) == 3:
        a_full = lab_image[:, :, 1].ravel().astype(np.float64).reshape(-1, 1)
        b_full = lab_image[:, :, 2].ravel().astype(np.float64).reshape(-1, 1)
        full_features = np.hstack([full_features, a_full * 1.5, b_full * 1.5])

    labels_flat = gmm.predict(full_features)
    labels = labels_flat.reshape((h, w))

    # Compute phase percentages and descriptors
    phase_info = []
    colors = ["#60a5fa", "#f97316", "#34d399", "#a78bfa", "#fbbf24"]
    for i in range(best_n):
        mask = (labels == i)
        pct = float(mask.sum()) / (h*w) * 100
        mean_int = float(np.mean(gray[mask])) if mask.sum() > 0 else 128
        mean_tex = float(np.mean(lbp_norm[mask])) if mask.sum() > 0 else 0
        std_int = float(np.std(gray[mask])) if mask.sum() > 0 else 0
        
        # Analyze morphology using contours on phase mask
        contours, _ = cv2.findContours(mask.astype(np.uint8)*255, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        avg_aspect, avg_circ = 1.0, 1.0
        if contours:
            areas = [cv2.contourArea(c) for c in contours]
            valid_c = [c for c, a in zip(contours, areas) if a > 10]
            if valid_c:
                aspects, circs = [], []
                for c in valid_c:
                    area = cv2.contourArea(c)
                    perim = cv2.arcLength(c, True)
                    circs.append((4 * np.pi * area) / (perim ** 2) if perim > 0 else 0)
                    rect = cv2.minAreaRect(c)
                    ar = max(rect[1][0], rect[1][1]) / (min(rect[1][0], rect[1][1]) + 1e-6)
                    aspects.append(ar)
                avg_aspect = float(np.mean(aspects))
                avg_circ = float(np.mean(circs))
        
        phase_info.append({
            "id": i,
            "pct": pct,
            "mean_intensity": mean_int,
            "mean_texture": mean_tex,
            "std_intensity": std_int,
            "aspect_ratio": avg_aspect,
            "circularity": avg_circ
        })

    # Filter out tiny phases < 2%
    phase_info = [p for p in phase_info if p["pct"] >= 2.0]
    if not phase_info:
        phase_info = [{"pct": 100.0, "mean_intensity": float(np.mean(gray)),
                       "mean_texture": 0, "std_intensity": 0, "aspect_ratio": 1.0, "circularity": 1.0}]

    # Normalize percentages
    total = sum(p["pct"] for p in phase_info)
    for p in phase_info:
        p["pct"] = p["pct"] / total * 100

    # Sort by percentage (largest phase is Matrix)
    phase_info.sort(key=lambda x: x["pct"], reverse=True)

    # Assign generic physical descriptors instead of hardcoded steel names
    phases = []
    for idx, p in enumerate(phase_info):
        # Tone
        tone = "Dark" if p["mean_intensity"] < 80 else "Mid-tone" if p["mean_intensity"] < 160 else "Light"
        # Role
        role = "Primary Matrix" if idx == 0 and p["pct"] > 50 else f"Secondary Phase {idx}"
        # Texture
        tex = "Textured/Lamellar" if p["std_intensity"] > 25 or p["mean_texture"] > 80 else "Smooth/Solid"
        # Shape
        shape = "Elongated" if p["aspect_ratio"] > 2.5 else "Equiaxed/Blocky"
        if p["pct"] < 30 and p["circularity"] > 0.6:
            shape = "Spheroidal Precipitates"
            
        desc_name = f"{role} ({tone}, {tex}, {shape})"
        
        phases.append({
            "name": desc_name,
            "percentage": round(p["pct"], 1),
            "color": colors[idx % len(colors)],
            # Keep raw stats for LLM analysis without sending to frontend directly
            "_raw_intensity": round(p["mean_intensity"], 1),
            "_raw_morph": f"AR={round(p['aspect_ratio'], 1)}, C={round(p['circularity'], 2)}"
        })

    return phases


# ═══════════════════════════════════════════════════════════════
# 6. DEFECT DETECTION (Enhanced)
# ═══════════════════════════════════════════════════════════════

def detect_defects(preprocessed: np.ndarray, markers: np.ndarray) -> list:
    """Enhanced defect detection with local statistics and texture analysis."""
    defects = []
    h, w = preprocessed.shape
    total_area = h * w

    # Local statistics for adaptive thresholding
    local_mean = cv2.blur(preprocessed.astype(np.float32), (51, 51))
    local_std = np.sqrt(cv2.blur((preprocessed.astype(np.float32) - local_mean)**2, (51, 51)))
    local_std = np.maximum(local_std, 5)  # avoid division by zero

    # --- Dark anomalies (using local statistics) ---
    z_score = (preprocessed.astype(np.float32) - local_mean) / local_std
    dark_mask = (z_score < -2.0).astype(np.uint8) * 255

    kernel_sm = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    kernel_md = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, kernel_sm)
    dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_CLOSE, kernel_md)

    contours_dark, _ = cv2.findContours(dark_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours_dark:
        area = cv2.contourArea(cnt)
        if area < max(15, total_area * 0.00003):
            continue

        perimeter = cv2.arcLength(cnt, True)
        pct = (area / total_area) * 100
        circularity = (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0

        rect = cv2.minAreaRect(cnt)
        rect_w, rect_h = rect[1]
        aspect_ratio = max(rect_w, rect_h) / (min(rect_w, rect_h) + 1e-6)

        M = cv2.moments(cnt)
        cx = int(M["m10"] / M["m00"]) if M["m00"] > 0 else w // 2
        cy = int(M["m01"] / M["m00"]) if M["m00"] > 0 else h // 2

        if circularity > 0.6 and aspect_ratio < 2.0:
            defect_type = "Porosity" if area < total_area * 0.005 else "Void"
        elif aspect_ratio > 3.0:
            defect_type = "Micro-crack"
        elif circularity < 0.3:
            defect_type = "Irregular void"
        else:
            defect_type = "Porosity"

        defects.append({
            "type": defect_type,
            "location": _get_location(cx, cy, w, h),
            "severity": _classify_severity(pct, defect_type),
            "area_percentage": round(pct, 3),
            "circularity": round(circularity, 3),
            "aspect_ratio": round(aspect_ratio, 2),
        })

    # --- Bright anomalies (inclusions) ---
    bright_mask = (z_score > 2.5).astype(np.uint8) * 255
    bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_OPEN, kernel_sm)

    contours_bright, _ = cv2.findContours(bright_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours_bright:
        area = cv2.contourArea(cnt)
        if area < max(10, total_area * 0.00002):
            continue

        pct = (area / total_area) * 100
        perimeter = cv2.arcLength(cnt, True)
        circularity = (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0

        M = cv2.moments(cnt)
        cx = int(M["m10"] / M["m00"]) if M["m00"] > 0 else w // 2
        cy = int(M["m01"] / M["m00"]) if M["m00"] > 0 else h // 2

        if circularity > 0.7:
            inc_type = "Oxide inclusion"
        elif circularity > 0.4:
            inc_type = "Sulfide inclusion"
        else:
            inc_type = "Non-metallic inclusion"

        defects.append({
            "type": inc_type,
            "location": _get_location(cx, cy, w, h),
            "severity": _classify_severity(pct, inc_type),
            "area_percentage": round(pct, 3),
            "circularity": round(circularity, 3),
            "aspect_ratio": 1.0,
        })

    # --- Texture anomalies via local entropy ---
    try:
        entropy_img = filters.rank.entropy(preprocessed, morphology.disk(5))
        entropy_mean = np.mean(entropy_img)
        entropy_std = np.std(entropy_img)
        high_entropy = (entropy_img > entropy_mean + 2.5 * entropy_std).astype(np.uint8) * 255
        high_entropy = cv2.morphologyEx(high_entropy, cv2.MORPH_OPEN, kernel_md)

        contours_ent, _ = cv2.findContours(high_entropy, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours_ent:
            area = cv2.contourArea(cnt)
            if area < total_area * 0.001:
                continue
            pct = (area / total_area) * 100
            M = cv2.moments(cnt)
            cx = int(M["m10"] / M["m00"]) if M["m00"] > 0 else w // 2
            cy = int(M["m01"] / M["m00"]) if M["m00"] > 0 else h // 2
            defects.append({
                "type": "Segregation zone",
                "location": _get_location(cx, cy, w, h),
                "severity": "Minor" if pct < 2 else "Moderate",
                "area_percentage": round(pct, 3),
                "circularity": 0.0,
                "aspect_ratio": 1.0,
            })
    except Exception:
        pass

    defects.sort(key=lambda d: d["area_percentage"], reverse=True)
    return defects[:15]


def _get_location(cx, cy, w, h):
    col = "left" if cx < w / 3 else "right" if cx > 2 * w / 3 else "center"
    row = "Upper" if cy < h / 3 else "Lower" if cy > 2 * h / 3 else "Mid"
    return f"{row}-{col} region"


def _classify_severity(area_pct, defect_type):
    if defect_type in ("Micro-crack", "Void"):
        if area_pct < 0.05: return "Negligible"
        if area_pct < 0.2: return "Minor"
        if area_pct < 0.8: return "Moderate"
        return "Significant"
    else:
        if area_pct < 0.2: return "Negligible"
        if area_pct < 0.8: return "Minor"
        if area_pct < 2.5: return "Moderate"
        return "Significant"


# ═══════════════════════════════════════════════════════════════
# 7. OVERLAY GENERATION
# ═══════════════════════════════════════════════════════════════

def generate_overlay(original, boundary_mask, defects, preprocessed):
    """Publication-quality overlay with color-coded boundaries and defect markers."""
    if len(original.shape) == 2:
        overlay = cv2.cvtColor(original, cv2.COLOR_GRAY2BGR)
    else:
        overlay = original.copy()

    h, w = preprocessed.shape

    # Grain boundaries in cyan
    boundary_layer = overlay.copy()
    # Dilate boundaries for visibility
    boundary_thick = cv2.dilate(boundary_mask, np.ones((2, 2), np.uint8), iterations=1)
    boundary_layer[boundary_thick > 0] = [255, 255, 0]
    overlay = cv2.addWeighted(overlay, 0.65, boundary_layer, 0.35, 0)
    overlay[boundary_thick > 0] = [200, 240, 0]

    # Local anomaly detection for defect overlay
    local_mean = cv2.blur(preprocessed.astype(np.float32), (51, 51))
    local_std = np.sqrt(cv2.blur((preprocessed.astype(np.float32) - local_mean)**2, (51, 51)))
    local_std = np.maximum(local_std, 5)
    z_score = (preprocessed.astype(np.float32) - local_mean) / local_std

    # Dark defects in red
    dark_mask = (z_score < -2.0).astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    dark_mask = cv2.morphologyEx(dark_mask, cv2.MORPH_OPEN, kernel)
    defect_layer = overlay.copy()
    defect_layer[dark_mask > 0] = [0, 0, 255]
    overlay = cv2.addWeighted(overlay, 0.8, defect_layer, 0.2, 0)

    # Bright defects in magenta
    bright_mask = (z_score > 2.5).astype(np.uint8) * 255
    bright_mask = cv2.morphologyEx(bright_mask, cv2.MORPH_OPEN, kernel)
    inc_layer = overlay.copy()
    inc_layer[bright_mask > 0] = [255, 0, 255]
    overlay = cv2.addWeighted(overlay, 0.85, inc_layer, 0.15, 0)

    # Scale bar
    bar_px = min(150, w // 4)
    bar_um = bar_px * 0.5
    bar_y = h - 30
    bar_x = w - bar_px - 20
    cv2.rectangle(overlay, (bar_x, bar_y), (bar_x + bar_px, bar_y + 6), (255, 255, 255), -1)
    cv2.rectangle(overlay, (bar_x, bar_y), (bar_x + bar_px, bar_y + 6), (0, 0, 0), 1)
    cv2.putText(overlay, f"{bar_um:.0f} um", (bar_x + 5, bar_y - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

    return overlay


# ═══════════════════════════════════════════════════════════════
# 8. AI EXPLANATION (Senior Metallurgical Briefing)
# ═══════════════════════════════════════════════════════════════

def generate_explanation(gs, phases, defects, defect_pct, quality, material_type="Unknown"):
    """Generate expert engineering briefing via Groq or fallback via templates."""
    if not GROQ_AVAILABLE or not os.environ.get("GROQ_API_KEY"):
        return _template_explanation(gs, phases, defects, defect_pct, quality)
        
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # Expose raw morphological data to LLM so it can guess the exact alloy
    phase_lines = []
    for p in phases:
        raw_i = p.get("_raw_intensity", "N/A")
        raw_m = p.get("_raw_morph", "N/A")
        phase_lines.append(f"- {p['name']}: {p['percentage']}% (Intensity: {raw_i}, Morph: {raw_m})")
    phase_str = "\n".join(phase_lines)
    
    grain_str = f"Avg: {gs['avg_size_um']}um, ASTM G: {gs['astm_number']}, Intercept: {gs['intercept_grain_size_um']}um, Unif: {gs['grain_uniformity']}"
    defect_str = ", ".join([f"{d['type']} ({d['severity']})" for d in defects]) if defects else "None"
    
    prompt = f"""YOU ARE A SENIOR METALLURGICAL SCIENTIST (PhD).
    Analyze these physical descriptors of a metallic microstructure.
    The user has specified the base material family as: **{material_type}**.
    Use this information to anchor your phase identification. If it is "Unknown", deduce the most likely family.

    PHYSICAL DESCRIPTORS:
    PHASES:
    {phase_str}
    
    GRAINS: {grain_str}
    DEFECTS: {defect_str}
    
    TASK: Based on the requested material family ({material_type}) and the physical morphology (brightness, shape, volume fraction), IDENTIFY the most likely alloy and phases.
    
    OUTPUT FORMAT (Use EXACT headings below):
    1. LIKELY MATERIAL & ALLOY CLASS: (List top 2 candidates based on the known family, e.g. "Likely Hypoeutectic Al-Si Alloy")
    2. METALLURGICAL PHASE IDENTIFICATION: (Map our "Phase 1 / Phase 2" descriptors to actual metallurgical names like Alpha matrix, Silicon particles, Pearlite, Martensite, etc. Explain why based on morphology).
    3. PROCESSING INFERENCE: (e.g., As-cast, Annealed, Quenched, directionally rolled)
    4. ESTIMATED MECHANICAL PROFILE: (Relative strength, ductility, hardness based on grain size and phases)
    5. QUALITY ASSESSMENT: (Note any issues with defects or grain heterogeneity)
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.2
        )
        return chat_completion.choices[0].message.content
    except Exception:
        return _template_explanation(gs, phases, defects, defect_pct, quality)


def _template_explanation(gs, phases, defects, defect_pct, quality):
    """Enhanced template-based explanation with detailed engineering insights."""
    sections = []

    if gs["count"] > 0:
        size = gs["avg_size_um"]
        size_desc = ("ultra-fine" if size < 10 else "very fine" if size < 20 else
                     "fine" if size < 35 else "moderate" if size < 60 else
                     "coarse" if size < 100 else "very coarse")
        unif = gs.get("grain_uniformity", 0)
        unif_desc = "highly uniform" if unif > 0.75 else "moderately uniform" if unif > 0.45 else "heterogeneous"

        sections.append(
            f"MICROSTRUCTURE OVERVIEW: The specimen exhibits a {size_desc}, {unif_desc} grain structure. "
            f"Analysis measured {gs['count']} complete grains (edge-touching grains excluded per ASTM E112 §9)."
        )

        sections.append(
            f"GRAIN ANALYSIS: Mean equivalent circular diameter (ECD) = {size} μm "
            f"(ASTM E112 grain size number G = {gs['astm_number']}). "
            f"Size distribution: {gs['min_size_um']}–{gs['max_size_um']} μm (σ = {gs['std_dev']} μm). "
            f"Heyn intercept grain size: {gs.get('intercept_grain_size_um', 'N/A')} μm. "
            f"Mean circularity = {gs['avg_circularity']:.3f}, eccentricity = {gs['avg_eccentricity']:.3f}."
        )

        # Hall-Petch estimation
        if size > 0:
            sigma_0 = 70  # MPa for ferrite
            k_y = 0.74  # MPa·mm^(1/2) for low-carbon steel
            sigma_y = sigma_0 + k_y / np.sqrt(size / 1000)
            sections.append(
                f"MECHANICAL PROPERTIES: Based on Hall-Petch relationship (σ_y = σ_0 + k_y·d^(-1/2)), "
                f"estimated yield strength ≈ {sigma_y:.0f} MPa for ferrite matrix. "
                f"{'Fine grain size provides excellent strength-toughness balance.' if size < 30 else ''}"
                f"{'Coarse grains suggest annealed condition with good ductility but lower strength.' if size > 80 else ''}"
            )

        circ = gs.get("avg_circularity", 0)
        ar = gs.get("avg_aspect_ratio", 1.0)
        if circ > 0.75 and ar < 1.5:
            sections.append("GRAIN MORPHOLOGY: Equiaxed grains indicate full recrystallization, consistent with annealing or normalizing treatment.")
        elif circ > 0.5:
            sections.append("GRAIN MORPHOLOGY: Slightly elongated grains suggest partial recrystallization or light cold work followed by recovery.")
        elif circ > 0:
            sections.append(f"GRAIN MORPHOLOGY: Significantly elongated grains (aspect ratio {ar:.1f}) indicate directional processing such as rolling or forging without full recrystallization.")

    if phases:
        phase_str = ", ".join([f"{p['name']} ({p['percentage']}%)" for p in phases])
        sections.append(f"PHASE COMPOSITION: Detected phases — {phase_str}.")

        phase_names = {p["name"].lower() for p in phases}
        if "martensite" in phase_names:
            mart_pct = next((p["percentage"] for p in phases if "martensite" in p["name"].lower()), 0)
            sections.append(
                f"Martensite ({mart_pct}%) indicates rapid cooling (quenching) from austenitizing temperature. "
                f"Expected hardness: {350 + mart_pct * 3:.0f}–{400 + mart_pct * 4:.0f} HV. "
                f"Tempering treatment recommended if not already applied."
            )
        if "pearlite" in phase_names and "ferrite" in phase_names:
            ferrite_pct = next((p["percentage"] for p in phases if "ferrite" in p["name"].lower()), 0)
            pearlite_pct = next((p["percentage"] for p in phases if "pearlite" in p["name"].lower()), 0)
            carbon_est = pearlite_pct / 100 * 0.8
            sections.append(
                f"Ferrite-pearlite structure indicates hypo{'eutectoid' if ferrite_pct > 50 else 'er'} steel. "
                f"Estimated carbon content ≈ {carbon_est:.2f}% C (lever rule approximation). "
                f"{'Good weldability and formability expected.' if carbon_est < 0.25 else 'Moderate weldability; preheat recommended for welding.' if carbon_est < 0.45 else 'Poor weldability; special procedures required.'}"
            )
        if "bainite" in phase_names:
            sections.append("Bainite phase suggests intermediate cooling rate or isothermal transformation. Provides good strength-toughness combination.")

    if defects:
        defect_types = list(set(d["type"] for d in defects))
        sections.append(
            f"DEFECT ASSESSMENT: {len(defects)} defect region(s) detected, total affected area = {defect_pct:.2f}%. "
            f"Types: {', '.join(defect_types)}."
        )
        if any("crack" in d["type"].lower() for d in defects):
            sections.append("⚠ CRITICAL: Micro-cracks detected — potential stress concentrators under cyclic loading. Recommend NDE (ultrasonic/dye-penetrant) inspection per ASTM E165/E2375.")
        if defect_pct > 3:
            sections.append("⚠ HIGH DEFECT DENSITY: Total defect area exceeds 3%. Material may not meet acceptance criteria per ASTM E45. Consider rejection or reprocessing.")
        elif defect_pct > 1:
            sections.append("MODERATE DEFECT LEVEL: Acceptable for general structural applications but requires evaluation for fatigue-critical or pressure-containing components.")
        elif defect_pct > 0:
            sections.append("LOW DEFECT LEVEL: Within acceptable limits for most engineering applications per ASTM E45 Method A.")
    else:
        sections.append("DEFECT ASSESSMENT: No significant defects detected. Microstructure appears clean and homogeneous — suitable for high-reliability applications.")

    if quality["overall"] < 0.5:
        weak = "blur" if quality["sharpness"] < 0.4 else "low contrast" if quality["contrast"] < 0.4 else "noise"
        sections.append(f"⚠ IMAGE QUALITY: Score = {quality['overall']:.2f}/1.00 (limited by {weak}). Results may have reduced accuracy. Higher-quality imaging recommended for definitive analysis.")

    return "\n\n".join(sections)


# ═══════════════════════════════════════════════════════════════
# 9. UTILITIES
# ═══════════════════════════════════════════════════════════════

def image_to_base64(image):
    _, buffer = cv2.imencode(".png", image)
    return base64.b64encode(buffer).decode("utf-8")


def compute_confidence(grain_stats, quality, num_defects):
    q = quality["overall"]
    count = grain_stats.get("count", 0)
    uniformity = grain_stats.get("grain_uniformity", 0)

    if count == 0:
        return round(20.0 + q * 20, 1)

    # Multi-factor confidence
    base = 35 + q * 25
    count_boost = min(18, count / 8)
    unif_boost = uniformity * 12
    sharpness_boost = quality.get("sharpness", 0.5) * 8
    # Cross-validation bonus: if intercept and planimetric agree
    intercept_d = grain_stats.get("intercept_grain_size_um", 0)
    avg_d = grain_stats.get("avg_size_um", 0)
    if intercept_d > 0 and avg_d > 0:
        agreement = 1.0 - min(1.0, abs(intercept_d - avg_d) / max(intercept_d, avg_d))
        cross_val_boost = agreement * 8
    else:
        cross_val_boost = 0

    defect_penalty = min(5, num_defects * 0.3)
    confidence = base + count_boost + unif_boost + sharpness_boost + cross_val_boost - defect_penalty
    return round(min(97.0, max(15.0, confidence)), 1)


# ═══════════════════════════════════════════════════════════════
# 10. MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════

def analyze_microstructure(image_path: str, scale_um_per_px: float = 0.5, material_type: str = "Unknown") -> dict:
    """Full analysis pipeline with god-level accuracy."""
    start = time.time()

    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")

    # Keep BGR color for color-aware phase estimation
    bgr_image = image.copy()

    if len(image.shape) == 3:
        gray_raw = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray_raw = image.copy()

    # Step 1: Quality
    quality = assess_image_quality(gray_raw)

    # Step 2: Adaptive preprocessing
    preprocessed = preprocess_image(image)

    # Step 3: Grain boundary detection
    boundary_mask, markers = detect_grain_boundaries(preprocessed)

    # Step 4: Grain sizing
    grain_stats = estimate_grain_sizes(markers, scale_um_per_px)

    # Step 5: Grain distribution
    grain_distribution = compute_grain_distribution(markers, scale_um_per_px)

    # Step 6: Phase estimation (Color-aware)
    phases = estimate_phases(preprocessed, markers, bgr_image=bgr_image)

    # Step 7: Defect detection
    defects = detect_defects(preprocessed, markers)
    total_defect_pct = round(sum(d["area_percentage"] for d in defects), 2)

    # Step 8: Confidence
    confidence = compute_confidence(grain_stats, quality, len(defects))

    # Step 9: AI explanation
    explanation = generate_explanation(grain_stats, phases, defects, total_defect_pct, quality, material_type=material_type)

    # Step 10: Overlays
    overlay = generate_overlay(image, boundary_mask, defects, preprocessed)
    boundary_color = cv2.cvtColor(boundary_mask, cv2.COLOR_GRAY2BGR)

    processing_time = round(time.time() - start, 2)

    return {
        "grain_stats": grain_stats,
        "grain_distribution": grain_distribution,
        "phases": phases,
        "defects": defects,
        "defect_percentage": total_defect_pct,
        "confidence": confidence,
        "ai_explanation": explanation,
        "processing_time": processing_time,
        "image_quality": quality,
        "overlay_base64": image_to_base64(overlay),
        "boundary_base64": image_to_base64(boundary_color),
        "original_base64": image_to_base64(image),
    }
