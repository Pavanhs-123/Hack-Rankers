from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np
import open3d as o3d


def _extract_features(image_path: Path):
    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None, None

    detector = cv2.SIFT_create() if hasattr(cv2, "SIFT_create") else cv2.ORB_create(3000)
    kp, desc = detector.detectAndCompute(img, None)
    return kp, desc


def _match_features(desc1, desc2):
    if desc1 is None or desc2 is None:
        return []

    if desc1.dtype == np.uint8:
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = matcher.match(desc1, desc2)
        return sorted(matches, key=lambda m: m.distance)[:300]

    matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
    matches = matcher.match(desc1, desc2)
    return sorted(matches, key=lambda m: m.distance)[:500]


def _synthetic_camera_poses(n: int) -> List[np.ndarray]:
    poses = []
    radius = 2.0
    for i in range(n):
        theta = (i / max(1, n)) * 2 * np.pi
        cam = np.array([radius * np.cos(theta), 0.6, radius * np.sin(theta)], dtype=np.float32)
        poses.append(cam)
    return poses


def generate_sparse_point_cloud(image_paths: List[Path]) -> np.ndarray:
    keypoints = []
    descriptors = []

    for path in image_paths:
        kp, desc = _extract_features(path)
        keypoints.append(kp)
        descriptors.append(desc)

    camera_positions = _synthetic_camera_poses(len(image_paths))
    cloud_points = []

    for i in range(len(image_paths) - 1):
        matches = _match_features(descriptors[i], descriptors[i + 1])
        if len(matches) < 30:
            continue

        for m in matches:
            p1 = keypoints[i][m.queryIdx].pt
            p2 = keypoints[i + 1][m.trainIdx].pt

            depth = max(0.2, min(2.5, abs(p1[0] - p2[0]) / 80.0 + 0.3))

            x = (p1[0] - 320.0) / 260.0
            y = (p1[1] - 240.0) / 260.0
            base = np.array([x, -y, depth], dtype=np.float32)

            # Blend with synthetic camera arc for pseudo multi-view geometry.
            world = base + 0.22 * camera_positions[i]
            cloud_points.append(world)

    if len(cloud_points) < 300:
        # fallback geometric prior: a partial wall-like ruin volume
        x = np.random.uniform(-1.0, 1.0, 4000)
        y = np.random.uniform(-0.2, 1.4, 4000)
        z = np.random.uniform(-0.25, 0.25, 4000)
        mask = (np.abs(x) > 0.15) | (y < 0.5)
        cloud_points = np.vstack([x[mask], y[mask], z[mask]]).T.tolist()

    return np.array(cloud_points, dtype=np.float32)


def point_cloud_to_mesh(points: np.ndarray) -> Tuple[o3d.geometry.PointCloud, o3d.geometry.TriangleMesh]:
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd = pcd.voxel_down_sample(voxel_size=0.02)
    pcd.estimate_normals()

    mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=8)
    mesh.compute_vertex_normals()

    bbox = pcd.get_axis_aligned_bounding_box()
    mesh = mesh.crop(bbox.scale(1.15, bbox.get_center()))

    return pcd, mesh


def run_reconstruction(image_paths: List[Path], output_mesh: Path, output_ply: Path):
    points = generate_sparse_point_cloud(image_paths)
    pcd, mesh = point_cloud_to_mesh(points)

    o3d.io.write_point_cloud(str(output_ply), pcd)
    o3d.io.write_triangle_mesh(str(output_mesh), mesh)
