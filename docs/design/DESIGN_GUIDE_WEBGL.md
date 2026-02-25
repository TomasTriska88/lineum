# Portal Animation & 3D Graphics Guidelines

## WebGL Rendering (Browser & Mobile Protection)

When creating new visualizations within the Lineum Portal (`src/lib/components` / `src/routes`) that utilize raw WebGL `canvas` performance (including wrappers like `Three.js` or `PixiJS`), it is strictly required to adhere to these rules:

### 1. Strict Garbage Collection (`onDestroy`)
If your `.svelte` component initializes an animation loop, it must de-allocate browser memory before its destruction. Simply navigating away via a Link will fill up the browser's buffer (resulting in a *Too many WebGL contexts* warning in the console).

```javascript
import { onMount } from 'svelte';

onMount(() => {
    let canvas = document.querySelector('canvas');
    let gl = canvas.getContext('webgl');
    let program = gl.createProgram();
    let frameId;
    
    const render = () => {
        // ... render logic ...
        frameId = requestAnimationFrame(render);
    };
    render();

    return () => {
        // Stop the animation frame request
        cancelAnimationFrame(frameId);

        // De-allocate blocks from Browser's Garbage Collector
        if (gl) {
            gl.deleteProgram(program);
            const lossContext = gl.getExtension('WEBGL_lose_context');
            if (lossContext) lossContext.loseContext();
        }
    }
});
```

### 2. Fragment Shader Complexity
When modeling mathematically complex rendering waves (e.g., `Eq-4` tensor fields):
* Whenever possible and pixel-perfect accuracy to the micrometer is not needed (i.e., for pure visual animation), always use `precision mediump float;` instead of `precision highp float;`. This significantly increases the frame rate on mobile devices (Android/iOS) and reduces GPU heat.
* Eliminate `for(...)` loops where possible. The Fragment Shader executes for **every single rendered pixel on the screen**, 60 times a second! Avoid nesting loops and reduce the number of "Glow" shadow iterations to the absolute minimum without sacrificing visual quality.

### 3. Mandatory Testing
If you are working on such UI, you must verify it using the Playwright E2E tests (`tests/e2e/routing_ui_pro.test.ts`), which catch memory leaks from the browser console. Never submit code without testing navigation back and forth.
