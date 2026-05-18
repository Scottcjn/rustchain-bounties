import * as THREE from "three";

const API_URL = "https://explorer.rustchain.org/api/miners";
const ACTIVE_WINDOW_SECONDS = 300;

const exhibits = [
  {
    id: "powerbook-g4",
    title: "PowerBook G4 Collection",
    summary: "Portable PowerPC machines representing the highest-antiquity laptop story.",
    multiplier: "2.5x target",
    keywords: ["powerbook", "powerbook g4", "powerbook_g4"],
    position: [-10, 0, -8],
    accent: 0xe2e8f0,
    build: "laptop",
  },
  {
    id: "powermac-g4-g5",
    title: "Power Mac G4 MDD + G5 Dual",
    summary: "Tower-era Apple hardware with a visible repair-and-reuse path.",
    multiplier: "2.0x target",
    keywords: ["power mac", "powermac", "g4 mdd", "g5 dual", "powermac_g4", "powermac_g5"],
    position: [-5, 0, -11],
    accent: 0xb8c2cc,
    build: "tower",
  },
  {
    id: "power8-s824",
    title: "IBM POWER8 S824",
    summary: "Centerpiece enterprise system: 128 threads, 512GB RAM, active RustChain proof anchor.",
    multiplier: "2.0x live",
    keywords: ["power8", "s824", "sophia"],
    position: [0, 0, -7],
    accent: 0x2f3d4d,
    build: "rack",
  },
  {
    id: "dell-c4130",
    title: "Dell C4130 GPU Cluster",
    summary: "Dense accelerator hardware for modern compute comparison inside the antiquity museum.",
    multiplier: "modern cluster",
    keywords: ["dell", "gpu", "c4130"],
    position: [5, 0, -11],
    accent: 0x4b5563,
    build: "cluster",
  },
  {
    id: "retro-lab",
    title: "486/386 Laptops + SPARCstations",
    summary: "Early-era machines grouped as the long-tail proof collection.",
    multiplier: "deep vintage",
    keywords: ["486", "386", "sparc", "retro"],
    position: [10, 0, -8],
    accent: 0xd6d3d1,
    build: "shelf",
  },
];

const sceneRoot = document.querySelector("#sceneRoot");
const enterBtn = document.querySelector("#enterBtn");
const apiStatus = document.querySelector("#apiStatus");
const selectedLabel = document.querySelector("#selectedLabel");
const minerTotal = document.querySelector("#minerTotal");
const activeTotal = document.querySelector("#activeTotal");
const vintageTotal = document.querySelector("#vintageTotal");
const detailPanel = document.querySelector("#detailPanel");
const detailKicker = document.querySelector("#detailKicker");
const detailTitle = document.querySelector("#detailTitle");
const detailSummary = document.querySelector("#detailSummary");
const detailStats = document.querySelector("#detailStats");
const closePanel = document.querySelector("#closePanel");

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x080b10);
scene.fog = new THREE.Fog(0x080b10, 16, 54);

const camera = new THREE.PerspectiveCamera(64, window.innerWidth / window.innerHeight, 0.1, 120);
camera.position.set(0, 2.2, 8);
camera.rotation.order = "YXZ";

const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.domElement.tabIndex = 0;
sceneRoot.appendChild(renderer.domElement);

const clock = new THREE.Clock();
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
const keys = new Set();
const touchMoves = new Set();
const exhibitGroups = new Map();
const interactables = [];
let yaw = 0;
let pitch = -0.04;
let dragging = false;
let lastPointer = { x: 0, y: 0 };
let pointerTravel = 0;
let minerData = [];
let selectedExhibit = null;

setupLighting();
buildMuseum();
bindEvents();
loadMinerData();
setInterval(loadMinerData, 30000);
renderer.setAnimationLoop(animate);

function setupLighting() {
  scene.add(new THREE.HemisphereLight(0xaecfff, 0x1f2933, 0.72));

  const key = new THREE.DirectionalLight(0xffffff, 1.6);
  key.position.set(-8, 14, 8);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  scene.add(key);

  [
    [-12, 5, -10, 0xe3b34f],
    [0, 6, -6, 0x73a7ff],
    [12, 5, -10, 0x32d17d],
  ].forEach(([x, y, z, color]) => {
    const light = new THREE.PointLight(color, 1.2, 18);
    light.position.set(x, y, z);
    scene.add(light);
  });
}

function buildMuseum() {
  const floor = new THREE.Mesh(
    new THREE.PlaneGeometry(34, 30),
    new THREE.MeshStandardMaterial({ color: 0x111821, roughness: 0.86, metalness: 0.08 })
  );
  floor.rotation.x = -Math.PI / 2;
  floor.receiveShadow = true;
  scene.add(floor);

  const backWall = new THREE.Mesh(
    new THREE.BoxGeometry(36, 8, 0.4),
    new THREE.MeshStandardMaterial({ color: 0x151d27, roughness: 0.72 })
  );
  backWall.position.set(0, 4, -15);
  backWall.receiveShadow = true;
  scene.add(backWall);

  for (let x = -15; x <= 15; x += 5) {
    const guide = new THREE.Mesh(
      new THREE.BoxGeometry(0.035, 0.03, 25),
      new THREE.MeshBasicMaterial({ color: 0x2b3a48 })
    );
    guide.position.set(x, 0.015, -4);
    scene.add(guide);
  }

  exhibits.forEach((exhibit) => buildExhibit(exhibit));
}

function buildExhibit(exhibit) {
  const group = new THREE.Group();
  group.position.set(...exhibit.position);
  group.userData.exhibit = exhibit;

  const pedestal = new THREE.Mesh(
    new THREE.BoxGeometry(3.2, 0.72, 2.4),
    new THREE.MeshStandardMaterial({ color: 0x202a34, roughness: 0.62, metalness: 0.2 })
  );
  pedestal.position.y = 0.36;
  pedestal.castShadow = true;
  pedestal.receiveShadow = true;
  group.add(pedestal);

  const ring = new THREE.Mesh(
    new THREE.TorusGeometry(1.78, 0.025, 10, 96),
    new THREE.MeshBasicMaterial({ color: 0x334155 })
  );
  ring.rotation.x = Math.PI / 2;
  ring.position.y = 0.76;
  group.add(ring);
  group.userData.statusRing = ring;

  const glow = new THREE.PointLight(0x32d17d, 0, 5);
  glow.position.set(0, 2.1, 0);
  group.add(glow);
  group.userData.glow = glow;

  const model = buildMachineModel(exhibit);
  model.position.y = 1.05;
  group.add(model);

  const label = makeLabel(exhibit.title, exhibit.multiplier);
  label.position.set(0, 2.75, 0.2);
  group.add(label);

  group.traverse((node) => {
    if (node.isMesh) {
      node.castShadow = true;
      node.userData.exhibitId = exhibit.id;
      interactables.push(node);
    }
  });

  scene.add(group);
  exhibitGroups.set(exhibit.id, group);
}

function buildMachineModel(exhibit) {
  const group = new THREE.Group();
  const material = new THREE.MeshStandardMaterial({
    color: exhibit.accent,
    roughness: 0.38,
    metalness: 0.42,
  });
  const dark = new THREE.MeshStandardMaterial({ color: 0x0c1118, roughness: 0.5, metalness: 0.28 });
  const glass = new THREE.MeshStandardMaterial({ color: 0x15263a, roughness: 0.2, metalness: 0.1, emissive: 0x031326 });

  if (exhibit.build === "laptop") {
    addBox(group, [1.8, 0.12, 1.1], [0, 0.1, 0], material);
    addBox(group, [1.8, 1.05, 0.1], [0, 0.72, -0.54], material);
    addBox(group, [1.55, 0.8, 0.04], [0, 0.72, -0.6], glass);
  } else if (exhibit.build === "tower") {
    addBox(group, [0.82, 1.85, 1.2], [-0.42, 0.92, 0], material);
    addBox(group, [0.82, 1.85, 1.2], [0.52, 0.92, 0], material);
    addVentStack(group, 0.52, 1.1);
  } else if (exhibit.build === "rack") {
    addBox(group, [2.35, 2.6, 1.35], [0, 1.3, 0], dark);
    for (let row = 0; row < 6; row += 1) {
      addBox(group, [1.88, 0.08, 0.05], [0, 0.38 + row * 0.36, 0.7], glass);
    }
  } else if (exhibit.build === "cluster") {
    addBox(group, [2.35, 0.62, 1.45], [0, 0.54, 0], dark);
    for (let slot = -3; slot <= 3; slot += 1) {
      addBox(group, [0.18, 0.38, 1.2], [slot * 0.28, 0.62, 0], material);
    }
  } else {
    addBox(group, [2.45, 1.6, 0.32], [0, 0.8, -0.35], dark);
    [-0.8, 0, 0.8].forEach((x, index) => {
      addBox(group, [0.62, 0.18, 0.72], [x, 0.42 + index * 0.35, 0.12], material);
    });
  }

  return group;
}

function addBox(group, size, position, material) {
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(...size), material);
  mesh.position.set(...position);
  group.add(mesh);
  return mesh;
}

function addVentStack(group, x, y) {
  const ventMaterial = new THREE.MeshBasicMaterial({ color: 0x111827 });
  for (let i = 0; i < 5; i += 1) {
    const vent = new THREE.Mesh(new THREE.BoxGeometry(0.48, 0.035, 0.03), ventMaterial);
    vent.position.set(x, y + i * 0.12, 0.62);
    group.add(vent);
  }
}

function makeLabel(title, subtitle) {
  const canvas = document.createElement("canvas");
  canvas.width = 768;
  canvas.height = 320;
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "rgba(9, 11, 16, 0.78)";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.strokeStyle = "rgba(227, 179, 79, 0.82)";
  ctx.lineWidth = 8;
  ctx.strokeRect(8, 8, canvas.width - 16, canvas.height - 16);
  ctx.fillStyle = "#eef5f8";
  ctx.font = "700 44px Arial";
  ctx.textAlign = "center";
  wrapCanvasText(ctx, title, canvas.width / 2, 112, 640, 48);
  ctx.fillStyle = "#e3b34f";
  ctx.font = "700 32px Arial";
  ctx.fillText(subtitle, canvas.width / 2, 240);

  const texture = new THREE.CanvasTexture(canvas);
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: texture, transparent: true }));
  sprite.scale.set(3.1, 1.28, 1);
  return sprite;
}

function wrapCanvasText(ctx, text, x, y, maxWidth, lineHeight) {
  const words = text.split(" ");
  let line = "";
  let currentY = y;
  words.forEach((word) => {
    const test = `${line}${word} `;
    if (ctx.measureText(test).width > maxWidth && line) {
      ctx.fillText(line.trim(), x, currentY);
      line = `${word} `;
      currentY += lineHeight;
    } else {
      line = test;
    }
  });
  ctx.fillText(line.trim(), x, currentY);
}

function bindEvents() {
  window.addEventListener("resize", onResize);
  window.addEventListener("keydown", (event) => keys.add(event.code));
  window.addEventListener("keyup", (event) => keys.delete(event.code));

  enterBtn.addEventListener("click", () => renderer.domElement.focus());
  closePanel.addEventListener("click", () => {
    selectedExhibit = null;
    selectedLabel.textContent = "No exhibit selected";
    detailPanel.classList.remove("active");
  });

  renderer.domElement.addEventListener("pointerdown", (event) => {
    dragging = true;
    lastPointer = { x: event.clientX, y: event.clientY };
    pointerTravel = 0;
    renderer.domElement.setPointerCapture(event.pointerId);
  });
  renderer.domElement.addEventListener("pointermove", (event) => {
    if (!dragging) return;
    const dx = event.clientX - lastPointer.x;
    const dy = event.clientY - lastPointer.y;
    pointerTravel += Math.abs(dx) + Math.abs(dy);
    yaw -= dx * 0.004;
    pitch = THREE.MathUtils.clamp(pitch - dy * 0.003, -1.2, 1.1);
    lastPointer = { x: event.clientX, y: event.clientY };
  });
  renderer.domElement.addEventListener("pointerup", (event) => {
    dragging = false;
    if (pointerTravel < 7) selectFromPointer(event);
  });

  document.querySelectorAll("[data-move]").forEach((button) => {
    const move = button.dataset.move;
    button.addEventListener("pointerdown", () => touchMoves.add(move));
    button.addEventListener("pointerup", () => touchMoves.delete(move));
    button.addEventListener("pointerleave", () => touchMoves.delete(move));
  });
}

async function loadMinerData() {
  apiStatus.className = "status-pill pending";
  apiStatus.textContent = "Loading API";
  try {
    const response = await fetch(API_URL, { cache: "no-store" });
    if (!response.ok) throw new Error(`API ${response.status}`);
    const payload = await response.json();
    minerData = Array.isArray(payload) ? payload : payload.miners || [];
    apiStatus.className = "status-pill live";
    apiStatus.textContent = "Live API";
  } catch (error) {
    minerData = [];
    apiStatus.className = "status-pill warn";
    apiStatus.textContent = error.message;
  }
  updateExhibitStatus();
}

function updateExhibitStatus() {
  const active = minerData.filter(isActiveMiner);
  const vintage = minerData.filter((miner) => Number(miner.antiquity_multiplier || 0) > 1.2);
  minerTotal.textContent = minerData.length;
  activeTotal.textContent = active.length;
  vintageTotal.textContent = vintage.length;

  exhibits.forEach((exhibit) => {
    const group = exhibitGroups.get(exhibit.id);
    const match = findMinerForExhibit(exhibit);
    const activeMatch = match && isActiveMiner(match);
    group.userData.miner = match || null;
    group.userData.glow.intensity = activeMatch ? 1.8 : 0.18;
    group.userData.statusRing.material.color.set(activeMatch ? 0x32d17d : 0x52606d);
  });

  if (selectedExhibit) showDetails(selectedExhibit);
}

function findMinerForExhibit(exhibit) {
  const scored = minerData
    .map((miner) => ({ miner, score: scoreMiner(exhibit, miner) }))
    .filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score || Number(b.miner.last_attest || 0) - Number(a.miner.last_attest || 0));
  return scored[0]?.miner || null;
}

function scoreMiner(exhibit, miner) {
  const text = [
    miner.miner,
    miner.device_arch,
    miner.device_family,
    miner.hardware_type,
  ].join(" ").toLowerCase();

  if (exhibit.id === "powerbook-g4" || exhibit.id === "powermac-g4-g5") {
    const isPower8 = text.includes("power8") || text.includes("s824");
    if (isPower8) return 0;
  }

  return exhibit.keywords.reduce((score, keyword) => score + (text.includes(keyword) ? 1 : 0), 0);
}

function isActiveMiner(miner) {
  const last = Number(miner.last_attest || 0);
  if (!last) return false;
  return Math.max(0, Date.now() / 1000 - last) <= ACTIVE_WINDOW_SECONDS;
}

function selectFromPointer(event) {
  const rect = renderer.domElement.getBoundingClientRect();
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  const hit = raycaster.intersectObjects(interactables, false)[0];
  if (!hit) return;

  const exhibit = exhibits.find((item) => item.id === hit.object.userData.exhibitId);
  if (exhibit) showDetails(exhibit);
}

function showDetails(exhibit) {
  selectedExhibit = exhibit;
  const group = exhibitGroups.get(exhibit.id);
  const miner = group?.userData.miner;
  const status = miner ? (isActiveMiner(miner) ? "Active" : "Stale") : "No direct match";
  selectedLabel.textContent = exhibit.title;
  detailPanel.classList.add("active");
  detailKicker.textContent = status;
  detailTitle.textContent = exhibit.title;
  detailSummary.textContent = exhibit.summary;
  detailStats.innerHTML = renderStats([
    ["Target multiplier", exhibit.multiplier],
    ["Matched miner", miner?.miner || "No live miner mapped"],
    ["Hardware", miner?.hardware_type || "Exhibit model"],
    ["Architecture", miner?.device_arch || "Museum data"],
    ["Last attest", miner ? relativeTime(miner.last_attest) : "Not available"],
    ["API status", apiStatus.textContent],
  ]);
}

function renderStats(rows) {
  return rows.map(([label, value]) => `
    <div>
      <dt>${escapeHtml(label)}</dt>
      <dd>${escapeHtml(value)}</dd>
    </div>
  `).join("");
}

function relativeTime(seconds) {
  const value = Number(seconds || 0);
  if (!value) return "unknown";
  const diffSeconds = Math.round((value * 1000 - Date.now()) / 1000);
  const abs = Math.abs(diffSeconds);
  const units = [
    ["day", 86400],
    ["hour", 3600],
    ["minute", 60],
    ["second", 1],
  ];
  const [unit, size] = units.find(([, unitSeconds]) => abs >= unitSeconds) || units[3];
  return new Intl.RelativeTimeFormat("en", { numeric: "auto" }).format(Math.round(diffSeconds / size), unit);
}

function onResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

function animate() {
  const delta = Math.min(clock.getDelta(), 0.04);
  updateCamera(delta);
  const elapsed = clock.elapsedTime;
  exhibitGroups.forEach((group) => {
    const active = group.userData.glow.intensity > 1;
    group.userData.glow.intensity = active ? 1.5 + Math.sin(elapsed * 3) * 0.55 : 0.18;
    group.userData.statusRing.rotation.z += delta * 0.35;
  });
  renderer.render(scene, camera);
}

function updateCamera(delta) {
  const speed = keys.has("ShiftLeft") || keys.has("ShiftRight") ? 8 : 4.2;
  const forward = new THREE.Vector3(Math.sin(yaw), 0, Math.cos(yaw) * -1);
  const right = new THREE.Vector3(Math.cos(yaw), 0, Math.sin(yaw));
  const movement = new THREE.Vector3();

  if (keys.has("KeyW") || keys.has("ArrowUp") || touchMoves.has("forward")) movement.add(forward);
  if (keys.has("KeyS") || keys.has("ArrowDown") || touchMoves.has("back")) movement.sub(forward);
  if (keys.has("KeyD") || keys.has("ArrowRight") || touchMoves.has("right")) movement.add(right);
  if (keys.has("KeyA") || keys.has("ArrowLeft") || touchMoves.has("left")) movement.sub(right);

  if (movement.lengthSq() > 0) {
    movement.normalize().multiplyScalar(speed * delta);
    camera.position.add(movement);
    camera.position.x = THREE.MathUtils.clamp(camera.position.x, -16, 16);
    camera.position.z = THREE.MathUtils.clamp(camera.position.z, -14, 11);
  }

  camera.rotation.y = yaw;
  camera.rotation.x = pitch;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
