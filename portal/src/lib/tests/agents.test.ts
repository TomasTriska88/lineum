import { describe, it, expect } from "vitest";

describe("Agent Scale Slider Logic", () => {
    // Replicating the logic from api-solutions/+page.svelte
    function calculateScale(sliderValue: number): number {
        return Math.floor(Math.pow(10, sliderValue / 20)); // Up to ~100k for value=100
    }

    function calculateVisualCap(exponentialScale: number): number {
        return Math.min(exponentialScale, 500); // UI canvas limit
    }

    it("should start with 1 agent at slider value 0", () => {
        const scale = calculateScale(0);
        expect(scale).toBe(1);
        expect(calculateVisualCap(scale)).toBe(1);
    });

    it("should scale properly at intermediate values", () => {
        const scale50 = calculateScale(50);
        // 10 ^ (50/20) = 10 ^ 2.5 = 316.22
        expect(scale50).toBe(316);
        expect(calculateVisualCap(scale50)).toBe(316); // Under 500, all are visible
    });

    it("should reach 100k scale at slider value 100 but cap visuals to 500", () => {
        const scale100 = calculateScale(100);
        // 10 ^ (100/20) = 10 ^ 5 = 100,000
        expect(scale100).toBe(100000);
        expect(calculateVisualCap(scale100)).toBe(500); // 500 cap enforced!
    });

    it("should never exceed 500 items in the scenarioAgents pool allocation", () => {
        const poolSize = 500;
        const sliderAgentsPool = Array.from({ length: poolSize }).map((_, i) => ({
            id: `slider_agent_${i}`
        }));

        expect(sliderAgentsPool.length).toBe(500);

        // Simulating the Svelte reactive slice statement
        const scaleMax = calculateScale(100);
        const visualCap = calculateVisualCap(scaleMax);
        const scenarioAgents = sliderAgentsPool.slice(0, visualCap);

        // UI array must remain safe
        expect(scenarioAgents.length).toBe(500);
    });
});

describe("API Loading State Machine", () => {
    // Replicating the state transitions from api-solutions/+page.svelte startSimulation()
    it("should transition from idle -> compiling -> simulating -> idle correctly", async () => {
        let isSimulating = false;
        let isCompilingAPI = false;

        // Initial state
        expect(isSimulating).toBe(false);
        expect(isCompilingAPI).toBe(false);

        // 1. User clicks "Run Live"
        const startSimulation = async () => {
            if (isSimulating || isCompilingAPI) return;
            isCompilingAPI = true; // synchronous lock applies immediately

            // Mocking the POST fetch layout
            await new Promise(resolve => setTimeout(resolve, 50));

            // Mock WebSocket connection
            const mockSocketOnMessage = () => {
                isSimulating = true;
                isCompilingAPI = false; // loader hides
            };

            const mockSocketOnClose = () => {
                isSimulating = false;
                isCompilingAPI = false;
            };

            return { mockSocketOnMessage, mockSocketOnClose };
        };

        // Trigger start
        const promise = startSimulation();
        // Immediately after trigger, compiling should be true, simulating false
        expect(isCompilingAPI).toBe(true);
        expect(isSimulating).toBe(false);

        // Await the backend fetch to finish
        const socketControls = await promise;
        expect(socketControls).toBeDefined();

        // Still compiling until first WS message
        expect(isCompilingAPI).toBe(true);

        // 2. First WebGL JSON payload arrives
        socketControls?.mockSocketOnMessage();
        expect(isCompilingAPI).toBe(false); // loader disappears
        expect(isSimulating).toBe(true);    // canvas simulation takes over

        // 3. Simulation ends or User Aborts
        socketControls?.mockSocketOnClose();
        expect(isSimulating).toBe(false);
        expect(isCompilingAPI).toBe(false); // completely idle
    });
});

