import { describe, it, expect, beforeEach, vi } from 'vitest';
import { TopographyEngine } from '../src/lib/engines/TopographyEngine';

// Mocking ThreeJS and DOM elements for testing
// Mocking globals
global.requestAnimationFrame = vi.fn();
global.cancelAnimationFrame = vi.fn();

vi.mock('three', () => {
    const fn = () => vi.fn();
    return {
        Scene: function () { this.add = vi.fn(); },
        PerspectiveCamera: function () {
            this.position = { set: vi.fn() };
            this.lookAt = vi.fn();
            this.updateProjectionMatrix = vi.fn();
        },
        WebGLRenderer: function () {
            this.setSize = vi.fn();
            this.setPixelRatio = vi.fn();
            this.render = vi.fn();
            this.dispose = vi.fn();
            this.domElement = document.createElement('div');
        },
        AmbientLight: function () { },
        DirectionalLight: function () { this.position = { set: vi.fn() }; },
        PointLight: function () { this.position = { set: vi.fn() }; },
        PlaneGeometry: function () {
            this.rotateX = vi.fn();
            this.attributes = { position: { array: new Float32Array(10000), needsUpdate: false } };
            this.computeVertexNormals = vi.fn();
            this.dispose = vi.fn();
        },
        BufferGeometry: function () {
            this.setFromPoints = vi.fn().mockReturnThis();
            this.dispose = vi.fn();
        },
        Group: function () {
            this.add = vi.fn();
            this.rotation = { y: 0 };
            this.position = { set: vi.fn() };
        },
        MeshPhongMaterial: function () { this.dispose = vi.fn(); },
        MeshBasicMaterial: function () { this.dispose = vi.fn(); },
        LineBasicMaterial: function () { this.dispose = vi.fn(); },
        Mesh: function () { this.position = { set: vi.fn() }; },
        Line: function () { },
        SphereGeometry: function () { },
        Vector3: function (x, y, z) { this.x = x; this.y = y; this.z = z; },
        DoubleSide: 2
    };
});

describe('TopographyEngine Synchronization', () => {
    let container;
    let phiData;
    let trajData;
    let engine;

    beforeEach(() => {
        // Mock performance.now to control time BEFORE engine creation
        vi.spyOn(performance, 'now').mockReturnValue(0);

        container = document.createElement('div');
        phiData = {
            metadata: { frame_count: 100 },
            frames: Array(100).fill(Array(64).fill(Array(64).fill(0)))
        };
        trajData = [];
        engine = new TopographyEngine(container, phiData, trajData);
    });

    it('should respect playbackSpeed when advancing frames', () => {
        engine.playbackSpeed = 2.0;

        // Mock deltaTime by advancing performance.now
        // lastTime was 0 (from beforeEach). We move to 100ms.
        vi.spyOn(performance, 'now').mockReturnValue(100);

        // Base speed is 10fps. 100ms at 2x speed is 2 frames.
        const callback = vi.fn();
        engine.onFrameUpdate = callback;

        engine.animate();

        expect(engine.currentFrameIndex).toBe(2);
        expect(callback).toHaveBeenCalledWith(2);
    });

    it('should handle rapid speed changes correctly', () => {
        engine.playbackSpeed = 5.0; // Max speed
        vi.spyOn(performance, 'now').mockReturnValue(100); // 100ms since 0

        engine.animate();
        expect(engine.currentFrameIndex).toBe(5);

        engine.playbackSpeed = 0.5; // Slow down
        vi.spyOn(performance, 'now').mockReturnValue(200); // 100ms since 100

        engine.animate();
        // Previous index (5) + (100ms * 0.5 * 10fps) = 5 + 0.5 = 5.5 -> floor(5.5) -> index 5
        expect(engine.currentFrameIndex).toBe(5);

        vi.spyOn(performance, 'now').mockReturnValue(300); // another 100ms since 200
        engine.animate();
        // Now total frameTimeCounter from slow mode (0.5+0.5) hits 1.0
        expect(engine.currentFrameIndex).toBe(6);
    });
});
