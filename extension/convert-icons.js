const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

// Check if the icons directory exists
const iconsDir = path.join(__dirname, 'icons');
if (!fs.existsSync(iconsDir)) {
  fs.mkdirSync(iconsDir, { recursive: true });
}

// Sizes to generate
const sizes = [16, 48, 128];

async function convertSvgToPng() {
  try {
    // Read the SVG file
    const svgPath = path.join(iconsDir, 'icon.svg');
    if (!fs.existsSync(svgPath)) {
      console.error('SVG file not found');
      return;
    }

    // Convert SVG to PNG for each size
    for (const size of sizes) {
      await sharp(svgPath)
        .resize(size, size)
        .png()
        .toFile(path.join(iconsDir, `icon${size}.png`));
      
      console.log(`Generated icon${size}.png`);
    }

    console.log('Icon conversion complete');
  } catch (error) {
    console.error('Error converting icons:', error);
  }
}

convertSvgToPng(); 