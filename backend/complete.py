from pathlib import Path

import numpy as np
import trimesh


def _mirror_mesh(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    mirrored = mesh.copy()
    mirrored.vertices[:, 0] *= -1
    mirrored.invert()
    return trimesh.util.concatenate([mesh, mirrored])


def _add_arch_prior(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    # Hackathon visual prior: add an arch-like completion over tallest span.
    bounds = mesh.bounds
    min_b, max_b = bounds
    width = max_b[0] - min_b[0]
    height = max_b[1] - min_b[1]
    depth = max_b[2] - min_b[2]

    arch = trimesh.creation.torus(
        major_radius=max(0.25, width * 0.32),
        minor_radius=max(0.03, min(width, depth) * 0.08),
        major_sections=48,
        minor_sections=16,
    )
    arch.apply_scale([1.0, 0.7, max(0.3, depth * 0.8)])
    arch.apply_translation([
        (min_b[0] + max_b[0]) / 2.0,
        min_b[1] + max(0.2, height * 0.7),
        (min_b[2] + max_b[2]) / 2.0,
    ])

    return trimesh.util.concatenate([mesh, arch])


def complete_ruin_mesh(input_mesh: Path, output_mesh: Path):
    mesh = trimesh.load_mesh(str(input_mesh), process=True)

    if isinstance(mesh, trimesh.Scene):
        mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))

    mesh = _mirror_mesh(mesh)
    mesh = _add_arch_prior(mesh)

    mesh.fill_holes()
    mesh.remove_degenerate_faces()
    mesh.remove_duplicate_faces()
    mesh.remove_infinite_values()
    mesh.merge_vertices()

    # Light smoothing for believable restored surfaces.
    trimesh.smoothing.filter_laplacian(mesh, lamb=0.35, iterations=8)

    mesh.export(str(output_mesh))
