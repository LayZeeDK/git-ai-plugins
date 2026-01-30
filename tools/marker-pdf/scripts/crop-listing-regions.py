#!/usr/bin/env python3
"""
Crop code listing regions from PDF pages using percentage-based bbox specification.

Adapted from the Node.js figure cropping workflow (Sharp + pdf.js).
Uses pypdfium2 for rendering and Pillow for cropping.

Usage:
    python crop-listing-regions.py <pdf_file> <output_dir> <listing_specs_json>

Example:
    python crop-listing-regions.py paper.pdf ./images/ listing-specs.json

Listing specs JSON format:
[
  {
    "id": "listing-01",
    "page": 3,
    "topPercent": 0.45,
    "heightPercent": 0.20,
    "leftMargin": 100,
    "rightMargin": 100
  }
]
"""

import json
import sys
from pathlib import Path
from typing import List, Dict

def render_page(pdf_file: Path, page_num: int, scale: float = 3.0) -> 'Image':
    """
    Render a PDF page at specified scale using pypdfium2.

    Args:
        pdf_file: Path to PDF
        page_num: 1-indexed page number
        scale: Rendering scale (3.0 = ~300 DPI)

    Returns:
        PIL Image object
    """
    import pypdfium2 as pdfium

    pdf = pdfium.PdfDocument(str(pdf_file))
    page = pdf[page_num - 1]  # 0-indexed

    # Render at high resolution
    bitmap = page.render(scale=scale)
    pil_image = bitmap.to_pil()

    pdf.close()
    return pil_image

def calculate_bbox(image_width: int, image_height: int, spec: Dict) -> Dict[str, int]:
    """
    Calculate absolute pixel bbox from percentage specification.

    Follows the Node.js pattern:
    - topPercent: Where listing starts (0.0 = top, 1.0 = bottom)
    - heightPercent: How much vertical space it occupies
    - leftMargin/rightMargin: Fixed pixel margins

    Returns:
        Dict with keys: left, top, width, height (clamped to image bounds)
    """
    left = spec.get('leftMargin', 100)
    right_margin = spec.get('rightMargin', 100)

    top = round(image_height * spec['topPercent'])
    height = round(image_height * spec['heightPercent'])
    width = image_width - left - right_margin

    # CRITICAL: Clamp bbox to image boundaries (prevents "bad extract area")
    # Adapted from crop-figures.mjs lines 69-84
    bbox = {
        'left': max(0, left),
        'top': max(0, top),
        'width': max(10, min(width, image_width - left)),
        'height': max(10, min(height, image_height - top))
    }

    # Validate bbox doesn't extend beyond image
    if bbox['left'] + bbox['width'] > image_width:
        bbox['width'] = image_width - bbox['left']

    if bbox['top'] + bbox['height'] > image_height:
        bbox['height'] = image_height - bbox['top']

    return bbox

def crop_listing(image: 'Image', bbox: Dict[str, int], output_path: Path, optimize: bool = True):
    """
    Crop listing region from rendered page.

    Uses PIL's crop() method with bbox in format: (left, top, right, bottom)

    Args:
        image: PIL Image to crop from
        bbox: Dict with left, top, width, height
        output_path: Where to save cropped image
        optimize: Apply PNG optimization (like Sharp compressionLevel: 9)
    """
    from PIL import Image

    # Convert from (left, top, width, height) to PIL's (left, top, right, bottom)
    crop_box = (
        bbox['left'],
        bbox['top'],
        bbox['left'] + bbox['width'],
        bbox['top'] + bbox['height']
    )

    # Crop the region
    cropped = image.crop(crop_box)

    # Save with optimization (equivalent to Sharp compressionLevel: 9)
    cropped.save(
        output_path,
        'PNG',
        optimize=True,          # Enable PNG optimization
        compress_level=9        # Maximum compression (0-9)
    )

    return cropped.size  # Return (width, height)

def process_listing_specs(pdf_file: Path, output_dir: Path, specs: List[Dict], scale: float = 3.0):
    """
    Process all listing specifications to extract and crop images.

    Implements the workflow from finalize-markdown.js
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📄 Processing {len(specs)} listings from {pdf_file.name}")
    print(f"📐 Render scale: {scale}x (~{int(scale * 100)} DPI)\n")

    # Group specs by page to avoid re-rendering
    specs_by_page = {}
    for spec in specs:
        page = spec['page']
        if page not in specs_by_page:
            specs_by_page[page] = []
        specs_by_page[page].append(spec)

    results = []

    for page_num in sorted(specs_by_page.keys()):
        page_specs = specs_by_page[page_num]

        print(f"Page {page_num}:")

        # Render page once for all listings on it
        page_image = render_page(pdf_file, page_num, scale)
        img_width, img_height = page_image.size
        print(f"  Rendered: {img_width}×{img_height} pixels")

        for spec in page_specs:
            listing_id = spec['id']

            # Calculate bbox from percentages
            bbox = calculate_bbox(img_width, img_height, spec)

            # Crop the listing region
            output_path = output_dir / f"{listing_id}.png"
            cropped_size = crop_listing(page_image, bbox, output_path)

            # Calculate file size
            file_size_kb = output_path.stat().st_size / 1024

            print(f"  ✓ {listing_id}: {cropped_size[0]}×{cropped_size[1]}px, {file_size_kb:.0f}KB")

            results.append({
                'id': listing_id,
                'page': page_num,
                'size': cropped_size,
                'file_size_kb': file_size_kb,
                'output_path': str(output_path)
            })

        print()

    return results

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        print("\nExample listing-specs.json:")
        print(json.dumps([
            {
                "id": "listing-01",
                "page": 3,
                "topPercent": 0.45,
                "heightPercent": 0.20,
                "leftMargin": 100,
                "rightMargin": 100,
                "description": "Git conflict example"
            }
        ], indent=2))
        sys.exit(1)

    pdf_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    if not pdf_file.exists():
        print(f"❌ PDF not found: {pdf_file}")
        sys.exit(1)

    # Load specs from JSON file or command line
    if len(sys.argv) >= 4:
        specs_file = Path(sys.argv[3])
        if specs_file.exists():
            with open(specs_file) as f:
                specs = json.load(f)
        else:
            # Try parsing as JSON string
            try:
                specs = json.loads(sys.argv[3])
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON specs: {sys.argv[3]}")
                sys.exit(1)
    else:
        print("❌ No listing specs provided")
        sys.exit(1)

    # Process all listings
    results = process_listing_specs(pdf_file, output_dir, specs)

    print(f"✅ Extracted {len(results)} listings to: {output_dir}/")
    print("\n💡 Next step: Update markdown to reference these images")

    # Show markdown template
    print("\nMarkdown template:")
    for result in results:
        print(f"**Listing {result['id'].replace('listing-', '')}.** Caption here")
        print(f"![Listing visualization](./{Path(result['output_path']).name})")
        print()

if __name__ == "__main__":
    main()
