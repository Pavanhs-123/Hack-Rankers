import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.164.1/build/three.module.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.164.1/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'https://cdn.jsdelivr.net/npm/three@0.164.1/examples/jsm/loaders/GLTFLoader.js';

const runBtn = document.getElementById('runBtn');
const fileInput = document.getElementById('images');
const statusBox = document.getElementById('status');
const viewer = document.getElementById('viewer');

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x020617);
const camera = new THREE.PerspectiveCamera(60, viewer.clientWidth / viewer.clientHeight, 0.1, 100);
camera.position.set(1.5, 1.2, 2.2);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(viewer.clientWidth, viewer.clientHeight);
viewer.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

scene.add(new THREE.HemisphereLight(0xffffff, 0x444444, 1.2));
const dirLight = new THREE.DirectionalLight(0xffffff, 1.0);
dirLight.position.set(2, 3, 2);
scene.add(dirLight);

const grid = new THREE.GridHelper(5, 12, 0x334155, 0x1e293b);
scene.add(grid);

let currentModel = null;
function loadModel(url) {
  const loader = new GLTFLoader();
  loader.load(url, (gltf) => {
    if (currentModel) scene.remove(currentModel);
    currentModel = gltf.scene;
    scene.add(currentModel);
    statusBox.textContent = 'Done: model loaded.';
  }, undefined, (error) => {
    statusBox.textContent = `Model load failed: ${error}`;
  });
}

async function poll(jobId) {
  while (true) {
    const res = await fetch(`/api/status/${jobId}`);
    const data = await res.json();
    if (data.error) {
      statusBox.textContent = data.error;
      return;
    }

    statusBox.textContent = data.status;

    if (data.done) {
      if (data.error) {
        statusBox.textContent = `Failed: ${data.error}`;
      } else {
        loadModel(data.outputs.glb);
      }
      return;
    }

    await new Promise((resolve) => setTimeout(resolve, 2000));
  }
}

runBtn.onclick = async () => {
  const files = fileInput.files;
  if (!files || files.length < 3) {
    statusBox.textContent = 'Please select at least 3 images.';
    return;
  }

  const formData = new FormData();
  for (const file of files) formData.append('images', file);

  statusBox.textContent = 'Submitting job...';
  const res = await fetch('/api/reconstruct', { method: 'POST', body: formData });
  const data = await res.json();

  if (!res.ok) {
    statusBox.textContent = data.error || 'Request failed.';
    return;
  }

  await poll(data.job_id);
};

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
  camera.aspect = viewer.clientWidth / viewer.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(viewer.clientWidth, viewer.clientHeight);
});
