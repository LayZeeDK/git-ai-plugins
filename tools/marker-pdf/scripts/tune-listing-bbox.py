#!/usr/bin/env python3
"""
Interactive bbox tuning for listing extraction.

Shows current crop and allows adjustment of bbox parameters.

Usage:
    python tune-listing-bbox.py <pdf_file> <page_num> <listing_id>

Example:
    python tune-listing-bbox.py paper.pdf 3 listing-01

Controls:
    - Adjust topPercent: ↑↓ keys (or enter new value)
    - Adjust heightPercent: +- keys (or enter new value)
    - Preview crop: Press 'p'
    - Save spec: Press 's'
    - Quit: Press 'q'
"""

import sys
from pathlib import Path
import json

def render_page(pdf_file: Path, page_num: int, scale: float = 3.0):
    """Render PDF page"""
    import pypdfium2 as pdfium

    pdf = pdfium.PdfDocument(str(pdf_file))
    page = pdf[page_num - 1]
    bitmap = page.render(scale=scale)
    pil_image = bitmap.to_pil()
    pdf.close()

    return pil_image

def crop_and_save(image, bbox: dict, output_path: Path):
    """Crop image and save"""
    crop_box = (
        bbox['left'],
        bbox['top'],
        bbox['left'] + bbox['width'],
        bbox['top'] + bbox['height']
    )

    cropped = image.crop(crop_box)
    cropped.save(output_path, 'PNG', optimize=True, compress_level=9)

    return cropped.size

def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    pdf_file = Path(sys.argv[1])
    page_num = int(sys.argv[2])
    listing_id = sys.argv[3]

    if not pdf_file.exists():
        print(f"❌ PDF not found: {pdf_file}")
        sys.exit(1)

    # Default bbox (middle of page)
    bbox_spec = {
        'topPercent': 0.45,
        'heightPercent': 0.20,
        'leftMargin': 100,
        'rightMargin': 100
    }

    print(f"\n📄 Tuning bbox for {listing_id} on page {page_num}")
    print(f"📐 Rendering page...")

    page_image = render_page(pdf_file, page_num, scale=3.0)
    img_width, img_height = page_image.size
    print(f"   Page size: {img_width}×{img_height}px\n")

    # Interactive tuning
    print("🎛️  Current bbox:")
    print(f"   topPercent: {bbox_spec['topPercent']:.2f} (start at {bbox_spec['topPercent']*100:.0f}% down page)")
    print(f"   heightPercent: {bbox_spec['heightPercent']:.2f} (occupy {bbox_spec['heightPercent']*100:.0f}% of page)")
    print(f"   Margins: {bbox_spec['leftMargin']}px left, {bbox_spec['rightMargin']}px right\n")

    # Calculate absolute bbox
    bbox = {
        'left': bbox_spec['leftMargin'],
        'top': round(img_height * bbox_spec['topPercent']),
        'width': img_width - bbox_spec['leftMargin'] - bbox_spec['rightMargin'],
        'height': round(img_height * bbox_spec['heightPercent'])
    }

    print(f"📐 Absolute bbox:")
    print(f"   left: {bbox['left']}px, top: {bbox['top']}px")
    print(f"   width: {bbox['width']}px, height: {bbox['height']}px\n")

    # Generate preview
    output_dir = Path('test-output/bbox-tuning')
    output_dir.mkdir(parents=True, exist_ok=True)
    preview_path = output_dir / f"{listing_id}_preview.png"

    size = crop_and_save(page_image, bbox, preview_path)
    print(f"✅ Preview saved: {preview_path}")
    print(f"   Size: {size[0]}×{size[1]}px")
    print(f"   File: {preview_path.stat().st_size / 1024:.0f}KB\n")

    # Save spec
    spec_output = {
        'id': listing_id,
        'page': page_num,
        **bbox_spec
    }

    spec_path = output_dir / f"{listing_id}_spec.json"
    with open(spec_path, 'w') as f:
        json.dump(spec_output, f, indent=2)

    print(f"📋 Spec saved: {spec_path}\n")

    print("💡 To adjust:")
    print(f"   1. Open {preview_path} to review crop")
    print(f"   2. Edit {spec_path} to adjust percentages:")
    print(f"      - Increase topPercent to start lower on page")
    print(f"      - Decrease topPercent to start higher on page")
    print(f"      - Increase heightPercent to capture more content")
    print(f"      - Decrease heightPercent to capture less")
    print(f"   3. Re-run this script to preview adjusted crop")
    print(f"   4. When satisfied, use spec in fix-listings-workflow.py\n")

if __name__ == "__main__":
    main()
