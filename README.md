# RuinRebuild AI (Hackathon Prototype)

AI-based virtual reconstruction pipeline for partially damaged historical sites.

## What this demo does

1. Accepts multiple ruin images via a web UI.
2. Preprocesses images (resize + denoise + contrast normalize).
3. Builds a **base 3D mesh** from multi-image features (fast pseudo-photogrammetry fallback).
4. Applies **AI-inspired completion** (symmetry + architectural arch prior + smoothing).
5. Exports reconstructed model as `.glb` and visualizes it in an interactive Three.js viewer.

> This is optimized for a hackathon demo: fast, visual, robust on mixed hardware.

---

## Project Structure

```text
Hack-Rankers/
├─ app.py
├─ requirements.txt
├─ backend/
│  ├─ config.py
│  ├─ preprocess.py
│  ├─ reconstruct.py
│  ├─ complete.py
│  ├─ postprocess.py
│  ├─ pipeline.py
│  └─ utils.py
├─ frontend/
│  ├─ index.html
│  ├─ style.css
│  └─ app.js
├─ data/
│  ├─ input/
│  └─ processed/
├─ outputs/
└─ scripts/
   └─ run_windows.bat
```

---

## Windows Setup (Python backend)

### 1) Create virtual environment

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
```

### 2) Install dependencies

```bat
pip install -r requirements.txt
```

### 3) Run app

```bat
python app.py
```

Open: http://127.0.0.1:8000

---

## Optional: Better photogrammetry quality

For more realistic geometry, you can swap the fallback recon module with real COLMAP output.

1. Install COLMAP (Windows).
2. Update `backend/reconstruct.py` to call COLMAP CLI (`feature_extractor`, `mapper`, etc.).
3. Convert sparse/dense outputs to mesh and continue through completion + GLB export.

---

## Pipeline Details

### 1) Data input and validation
- API endpoint `/api/reconstruct` accepts multi-file upload.
- Requires at least 3 images.
- Supported: jpg/jpeg/png/bmp/webp.

### 2) Image preprocessing (OpenCV)
- Auto-resize to max side 1280.
- CLAHE contrast normalization.
- Non-local means denoising.

### 3) Base 3D reconstruction
- SIFT/ORB feature extraction.
- Pairwise matching between adjacent views.
- Synthetic camera arc prior for pseudo triangulation.
- Open3D Poisson meshing.

### 4) AI completion (fast demo mode)
- Mesh symmetry completion (mirror operation).
- Architectural prior (arch geometry) to infer plausible lost sections.
- Hole filling and Laplacian smoothing.

### 5) Post-processing
- Export to `OBJ` and `GLB` for browser visualization.

### 6) Visualization
- Three.js + GLTFLoader viewer.
- Orbit controls, lights, and status updates.

---

## Low GPU / CPU Fallback Strategy

This prototype is CPU-friendly by default:
- No model training.
- Lightweight geometry ops only.
- Works without CUDA.

If GPU is available, you can improve completion realism by integrating:
- TripoSR / Zero123 / Stable-Video-3D as replacement for `backend/complete.py`.

---

## Demo Script (for presentation)

1. Start app: `python app.py`.
2. Open UI and upload 5–15 photos of a ruin (captured around object/site).
3. Click **Run Reconstruction**.
4. Narrate stages shown in status panel:
   - validation
   - preprocessing
   - 3D reconstruction
   - AI completion
   - GLB export
5. Interact with final 3D model (rotate/zoom/pan).
6. Explain possible upgrades:
   - true COLMAP dense reconstruction
   - diffusion-based texture restoration
   - Blender rendering pipeline

---

## Sample usage tips

- Use images with overlap (50%+).
- Keep lighting consistent.
- Avoid motion blur.
- Capture from multiple angles around the structure.

---

## One-click Windows run

```bat
scripts\run_windows.bat
```

