class Museum3D {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        this.exhibits = [];
        this.minerStats = {};
        this.keys = {};
        this.moveSpeed = 5.0;
        this.clock = new THREE.Clock();
        
        this.init();
        this.setupEventListeners();
        this.animate();
    }

    init() {
        // Scene setup
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x1a1a1a);
        this.scene.fog = new THREE.Fog(0x1a1a1a, 50, 200);

        // Camera setup
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.camera.position.set(0, 5, 10);

        // Renderer setup
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.setPixelRatio(window.devicePixelRatio);
        document.getElementById('museum-container').appendChild(this.renderer.domElement);

        // Lighting
        this.setupLighting();
        
        // Museum environment
        this.createMuseumEnvironment();
        
        // Load exhibits
        this.loadExhibits();
        
        // Load miner stats
        this.loadMinerStats();
    }

    setupLighting() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404040, 0.3);
        this.scene.add(ambientLight);

        // Main directional light
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 20, 10);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        directionalLight.shadow.camera.near = 0.5;
        directionalLight.shadow.camera.far = 500;
        directionalLight.shadow.camera.left = -50;
        directionalLight.shadow.camera.right = 50;
        directionalLight.shadow.camera.top = 50;
        directionalLight.shadow.camera.bottom = -50;
        this.scene.add(directionalLight);

        // Spotlights for exhibits
        const spotlight1 = new THREE.SpotLight(0xffffff, 1, 30, Math.PI / 6, 0.3, 2);
        spotlight1.position.set(-15, 15, 0);
        spotlight1.target.position.set(-15, 0, 0);
        spotlight1.castShadow = true;
        this.scene.add(spotlight1);
        this.scene.add(spotlight1.target);

        const spotlight2 = new THREE.SpotLight(0xffffff, 1, 30, Math.PI / 6, 0.3, 2);
        spotlight2.position.set(15, 15, 0);
        spotlight2.target.position.set(15, 0, 0);
        spotlight2.castShadow = true;
        this.scene.add(spotlight2);
        this.scene.add(spotlight2.target);

        const spotlight3 = new THREE.SpotLight(0xffffff, 1, 30, Math.PI / 6, 0.3, 2);
        spotlight3.position.set(0, 15, -15);
        spotlight3.target.position.set(0, 0, -15);
        spotlight3.castShadow = true;
        this.scene.add(spotlight3);
        this.scene.add(spotlight3.target);
    }

    createMuseumEnvironment() {
        // Floor
        const floorGeometry = new THREE.PlaneGeometry(100, 100);
        const floorMaterial = new THREE.MeshLambertMaterial({ 
            color: 0x444444,
            transparent: true,
            opacity: 0.8
        });
        const floor = new THREE.Mesh(floorGeometry, floorMaterial);
        floor.rotation.x = -Math.PI / 2;
        floor.receiveShadow = true;
        this.scene.add(floor);

        // Walls
        const wallMaterial = new THREE.MeshLambertMaterial({ color: 0x333333 });
        
        // Back wall
        const backWallGeometry = new THREE.PlaneGeometry(100, 30);
        const backWall = new THREE.Mesh(backWallGeometry, wallMaterial);
        backWall.position.z = -50;
        backWall.position.y = 15;
        this.scene.add(backWall);

        // Side walls
        const sideWallGeometry = new THREE.PlaneGeometry(100, 30);
        const leftWall = new THREE.Mesh(sideWallGeometry, wallMaterial);
        leftWall.rotation.y = Math.PI / 2;
        leftWall.position.x = -50;
        leftWall.position.y = 15;
        this.scene.add(leftWall);

        const rightWall = new THREE.Mesh(sideWallGeometry, wallMaterial);
        rightWall.rotation.y = -Math.PI / 2;
        rightWall.position.x = 50;
        rightWall.position.y = 15;
        this.scene.add(rightWall);

        // Ceiling
        const ceilingGeometry = new THREE.PlaneGeometry(100, 100);
        const ceilingMaterial = new THREE.MeshLambertMaterial({ color: 0x222222 });
        const ceiling = new THREE.Mesh(ceilingGeometry, ceilingMaterial);
        ceiling.rotation.x = Math.PI / 2;
        ceiling.position.y = 30;
        this.scene.add(ceiling);

        // Display pedestals
        this.createPedestals();
    }

    createPedestals() {
        const pedestalGeometry = new THREE.CylinderGeometry(3, 3, 2, 16);
        const pedestalMaterial = new THREE.MeshPhongMaterial({ color: 0x666666 });

        const positions = [
            { x: -15, z: 0 },
            { x: 15, z: 0 },
            { x: 0, z: -15 },
            { x: -15, z: -30 },
            { x: 15, z: -30 }
        ];

        positions.forEach(pos => {
            const pedestal = new THREE.Mesh(pedestalGeometry, pedestalMaterial);
            pedestal.position.set(pos.x, 1, pos.z);
            pedestal.castShadow = true;
            pedestal.receiveShadow = true;
            this.scene.add(pedestal);
        });
    }

    loadExhibits() {
        const exhibits = [
            {
                name: 'Antminer S9',
                position: { x: -15, y: 3, z: 0 },
                model: 'antminer_s9',
                description: 'Bitcoin mining ASIC from 2016',
                specs: {
                    hashrate: '13.5 TH/s',
                    power: '1372W',
                    algorithm: 'SHA-256'
                }
            },
            {
                name: 'Antminer L3+',
                position: { x: 15, y: 3, z: 0 },
                model: 'antminer_l3',
                description: 'Litecoin mining ASIC from 2017',
                specs: {
                    hashrate: '504 MH/s',
                    power: '800W',
                    algorithm: 'Scrypt'
                }
            },
            {
                name: 'GPU Mining Rig',
                position: { x: 0, y: 3, z: -15 },
                model: 'gpu_rig',
                description: '6x GTX 1080 Ti Mining Rig',
                specs: {
                    hashrate: '420 MH/s (ETH)',
                    power: '1800W',
                    algorithm: 'Ethash'
                }
            },
            {
                name: 'Avalon 6',
                position: { x: -15, y: 3, z: -30 },
                model: 'avalon_6',
                description: 'Bitcoin mining ASIC from 2015',
                specs: {
                    hashrate: '3.5 TH/s',
                    power: '1100W',
                    algorithm: 'SHA-256'
                }
            },
            {
                name: 'WhatsMiner M3',
                position: { x: 15, y: 3, z: -30 },
                model: 'whatsminer_m3',
                description: 'Bitcoin mining ASIC from 2017',
                specs: {
                    hashrate: '11.5 TH/s',
                    power: '2000W',
                    algorithm: 'SHA-256'
                }
            }
        ];

        exhibits.forEach(exhibit => {
            this.createExhibit(exhibit);
        });
    }

    createExhibit(exhibitData) {
        const group = new THREE.Group();
        group.position.set(exhibitData.position.x, exhibitData.position.y, exhibitData.position.z);
        group.userData = exhibitData;

        // Create simplified miner models
        let minerGeometry, minerMaterial;

        switch (exhibitData.model) {
            case 'antminer_s9':
                minerGeometry = new THREE.BoxGeometry(4, 2, 2);
                minerMaterial = new THREE.MeshPhongMaterial({ color: 0x333333 });
                break;
            case 'antminer_l3':
                minerGeometry = new THREE.BoxGeometry(3.5, 1.8, 1.8);
                minerMaterial = new THREE.MeshPhongMaterial({ color: 0x2c5aa0 });
                break;
            case 'gpu_rig':
                minerGeometry = new THREE.BoxGeometry(6, 3, 2.5);
                minerMaterial = new THREE.MeshPhongMaterial({ color: 0x1a5f1a });
                break;
            case 'avalon_6':
                minerGeometry = new THREE.BoxGeometry(3.8, 2.2, 2.2);
                minerMaterial = new THREE.MeshPhongMaterial({ color: 0x4d4d4d });
                break;
            case 'whatsminer_m3':
                minerGeometry = new THREE.BoxGeometry(4.2, 2.5, 2.5);
                minerMaterial = new THREE.MeshPhongMaterial({ color: 0x800080 });
                break;
            default:
                minerGeometry = new THREE.BoxGeometry(4, 2, 2);
                minerMaterial = new THREE.MeshPhongMaterial({ color: 0x666666 });
        }

        const minerMesh = new THREE.Mesh(minerGeometry, minerMaterial);
        minerMesh.castShadow = true;
        minerMesh.receiveShadow = true;

        // Add fans
        const fanGeometry = new THREE.CircleGeometry(0.3, 8);
        const fanMaterial = new THREE.MeshPhongMaterial({ color: 0x000000 });
        
        for (let i = 0; i < 2; i++) {
            const fan = new THREE.Mesh(fanGeometry, fanMaterial);
            fan.position.set(-1.5 + i * 3, 0, 1.01);
            minerMesh.add(fan);
        }

        // Add LED indicators
        const ledGeometry = new THREE.SphereGeometry(0.1, 8, 6);
        const ledMaterial = new THREE.MeshPhongMaterial({ 
            color: 0x00ff00,
            emissive: 0x002200
        });
        
        const led = new THREE.Mesh(ledGeometry, ledMaterial);
        led.position.set(1.5, 0.5, 1.01);
        minerMesh.add(led);

        group.add(minerMesh);

        // Add info plaque
        const plaqueGeometry = new THREE.PlaneGeometry(2, 1);
        const canvas = document.createElement('canvas');
        canvas.width = 256;
        canvas.height = 128;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#000000';
        ctx.fillRect(0, 0, 256, 128);
        ctx.fillStyle = '#ffffff';
        ctx.font = '16px Arial';
        ctx.fillText(exhibitData.name, 10, 25);
        ctx.font = '12px Arial';
        ctx.fillText(`Hashrate: ${exhibitData.specs.hashrate}`, 10, 50);
        ctx.fillText(`Power: ${exhibitData.specs.power}`, 10, 70);
        ctx.fillText(`Algorithm: ${exhibitData.specs.algorithm}`, 10, 90);

        const plaqueTexture = new THREE.CanvasTexture(canvas);
        const plaqueMaterial = new THREE.MeshBasicMaterial({ map: plaqueTexture });
        const plaque = new THREE.Mesh(plaqueGeometry, plaqueMaterial);
        plaque.position.set(0, -2, 2);
        group.add(plaque);

        this.scene.add(group);
        this.exhibits.push(group);
    }

    setupEventListeners() {
        // Keyboard controls
        document.addEventListener('keydown', (event) => {
            this.keys[event.code] = true;
        });

        document.addEventListener('keyup', (event) => {
            this.keys[event.code] = false;
        });

        // Mouse controls
        document.addEventListener('mousemove', (event) => {
            this.mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            this.mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
        });

        document.addEventListener('click', (event) => {
            this.handleClick();
        });

        // Window resize
        window.addEventListener('resize', () => {
            this.camera.aspect = window.innerWidth / window.innerHeight;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(window.innerWidth, window.innerHeight);
        });
    }

    handleMovement() {
        const delta = this.clock.getDelta();
        const moveDistance = this.moveSpeed * delta;

        const direction = new THREE.Vector3();
        this.camera.getWorldDirection(direction);
        direction.y = 0;
        direction.normalize();

        const right = new THREE.Vector3();
        right.crossVectors(direction, this.camera.up).normalize();

        if (this.keys['KeyW']) {
            this.camera.position.addScaledVector(direction, moveDistance);
        }
        if (this.keys['KeyS']) {
            this.camera.position.addScaledVector(direction, -moveDistance);
        }
        if (this.keys['KeyA']) {
            this.camera.position.addScaledVector(right, -moveDistance);
        }
        if (this.keys['KeyD']) {
            this.camera.position.addScaledVector(right, moveDistance);
        }

        // Mouse look
        if (document.pointerLockElement === this.renderer.domElement) {
            const euler = new THREE.Euler(0, 0, 0, 'YXZ');
            euler.setFromQuaternion(this.camera.quaternion);
            euler.y -= this.mouse.x * 0.002;
            euler.x -= this.mouse.y * 0.002;
            euler.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, euler.x));
            this.camera.quaternion.setFromEuler(euler);
        }
    }

    handleClick() {
        this.raycaster.setFromCamera(this.mouse, this.camera);
        const intersects = this.raycaster.intersectObjects(this.exhibits, true);

        if (intersects.length > 0) {
            let exhibit = intersects[0].object;
            while (exhibit.parent && !exhibit.userData.name) {
                exhibit = exhibit.parent;
            }
            
            if (exhibit.userData.name) {
                this.showExhibitInfo(exhibit.userData);
            }
        } else {
            // Request pointer lock for mouse look
            this.renderer.domElement.requestPointerLock();
        }
    }

    showExhibitInfo(exhibitData) {
        const infoPanel = document.getElementById('info-panel');
        const content = `
            <h3>${exhibitData.name}</h3>
            <p>${exhibitData.description}</p>
            <ul>
                <li><strong>Hashrate:</strong> ${exhibitData.specs.hashrate}</li>
                <li><strong>Power Consumption:</strong> ${exhibitData.specs.power}</li>
                <li><strong>Algorithm:</strong> ${exhibitData.specs.algorithm}</li>
            </ul>
            ${this.minerStats[exhibitData.name] ? 
                `<div class="stats">
                    <h4>Current Network Stats:</h4>
                    <p>Network Hashrate: ${this.minerStats[exhibitData.name].networkHashrate}</p>
                    <p>Difficulty: ${this.minerStats[exhibitData.name].difficulty}</p>
                    <p>Block Reward: ${this.minerStats[exhibitData.name].blockReward}</p>
                </div>` : ''
            }
            <button onclick="museum.hideExhibitInfo()">Close</button>
        `;
        infoPanel.innerHTML = content;
        infoPanel.classList.add('active');
    }

    hideExhibitInfo() {
        const infoPanel = document.getElementById('info-panel');
        infoPanel.classList.remove('active');
    }

    async loadMinerStats() {
        try {
            // Simulate API calls for different cryptocurrencies
            const bitcoinStats = await this.fetchCryptoStats('bitcoin');
            const litecoinStats = await this.fetchCryptoStats('litecoin');
            const ethereumStats = await this.fetchCryptoStats('ethereum');

            this.minerStats = {
                'Antminer S9': bitcoinStats,
                'Avalon 6': bitcoinStats,
                'WhatsMiner M3': bitcoinStats,
                'Antminer L3+': litecoinStats,
                'GPU Mining Rig': ethereumStats
            };
        } catch (error) {
            console.log('Failed to load miner stats:', error);
        }
    }

    async fetchCryptoStats(crypto) {
        // Simulate API response
        return new Promise((resolve) => {
            setTimeout(() => {
                const mockStats = {
                    bitcoin: {
                        networkHashrate: '150 EH/s',
                        difficulty: '25.05 T',
                        blockReward: '6.25 BTC'
                    },
                    litecoin: {
                        networkHashrate: '350 TH/s',
                        difficulty: '18.2 M',
                        blockReward: '12.5 LTC'
                    },
                    ethereum: {
                        networkHashrate: '900 TH/s',
                        difficulty: '12.5 P',
                        blockReward: '2 ETH'
                    }
                };
                resolve(mockStats[crypto]);
            }, Math.random() * 1000);
        });
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        
        this.handleMovement();
        
        // Animate exhibit elements
        this.exhibits.forEach(exhibit => {
            // Rotate miners slightly
            const minerMesh = exhibit.children[0];
            if (minerMesh) {
                minerMesh.rotation.y += 0.002;
                
                // Animate LED
                const led = minerMesh.children.find(child => 
                    child.material && child.material.emissive
                );
                if (led) {
                    const time = Date.now() * 0.005;
                    led.material.emissive.setHex(
                        Math.sin(time) > 0 ? 0x002200 : 0x004400
                    );
                }
            }
        });

        this.renderer.render(this.scene, this.camera);
    }
}

// Initialize museum when page loads
let museum;
document.addEventListener('DOMContentLoaded', () => {
    museum = new Museum3D();
});