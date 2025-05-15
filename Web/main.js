import * as THREE from 'three';
import { load } from '@loaders.gl/core';
import { LASLoader } from '@loaders.gl/las';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

let camera, scene, renderer, controls, points;

let profilePoints = [];

async function init() {
  // Scene and camera
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 10000);

  // Renderer
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);

  // Controls
  controls = new OrbitControls(camera, renderer.domElement);


  // DOM event listeners
  renderer.domElement.addEventListener('click', onClick);


  // Load and render LAS file
  await loadLASFile('GK_465_135.las');

  // Fit camera to points
  fitCameraToPointCloud();

  // Handle resize
  window.addEventListener('resize', onWindowResize);

  animate();
}

async function loadLASFile(url) {
  try {
    const data = await load(url, LASLoader);

    // Create geometry
    const geometry = new THREE.BufferGeometry();
    const positions = data.attributes.POSITION.value;
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));

    // Elevation coloring
    const numPoints = positions.length / 3;
    let minZ = Infinity, maxZ = -Infinity;
    for (let i = 0; i < numPoints; i++) {
      const z = positions[3 * i + 2];
      if (z < minZ) minZ = z;
      if (z > maxZ) maxZ = z;
    }

    const colors = new Float32Array(numPoints * 3);
    for (let i = 0; i < numPoints; i++) {
      const z = positions[3 * i + 2];
      // Normalize elevation to [0,1]
      const t = (z - minZ) / (maxZ - minZ);
      // Color: blue (low) -> green (mid) -> red (high)
      const color = new THREE.Color();
      color.setHSL(0.7 - 0.7 * t, 1.0, 0.5); // 0.7=blue, 0.0=red
      colors[3 * i] = color.r;
      colors[3 * i + 1] = color.g;
      colors[3 * i + 2] = color.b;
    }
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    // Material
    const material = new THREE.PointsMaterial({
      size: 0.5,
      vertexColors: true
    });

    // Points
    points = new THREE.Points(geometry, material);
    scene.add(points);
  } catch (error) {
    console.error('Error loading LAS file:', error);
  }
}
function fitCameraToPointCloud() {
  if (!points) return;
  const bbox = new THREE.Box3().setFromObject(points);
  const center = bbox.getCenter(new THREE.Vector3());
  const size = bbox.getSize(new THREE.Vector3());
  camera.position.set(center.x + size.x * 2, center.y + size.y * 2, center.z + size.z * 2);
  camera.lookAt(center);
  controls.target.copy(center);
  controls.update();
}

function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}

function createProfile(start, end) {
  const steps = 100;
  const positions = points.geometry.attributes.position.array;
  const numPoints = positions.length / 3;

  console.log('--- Creating profile ---');
  console.log('Start point:', start);
  console.log('End point:', end);
  console.log('Number of steps:', steps);
  console.log('Number of points in cloud:', numPoints);

  // Remove previous profile markers if any
  if (window.profileMarkers) {
    window.profileMarkers.forEach(marker => scene.remove(marker));
  }
  window.profileMarkers = [];

  const profile = [];
  let minProfileZ = Infinity, maxProfileZ = -Infinity;

  for (let i = 0; i <= steps; i++) {
    const t = i / steps;
    const x = start.x + (end.x - start.x) * t;
    const y = start.y + (end.y - start.y) * t;

    // Find the closest point in the cloud to (x, y)
    let minDist = Infinity;
    let z = 0;
    let closestPoint = null;
    for (let j = 0; j < numPoints; j++) {
      const px = positions[3 * j];
      const py = positions[3 * j + 1];
      const pz = positions[3 * j + 2];
      const dist = Math.hypot(px - x, py - y);
      if (dist < minDist) {
        minDist = dist;
        z = pz;
        closestPoint = { x: px, y: py, z: pz };
      }
    }
    if (z < minProfileZ) minProfileZ = z;
    if (z > maxProfileZ) maxProfileZ = z;
    profile.push({ dist: t * start.distanceTo(end), z });

    // Log every 10th step
    if (i % 10 === 0) {
      console.log(`Step ${i}: x=${x.toFixed(2)}, y=${y.toFixed(2)}, z=${z.toFixed(2)}, dist=${profile[profile.length-1].dist.toFixed(2)}`);
    }

    // Highlight the considered profile point as a large white sphere
    if (closestPoint) {
      const marker = new THREE.Mesh(
        new THREE.SphereGeometry(2, 16, 16), // Larger sphere
        new THREE.MeshBasicMaterial({ color: 0xffffff }) // white
      );
      marker.position.set(closestPoint.x, closestPoint.y, closestPoint.z);
      scene.add(marker);
      window.profileMarkers.push(marker);
    }
  }

  console.log('Profile min elevation:', minProfileZ);
  console.log('Profile max elevation:', maxProfileZ);
  console.log('Profile array:', profile);

  // Plot with Plotly
  Plotly.newPlot('profile', [{
    x: profile.map(p => p.dist),
    y: profile.map(p => p.z),
    mode: 'lines+markers',
    line: { color: '#2196F3' }
  }], {
    title: 'Terrain Profile',
    xaxis: { title: 'Distance' },
    yaxis: { title: 'Elevation (z)' },
    margin: { t: 40, l: 50, r: 20, b: 40 }
  });
}

function onClick(event) {
  // Get mouse position normalized to [-1, 1]
  const mouse = new THREE.Vector2(
    (event.clientX / renderer.domElement.clientWidth) * 2 - 1,
    -(event.clientY / renderer.domElement.clientHeight) * 2 + 1
  );

  const raycaster = new THREE.Raycaster();
  raycaster.setFromCamera(mouse, camera);

  const intersects = raycaster.intersectObject(points);
  if (intersects.length > 0) {
    profilePoints.push(intersects[0].point.clone());

    // Log the selected point
    console.log(`Selected point ${profilePoints.length}:`, intersects[0].point);

    // Highlight chosen point as a large purple sphere
    const marker = new THREE.Mesh(
      new THREE.SphereGeometry(3, 24, 24), // Even larger sphere
      new THREE.MeshBasicMaterial({ color: 0x800080 }) // purple
    );
    marker.position.copy(intersects[0].point);
    scene.add(marker);

    if (profilePoints.length === 2) {
      console.log('Two points selected, generating profile...');
      createProfile(profilePoints[0], profilePoints[1]);
      profilePoints = [];
    }
  }
}

init();
