
const sharp = require('sharp');
const fs = require('fs');

async function analyzePixels(filePath) {
    console.log(`\n🕵️‍♀️ Analyzing: ${filePath}`);
    if (!fs.existsSync(filePath)) {
        console.log("   ❌ File not found.");
        return;
    }

    try {
        const image = sharp(filePath);
        const metadata = await image.metadata();
        const { width, height } = metadata;

        // Extract raw pixel data
        const buffer = await image.ensureAlpha().raw().toBuffer();
        const channels = 4; // R, G, B, Alpha

        // Check corner pixels (Top-Left)
        // 0,0
        const tl_r = buffer[0];
        const tl_g = buffer[1];
        const tl_b = buffer[2];
        const tl_a = buffer[3];

        console.log(`   🎨 Top-Left Pixel: rgba(${tl_r}, ${tl_g}, ${tl_b}, ${tl_a})`);

        if (tl_a === 0) {
            console.log("   ✅ Corner is TRANSPARENT.");
        } else if (tl_r > 240 && tl_g > 240 && tl_b > 240 && tl_a === 255) {
            console.log("   ⬜ Corner is WHITE.");
        } else {
            console.log("   ❓ Corner is colored.");
        }

        // Check if overall it looks like a white box
        // Sample a few points around the border
        let whitePixels = 0;
        let transparentPixels = 0;
        let totalSamples = 0;

        for (let y = 0; y < height; y += Math.floor(height / 10)) {
            for (let x = 0; x < width; x += width - 1) { // Left and right edges
                const idx = (y * width + x) * channels;
                if (idx < buffer.length) {
                    const r = buffer[idx];
                    const g = buffer[idx + 1];
                    const b = buffer[idx + 2];
                    const a = buffer[idx + 3];

                    if (a === 0) transparentPixels++;
                    else if (r > 240 && g > 240 && b > 240) whitePixels++;
                    totalSamples++;
                }
            }
        }

        console.log(`   📊 Edge Sampling: ${transparentPixels} transparent, ${whitePixels} white (out of ${totalSamples})`);

    } catch (error) {
        console.error("   ❌ Error:", error.message);
    }
}

async function run() {
    await analyzePixels('public/icon.png');
    await analyzePixels('public/live-icon.png');
}

run();
