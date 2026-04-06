from pathlib import Path
from typing import Callable, Dict, List

from .complete import complete_ruin_mesh
from .postprocess import export_glb
from .preprocess import preprocess_images, validate_image_set
from .reconstruct import run_reconstruction


StatusCallback = Callable[[str], None]


def run_full_pipeline(image_paths: List[Path], workspace: Path, status: StatusCallback) -> Dict[str, str]:
    workspace.mkdir(parents=True, exist_ok=True)

    pre_dir = workspace / "processed"
    base_mesh = workspace / "base_mesh.obj"
    base_ply = workspace / "base_cloud.ply"
    completed_mesh = workspace / "completed.obj"
    output_glb = workspace / "reconstruction.glb"

    status("Validating input images...")
    valid_images = validate_image_set(image_paths)

    status("Preprocessing images with OpenCV...")
    processed_images = preprocess_images(valid_images, pre_dir)

    status("Generating base 3D reconstruction...")
    run_reconstruction(processed_images, base_mesh, base_ply)

    status("Applying AI-inspired structural completion...")
    complete_ruin_mesh(base_mesh, completed_mesh)

    status("Post-processing and exporting GLB model...")
    export_glb(completed_mesh, output_glb)

    status("Completed")
    return {
        "base_mesh": str(base_mesh),
        "base_cloud": str(base_ply),
        "completed_mesh": str(completed_mesh),
        "glb": str(output_glb),
    }
