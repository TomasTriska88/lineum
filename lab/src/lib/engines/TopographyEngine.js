import * as THREE from 'three';

export class TopographyEngine {
    constructor(container, phiData, trajData) {
        this.container = container;
        this.phiData = phiData;
        this.trajData = trajData;

        this.currentFrameIndex = 0;
        this.frameCount = phiData.metadata.frame_count;
        this.playbackSpeed = 1.0; // ⚡ New: Control playback speed
        this.lastTime = performance.now();

        this.showSpiral = false; // 🌀 Toggle for Golden Spiral overlay
        this.harmonicData = null;

        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });

        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.container.appendChild(this.renderer.domElement);

        this.camera.position.set(50, 50, 50);
        this.camera.lookAt(0, 0, 0);

        this.initLights();
        this.initGrid();
        this.initHarmonics();

        window.addEventListener('resize', this.onResize.bind(this));
    }

    initLights() {
        const ambientLight = new THREE.AmbientLight(0x404040, 3);
        this.scene.add(ambientLight);

        this.dirLight = new THREE.DirectionalLight(0x00ffff, 2);
        this.dirLight.position.set(20, 40, 20);
        this.scene.add(this.dirLight);

        this.pointLight = new THREE.PointLight(0xff00ff, 3, 100);
        this.pointLight.position.set(-20, 20, -20);
        this.scene.add(this.pointLight);
    }

    initGrid() {
        const size = 80;
        const segments = 128;
        this.geometry = new THREE.PlaneGeometry(size, size, segments, segments);
        this.geometry.rotateX(-Math.PI / 2);

        // Group to rotate only the terrain, not the lights
        this.terrainGroup = new THREE.Group();
        this.scene.add(this.terrainGroup);

        this.material = new THREE.MeshPhongMaterial({
            color: 0x00ffff,
            wireframe: true,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.2
        });

        this.plane = new THREE.Mesh(this.geometry, this.material);
        this.terrainGroup.add(this.plane);

        // Solid surface with emissive "glow" for depth
        const solidMaterial = new THREE.MeshPhongMaterial({
            color: 0x050505,
            emissive: 0x001111,
            shininess: 100,
            specular: 0x00ffff,
            side: THREE.DoubleSide
        });
        this.solidPlane = new THREE.Mesh(this.geometry, solidMaterial);
        this.terrainGroup.add(this.solidPlane);

        this.initLinony();
    }

    initLinony() {
        this.linony = [];
        const fiberMaterial = new THREE.LineBasicMaterial({ color: 0xffaa00, transparent: true, opacity: 0.8 });

        // Create 3D fibers (lines) that extend from 2D plane into "depth"
        this.trajData.forEach(traj => {
            // Find first valid point to set initial fiber position
            const firstValid = traj.path.find(p => p !== null);
            if (!firstValid) return;

            const x = (firstValid[0] - 64) * 0.5;
            const z = (firstValid[1] - 64) * 0.5;

            const points = [];
            points.push(new THREE.Vector3(x, 50, z)); // Top
            points.push(new THREE.Vector3(x, -50, z)); // Bottom

            const geometry = new THREE.BufferGeometry().setFromPoints(points);
            const line = new THREE.Line(geometry, fiberMaterial);

            // Add a glowing core at the intersection
            const coreGeom = new THREE.SphereGeometry(0.5, 8, 8);
            const coreMat = new THREE.MeshBasicMaterial({ color: 0xffaa00, transparent: true, opacity: 1.0 });
            const core = new THREE.Mesh(coreGeom, coreMat);

            const group = new THREE.Group();
            group.add(line);
            group.add(core);

            this.terrainGroup.add(group);
            this.linony.push({ group, traj, core, line });
        });
    }

    initHarmonics() {
        this.harmonicsGroup = new THREE.Group();
        this.scene.add(this.harmonicsGroup);

        // Golden Spiral Geometry (Conceptual Ideal)
        const points = [];
        const a = 0.5; // Scale
        const phi = (1 + Math.sqrt(5)) / 2;
        const b = Math.log(phi) / (Math.PI / 2);

        for (let theta = 0; theta < Math.PI * 6; theta += 0.1) {
            const r = a * Math.exp(b * theta);
            const x = r * Math.cos(theta);
            const z = r * Math.sin(theta);
            points.push(new THREE.Vector3(x, 0, z));
        }

        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({
            color: 0xff00ff,
            transparent: true,
            opacity: 0.4,
            dashSize: 1,
            gapSize: 0.5
        });
        this.goldenSpiral = new THREE.Line(geometry, material);
        this.goldenSpiral.visible = false;
        this.harmonicsGroup.add(this.goldenSpiral);
    }

    updateTopography() {
        if (!this.phiData) return;

        const frame = this.phiData.frames[this.currentFrameIndex];
        const positions = this.geometry.attributes.position.array;

        // ⚖️ Normalization: subtract mean to stop "flying upwards" 
        // and focus on the spatial variations (the "wells")
        let sum = 0;
        let count = 0;
        for (let y = 0; y < 64; y++) {
            for (let x = 0; x < 64; x++) {
                sum += frame[y][x];
                count++;
            }
        }
        const meanPhi = sum / count;
        const hScale = -0.2; // Reduced to prevent "over-the-screen" mountains

        const segments = 128;
        for (let i = 0; i < positions.length; i += 3) {
            // Map 128x128 vertex grid to 64x64 audit data
            const vx = (positions[i] / 80 + 0.5) * 63;
            const vz = (positions[i + 2] / 80 + 0.5) * 63;

            const ix = Math.floor(vx);
            const iy = Math.floor(vz);

            if (ix >= 0 && ix < 64 && iy >= 0 && iy < 64) {
                // Use relative Φ (phi - mean)
                const relativePhi = frame[iy][ix] - meanPhi;
                positions[i + 1] = relativePhi * hScale;
            }
        }

        this.geometry.computeVertexNormals();
        this.geometry.attributes.position.needsUpdate = true;

        // Update linony positions and visual states
        this.linony.forEach(c => {
            const path = c.traj.path;

            // 👁️ Precise Visibility Gate: only show if we have a valid point for this frame index
            const point = path[this.currentFrameIndex];

            if (!point) {
                c.group.visible = false;
                return;
            }

            c.group.visible = true;

            const x = point[0]; // x is at index 0 in [x, y, amp, step]
            const y = point[1]; // y is at index 1
            const amplitude = point[2];

            const tx = (x - 64) * 0.5;
            const tz = (y - 64) * 0.5;

            c.group.position.set(tx, 0, tz);

            // Core height follows the local Φ-well depth
            const vx = (tx / 80 + 0.5) * 63;
            const vz = (tz / 80 + 0.5) * 63;
            const ix = Math.floor(vx);
            const iy = Math.floor(vz);

            if (ix >= 0 && ix < 64 && iy >= 0 && iy < 64) {
                const relativePhi = frame[iy][ix] - meanPhi;
                c.core.position.y = relativePhi * hScale;
            }

            // 👻 Ghost state for unborn linony (amplitude-based)
            if (amplitude < 100000) {
                c.core.material.opacity = 0.2;
                c.core.scale.set(0.5, 0.5, 0.5);
                c.line.material.opacity = 0.1;
            } else {
                c.core.material.opacity = 1.0;
                c.core.scale.set(1.0, 1.0, 1.0);
                c.line.material.opacity = 0.5;
            }
        });

        // This line is now handled by the animate function
        // this.currentFrameIndex = (this.currentFrameIndex + 1) % this.frameCount;
    }

    animate() {
        this.requestID = requestAnimationFrame(this.animate.bind(this));

        const currentTime = performance.now();
        const deltaTime = (currentTime - this.lastTime) / 1000;
        this.lastTime = currentTime;

        // ⏱️ Proper frame-rate independent playback
        this.frameTimeCounter += deltaTime * this.playbackSpeed * 10; // Base speed: 10 frames per second

        if (this.frameTimeCounter >= 1) {
            const framesToAdvance = Math.floor(this.frameTimeCounter);
            this.currentFrameIndex = (this.currentFrameIndex + framesToAdvance) % this.frameCount;
            this.frameTimeCounter -= framesToAdvance;
            this.updateTopography();

            // 📡 Notify UI of frame change
            if (this.onFrameUpdate) {
                this.onFrameUpdate(this.currentFrameIndex);
            }
        }

        this.terrainGroup.rotation.y += 0.001;
        this.renderer.render(this.scene, this.camera);
    }

    jumpToFrame(index) {
        if (index >= 0 && index < this.frameCount) {
            this.currentFrameIndex = index;
            this.frameTimeCounter = 0;
            this.updateTopography();
            if (this.onFrameUpdate) {
                this.onFrameUpdate(this.currentFrameIndex);
            }
        }
    }

    onResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    dispose() {
        cancelAnimationFrame(this.requestID);
        window.removeEventListener('resize', this.onResize);
        this.renderer.dispose();
        this.geometry.dispose();
        this.material.dispose();
    }
}
