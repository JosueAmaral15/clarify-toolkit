#!/usr/bin/env python3
"""
Icon Generator for Clarify Project
Converts SVG to PNG and ICO formats for desktop application usage.

Author: Josué Amaral
Date: December 21, 2025
"""

import os
import sys
from pathlib import Path

try:
    import cairosvg  # type: ignore
    HAS_CAIROSVG = True
except ImportError:
    HAS_CAIROSVG = False

try:
    from PIL import Image  # type: ignore
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

import io


def generate_icons():
    """Generate PNG and ICO icons from SVG source."""
    if not HAS_CAIROSVG:
        print("❌ cairosvg not installed. Run: pip install cairosvg")
        sys.exit(1)
    
    if not HAS_PIL:
        print("❌ Pillow not installed. Run: pip install Pillow")
        sys.exit(1)
    
    # Paths
    base_dir = Path(__file__).parent
    svg_path = base_dir / "assets" / "icons" / "icon.svg"
    icons_dir = base_dir / "assets" / "icons"
    
    if not svg_path.exists():
        raise FileNotFoundError(f"SVG icon not found: {svg_path}")
    
    # Read SVG content
    with open(svg_path, 'r', encoding='utf-8') as f:
        svg_content = f.read()
    
    # Generate PNG icons for different sizes
    sizes = [32, 64, 128, 256, 512]
    
    for size in sizes:
        print(f"Generating {size}x{size} PNG...")
        
        # Convert SVG to PNG
        png_data = cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            output_width=size,
            output_height=size
        )
        
        # Save PNG
        png_path = icons_dir / f"icon-{size}.png"
        with open(png_path, 'wb') as f:
            f.write(png_data)
    
    # Create main icon.png (256x256 - standard for desktop)
    main_png = icons_dir / "icon.png"
    if (icons_dir / "icon-256.png").exists():
        os.rename(icons_dir / "icon-256.png", main_png)
        print("Created main icon.png (256x256)")
    
    # Generate ICO file with multiple sizes (for Windows)
    print("Generating favicon.ico...")
    ico_sizes = [16, 32, 48, 64]
    images = []
    
    for size in ico_sizes:
        png_data = cairosvg.svg2png(
            bytestring=svg_content.encode('utf-8'),
            output_width=size,
            output_height=size
        )
        img = Image.open(io.BytesIO(png_data))
        images.append(img)
    
    # Save ICO with multiple sizes
    ico_path = icons_dir / "favicon.ico"
    # Convert each image to RGBA mode for ICO compatibility
    rgba_images = []
    for img in images:
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        rgba_images.append(img)
    
    rgba_images[0].save(
        ico_path,
        format='ICO',
        sizes=[(img.width, img.height) for img in rgba_images]
    )
    
    print(f"✅ Icons generated successfully in {icons_dir}")
    print("Generated files:")
    for icon_file in sorted(icons_dir.glob("*")):
        if icon_file.is_file():
            size = icon_file.stat().st_size
            print(f"  - {icon_file.name} ({size:,} bytes)")


if __name__ == "__main__":
    generate_icons()