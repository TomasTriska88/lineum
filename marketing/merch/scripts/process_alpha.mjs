import fs from 'fs';
import { createCanvas, loadImage } from 'canvas';
import path from 'path';

/**
 * Lineum Merch Alpha Extractor (Un-premultiply)
 * 
 * AI image generators struggle to natively produce clean transparent PNGs (Alpha channel).
 * They often composite images onto a black background and pseudo-transparency leaves "halos".
 * 
 * THIS SCRIPT mathematically subtracts a pure `#000000` black background 
 * by calculating luminescence and dividing the RGB values by it, 
 * perfectly recreating the original additive optical Alpha channel.
 * 
 * SECONDARILY, it immediately upscales the resulting image by 400% (4x)
 * using a crisp "Nearest Neighbor" scaling flag to ensure the final
 * transparent PNG meets Spreadshop/Printful DPI resolution requirements
 * without creating blurry edges.
 * 
 * Usage from `marketing/merch/scripts/`:
 * node process_alpha.mjs ../equation/art.png
 */

const targetFile = process.argv[2];

if (!targetFile) {
    console.error('Usage: node process_alpha.mjs <path-to-png-file>');
    process.exit(1);
}

const inputPath = path.resolve(process.cwd(), targetFile);

async function extractAlpha() {
    try {
        console.log(`Processing alpha channel for: ${inputPath}`);

        // Use fs.readFileSync to bypass canvas libpng path encoding issues with diacritics
        const imageBuffer = fs.readFileSync(inputPath);
        const image = await loadImage(imageBuffer);

        const canvas = createCanvas(image.width, image.height);
        const ctx = canvas.getContext('2d');

        // Draw the black-background original
        ctx.drawImage(image, 0, 0);

        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const data = imageData.data;

        for (let i = 0; i < data.length; i += 4) {
            const r = data[i];
            const g = data[i + 1];
            const b = data[i + 2];

            // Maximum brightness = the pixel's true opacity when composited over pure black
            const alpha = Math.max(r, g, b);

            if (alpha > 0) {
                // Restore the raw color (Un-premultiply) to its full un-dimmed vibrancy
                data[i] = Math.min(255, (r / alpha) * 255);
                data[i + 1] = Math.min(255, (g / alpha) * 255);
                data[i + 2] = Math.min(255, (b / alpha) * 255);
                // Set the derived pixel opacity
                data[i + 3] = alpha;
            } else {
                // If the pixel was pure black, it is now pure transparent
                data[i + 3] = 0;
            }
        }

        // --- PHASE 1: MATHEMATICAL ALPHA EXTRACTION ---
        ctx.putImageData(imageData, 0, 0);

        // --- PHASE 2: CRISP UPSCALING (NEAREST NEIGHBOR) ---
        console.log(`Upscaling image 400% for print resolution...`);
        const scale = 4;
        const printWidth = image.width * scale;
        const printHeight = image.height * scale;

        const printCanvas = createCanvas(printWidth, printHeight);
        const printCtx = printCanvas.getContext('2d');

        // Force raw algorithmic rendering to prevent blurry aliasing on the scale
        printCtx.patternQuality = 'nearest';
        printCtx.quality = 'nearest';
        printCtx.imageSmoothingEnabled = false;

        // Draw the extracted alpha canvas onto the new massive 4K print canvas
        printCtx.drawImage(canvas, 0, 0, printWidth, printHeight);

        // Finalize
        const buffer = printCanvas.toBuffer('image/png');

        // Overwrite the original file with the new massive transparent version
        fs.writeFileSync(inputPath, buffer);

        console.log('✅ Success! Perfect 400% upscaled transparent print image saved.');
    } catch (error) {
        console.error('❌ Error processing image:', error.message);
        process.exit(1);
    }
}

extractAlpha();
