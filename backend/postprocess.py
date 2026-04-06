from pathlib import Path

import trimesh


def export_glb(input_mesh: Path, output_glb: Path):
    mesh = trimesh.load_mesh(str(input_mesh), process=True)
    if isinstance(mesh, trimesh.Scene):
        scene = mesh
    else:
        scene = trimesh.Scene(mesh)
    scene.export(str(output_glb))
