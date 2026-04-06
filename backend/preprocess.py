from pathlib import Path
from typing import List

import cv2
import numpy as np

from .config import MAX_SIZE, SUPPORTED_EXTENSIONS


def _is_valid_image(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_EXTENSIONS


def validate_image_set(image_paths: List[Path]) -> List[Path]:
    valid = [p for p in image_paths if p.exists() and _is_valid_image(p)]
    if len(valid) < 3:
        raise ValueError("Please upload at least 3 valid images for reconstruction.")
    return valid


def preprocess_images(image_paths: List[Path], output_dir: Path) -> List[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    processed_paths: List[Path] = []

    for idx, path in enumerate(image_paths):
        image = cv2.imread(str(path))
        if image is None:
            continue

        h, w = image.shape[:2]
        scale = min(1.0, MAX_SIZE / max(h, w))
        if scale < 1.0:
            image = cv2.resize(image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(image)
        l = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(l)
        image = cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)

        denoised = cv2.fastNlMeansDenoisingColored(image, None, 3, 3, 7, 21)

        out = output_dir / f"frame_{idx:03d}.jpg"
        cv2.imwrite(str(out), denoised)
        processed_paths.append(out)

    if len(processed_paths) < 3:
        raise ValueError("Not enough readable images after preprocessing.")

    return processed_paths


def compute_sharpness_score(image_path: Path) -> float:
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        return 0.0
    return float(cv2.Laplacian(image, cv2.CV_64F).var())


def select_reference_image(image_paths: List[Path]) -> Path:
    scores = [(p, compute_sharpness_score(p)) for p in image_paths]
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[0][0]
