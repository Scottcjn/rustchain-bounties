// Three.js Scene Setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });

renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.setClearColor(0x222222);
document.getElementById('scene-container').appendChild(renderer.domElement);

// Lighting Setup
const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
scene.add(ambientLight);

const mainLight = new THREE.DirectionalLight(0xffffff, 1);
mainLight.position.set(10, 20, 10);
mainLight.castShadow = true;
mainLight.shadow.mapSize.width = 2048;
mainLight.shadow.mapSize.height = 2048;
scene.add(mainLight);

// Spotlight for exhibits
const spotLight = new THREE.SpotLight(0xffffff, 0.8);
spotLight.position.set(0, 15, 0);
spotLight.castShadow = true;
scene.add(spotLight);

// Museum Floor and Walls
const floorGeometry = new THREE.PlaneGeometry(50, 50);
const floorMaterial = new THREE.MeshLambertMaterial({ color: 0x666666 });
const floor = new THREE.Mesh(floorGeometry, floorMaterial);
floor.rotation.x = -Math.PI / 2;
floor.receiveShadow = true;
scene.add(floor);

// Walls
const wallGeometry = new THREE.PlaneGeometry(50, 20);
const wallMaterial = new THREE.MeshLambertMaterial({ color: 0x999999 });

const backWall = new THREE.Mesh(wallGeometry, wallMaterial);
backWall.position.set(0, 10, -25);
scene.add(backWall);

const leftWall = new THREE.Mesh(wallGeometry, wallMaterial);
leftWall.position.set(-25, 10, 0);
leftWall.rotation.y = Math.PI / 2;
scene.add(leftWall);

const rightWall = new THREE.Mesh(wallGeometry, wallMaterial);
rightWall.position.set(25, 10, 0);
rightWall.rotation.y = -Math.PI / 2;
scene.add(rightWall);

// Camera Controls
const controls = {
    forward: false,
    backward: false,
    left: false,
    right: false
};

const moveSpeed = 0.2;
camera.position.set(0, 5, 10);

// Hardware Exhibits Data
const exhibits = [
    {
        name: 'Antminer S9',
        position: { x: -10, y: 1, z: -10 },
        specs: { hashrate: '13.5 TH/s', power: '1323W', efficiency: '98 J/TH' },
        year: 2017
    },
    {
        name: 'Antminer S19 Pro',
        position: { x: 0, y: 1, z: -10 },
        specs: { hashrate: '110 TH/s', power: '3250W', efficiency: '29.5 J/TH' },
        year: 2020
    },
    {
        name: 'Whatsminer M30S++',
        position: { x: 10, y: 1, z: -10 },
        specs: { hashrate: '112 TH/s', power: '3472W', efficiency: '31 J/TH' },
        year: 2020
    },
    {
        name: 'GPU Mining Rig',
        position: { x: -10, y: 1, z: 0 },
        specs: { hashrate: '500 MH/s', power: '1200W', efficiency: 'Variable' },
        year: 2021
    },
    {
        name: 'FPGA Miner',
        position: { x: 10, y: 1, z: 0 },
        specs: { hashrate: '25 TH/s', power: '500W', efficiency: '20 J/TH' },
        year: 2019
    }
];

// Create Hardware Models
const exhibitMeshes = [];
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

function createHardwareModel(exhibit) {
    const group = new THREE.Group();
    
    // Main body
    const bodyGeometry = new THREE.BoxGeometry(3, 1.5, 2);
    const bodyMaterial = new THREE.MeshPhongMaterial({ color: 0x333333 });
    const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
    body.castShadow = true;
    group.add(body);
    
    // Fans
    const fanGeometry = new THREE.CylinderGeometry(0.3, 0.3, 0.1, 16);
    const fanMaterial = new THREE.MeshPhongMaterial({ color: 0x666666 });
    
    for (let i = 0; i < 2; i++) {
        const fan = new THREE.Mesh(fanGeometry, fanMaterial);
        fan.position.set(-1 + i * 2, 0, 1);
        fan.rotation.x = Math.PI / 2;
        group.add(fan);
    }
    
    // LED indicators
    const ledGeometry = new THREE.SphereGeometry(0.1, 8, 8);
    const ledMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x00ff00, 
        emissive: 0x004400 
    });
    
    for (let i = 0; i < 3; i++) {
        const led = new THREE.Mesh(ledGeometry, ledMaterial);
        led.position.set(-0.8 + i * 0.8, 0.8, 1);
        group.add(led);
    }
    
    // Information plaque
    const plaqueGeometry = new THREE.PlaneGeometry(2, 1);
    const plaqueMaterial = new THREE.MeshPhongMaterial({ color: 0xdddddd });
    const plaque = new THREE.Mesh(plaqueGeometry, plaqueMaterial);
    plaque.position.set(0, -1.5, 0);
    plaque.rotation.x = -Math.PI / 2;
    group.add(plaque);
    
    group.position.set(exhibit.position.x, exhibit.position.y, exhibit.position.z);
    group.userData = exhibit;
    
    return group;
}

// Create all exhibits
exhibits.forEach(exhibit => {
    const model = createHardwareModel(exhibit);
    scene.add(model);
    exhibitMeshes.push(model);
});

// API Integration for Live Mining Stats
async function fetchMiningStats() {
    try {
        const response = await fetch('https://api.blockchain.info/stats');
        const data = await response.json();
        return {
            difficulty: data.difficulty,
            hashrate: data.hash_rate,
            totalBlocks: data.n_blocks_total,
            marketPrice: data.market_price_usd
        };
    } catch (error) {
        console.error('Failed to fetch mining stats:', error);
        return null;
    }
}

// Update mining stats display
async function updateMiningStats() {
    const stats = await fetchMiningStats();
    if (stats) {
        document.getElementById('network-hashrate').textContent = 
            `${(stats.hashrate / 1e18).toFixed(2)} EH/s`;
        document.getElementById('difficulty').textContent = 
            stats.difficulty.toLocaleString();
        document.getElementById('total-blocks').textContent = 
            stats.totalBlocks.toLocaleString();
        document.getElementById('btc-price').textContent = 
            `$${stats.marketPrice.toFixed(2)}`;
    }
}

// Mouse interaction
function onMouseClick(event) {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    
    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(exhibitMeshes, true);
    
    if (intersects.length > 0) {
        const clickedExhibit = intersects[0].object.parent;
        const exhibit = clickedExhibit.userData;
        showExhibitInfo(exhibit);
    }
}

function showExhibitInfo(exhibit) {
    const infoPanel = document.getElementById('info-panel');
    const content = `
        <h3>${exhibit.name}</h3>
        <p><strong>Year:</strong> ${exhibit.year}</p>
        <p><strong>Hash Rate:</strong> ${exhibit.specs.hashrate}</p>
        <p><strong>Power Consumption:</strong> ${exhibit.specs.power}</p>
        <p><strong>Efficiency:</strong> ${exhibit.specs.efficiency}</p>
        <p>Click outside to close</p>
    `;
    infoPanel.innerHTML = content;
    infoPanel.style.display = 'block';
}

// Keyboard controls
function onKeyDown(event) {
    switch(event.code) {
        case 'KeyW':
            controls.forward = true;
            break;
        case 'KeyS':
            controls.backward = true;
            break;
        case 'KeyA':
            controls.left = true;
            break;
        case 'KeyD':
            controls.right = true;
            break;
    }
}

function onKeyUp(event) {
    switch(event.code) {
        case 'KeyW':
            controls.forward = false;
            break;
        case 'KeyS':
            controls.backward = false;
            break;
        case 'KeyA':
            controls.left = false;
            break;
        case 'KeyD':
            controls.right = false;
            break;
    }
}

// Camera movement
function updateCameraPosition() {
    const direction = new THREE.Vector3();
    camera.getWorldDirection(direction);
    
    const right = new THREE.Vector3();
    right.crossVectors(camera.up, direction).normalize();
    
    if (controls.forward) {
        camera.position.addScaledVector(direction, -moveSpeed);
    }
    if (controls.backward) {
        camera.position.addScaledVector(direction, moveSpeed);
    }
    if (controls.left) {
        camera.position.addScaledVector(right, moveSpeed);
    }
    if (controls.right) {
        camera.position.addScaledVector(right, -moveSpeed);
    }
    
    // Boundary constraints
    camera.position.x = Math.max(-20, Math.min(20, camera.position.x));
    camera.position.z = Math.max(-20, Math.min(20, camera.position.z));
    camera.position.y = Math.max(2, Math.min(15, camera.position.y));
}

// Mouse look
let mouseX = 0, mouseY = 0;
function onMouseMove(event) {
    if (document.pointerLockElement === renderer.domElement) {
        mouseX += event.movementX * 0.002;
        mouseY += event.movementY * 0.002;
        
        mouseY = Math.max(-Math.PI/2, Math.min(Math.PI/2, mouseY));
        
        camera.rotation.order = 'YXZ';
        camera.rotation.y = -mouseX;
        camera.rotation.x = -mouseY;
    }
}

// Pointer lock for mouse look
renderer.domElement.addEventListener('click', () => {
    renderer.domElement.requestPointerLock();
});

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    
    updateCameraPosition();
    
    // Animate LEDs
    const time = Date.now() * 0.001;
    exhibitMeshes.forEach((mesh, index) => {
        mesh.children.forEach(child => {
            if (child.material && child.material.emissive) {
                const intensity = Math.sin(time * 2 + index) * 0.5 + 0.5;
                child.material.emissive.setHex(0x004400 * intensity);
            }
        });
    });
    
    renderer.render(scene, camera);
}

// Window resize handler
function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

// Hide info panel when clicking outside
function hideInfoPanel() {
    document.getElementById('info-panel').style.display = 'none';
}

// Event listeners
window.addEventListener('resize', onWindowResize);
document.addEventListener('keydown', onKeyDown);
document.addEventListener('keyup', onKeyUp);
renderer.domElement.addEventListener('click', onMouseClick);
renderer.domElement.addEventListener('mousemove', onMouseMove);
document.addEventListener('click', (e) => {
    if (!e.target.closest('#info-panel')) {
        hideInfoPanel();
    }
});

// Initialize
updateMiningStats();
setInterval(updateMiningStats, 60000); // Update every minute
animate();

// Export for potential external use
window.museumApp = {
    scene,
    camera,
    renderer,
    exhibits,
    updateMiningStats
};