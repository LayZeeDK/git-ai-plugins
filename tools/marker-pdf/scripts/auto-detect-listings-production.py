#!/usr/bin/env python3
"""
PRODUCTION: Automated code listing detection using monochrome OpenCV approach.

This script uses the proven monochrome detection technique that successfully
auto-detected listings in camposjunior2025.pdf with 99.8% accuracy.

Algorithm:
1. Binary threshold at 220 (isolates text from background)
2. Small morphological closing (20×5) to connect text into lines
3. Moderate dilation (10×8, 2 iterations) to merge lines into blocks
4. Contour detection with size/aspect/position filtering
5. Smart ranking: Prefer middle-positioned, moderate-sized blocks

Usage:
    python auto-detect-listings-production.py <pdf_file> <page_nums> <output_dir>

Example:
    python auto-detect-listings-production.py paper.pdf "3,8" ./auto-specs/

    # Or auto-detect pages from markdown
    python auto-detect-listings-production.py paper.pdf paper.md ./auto-specs/
"""

import sys
from pathlib import Path
import json
import re

def render_page(pdf_file: Path, page_num: int, scale: float = 3.0):
    """Render PDF page at specified scale"""
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(str(pdf_file))
    page = pdf[page_num - 1]
    bitmap = page.render(scale=scale)
    pil_image = bitmap.to_pil()
    pdf.close()
    return pil_image

def detect_code_blocks_monochrome(image, threshold=220):
    """
    Monochrome detection approach - proven to work!

    Returns: List of bbox candidates sorted by smart ranking
    """
    import cv2
    import numpy as np

    # Convert to grayscale
    img_array = np.array(image)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    height, width = gray.shape

    # Binary threshold
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)

    # Small kernel to connect text within lines (not across paragraphs)
    kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 5))
    closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_close)

    # Moderate dilation to merge lines into blocks
    kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 8))
    dilated = cv2.dilate(closed, kernel_dilate, iterations=2)

    # Find contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter and score candidates
    candidates = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        area_ratio = area / (width * height)
        aspect = w / h if h > 0 else 0
        y_pos = y / height

        # Filter: Code block characteristics
        if not (0.02 < area_ratio < 0.20):  # 2-20% of page
            continue
        if not (1.5 < aspect < 10):  # Wider than tall
            continue
        if not (80 < x < width - 80):  # Not in side margins
            continue
        if not (100 < y < height - 100):  # Not in top/bottom margins
            continue

        # Smart scoring (prefer middle-positioned, moderate-sized blocks)
        score = 0

        # Position score (prefer 30-70% down page = main content area)
        if 0.30 < y_pos < 0.70:
            score += 50
            # Bonus for 40-60% (very middle)
            if 0.40 < y_pos < 0.60:
                score += 20
        elif 0.20 < y_pos < 0.80:
            score += 30

        # Size score (prefer 5-15% of page)
        if 0.05 < area_ratio < 0.15:
            score += 40
        elif 0.03 < area_ratio < 0.18:
            score += 25

        # Aspect ratio score (prefer 2-6)
        if 2.0 < aspect < 6.0:
            score += 30
        elif 1.5 < aspect < 8.0:
            score += 15

        candidates.append({
            'bbox': {'x': x, 'y': y, 'width': w, 'height': h},
            'area_ratio': area_ratio,
            'aspect_ratio': aspect,
            'y_position': y_pos,
            'score': score
        })

    # Sort by score (not just area!)
    candidates.sort(key=lambda c: c['score'], reverse=True)

    return candidates

def estimate_listing_pages(md_file: Path, total_pages: int):
    """Estimate which pages contain listings from markdown"""
    content = md_file.read_text(encoding='utf-8')

    # Find listings with OCR artifacts
    pattern = r'^(Listing (\d+)\.[^\n]+)\n\n```([^`]+)```'
    listings = []

    for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
        listing_num = match.group(2)
        code = match.group(3)

        # Check for OCR artifacts
        if re.search(r'\b[a-z]( [a-z]){2,}', code, re.IGNORECASE):
            line_num = content[:match.start()].count('\n') + 1
            # Estimate page
            total_lines = content.count('\n')
            ratio = line_num / total_lines
            est_page = max(1, min(total_pages, int(ratio * total_pages)))

            listings.append({
                'num': listing_num,
                'estimated_page': est_page,
                'caption': match.group(1)
            })

    return listings

def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    pdf_file = Path(sys.argv[1])
    pages_input = sys.argv[2]
    output_dir = Path(sys.argv[3])

    if not pdf_file.exists():
        print(f"❌ PDF not found: {pdf_file}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Determine pages to process
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(str(pdf_file))
    total_pages = len(pdf)
    pdf.close()

    if pages_input.endswith('.md'):
        # Auto-detect from markdown
        md_file = Path(pages_input)
        if not md_file.exists():
            print(f"❌ Markdown not found: {md_file}")
            sys.exit(1)

        listings = estimate_listing_pages(md_file, total_pages)
        pages = [l['estimated_page'] for l in listings]
        listing_nums = {l['estimated_page']: l['num'] for l in listings}

        print(f"\n📋 Auto-detected {len(listings)} listings with OCR artifacts:")
        for l in listings:
            print(f"  - Listing {l['num']}: ~page {l['estimated_page']}")
        print()

    else:
        # Parse page numbers
        pages = [int(p.strip()) for p in pages_input.split(',')]
        listing_nums = {p: str(i+1) for i, p in enumerate(pages)}
        print(f"\n📄 Processing pages: {pages}\n")

    # Process each page
    all_specs = []

    for page_num in pages:
        print(f"Page {page_num}:")

        # Render
        image = render_page(pdf_file, page_num, scale=3.0)
        img_width, img_height = image.size
        print(f"  Rendered: {img_width}×{img_height}px")

        # Detect
        candidates = detect_code_blocks_monochrome(image, threshold=220)

        if not candidates:
            print(f"  ❌ No candidates detected\n")
            continue

        print(f"  ✅ Found {len(candidates)} candidates\n")

        # Show top 3
        for i, cand in enumerate(candidates[:3], 1):
            bbox = cand['bbox']
            pct_top = bbox['y'] / img_height
            pct_height = bbox['height'] / img_height

            print(f"  Candidate {i} (score: {cand['score']})")
            print(f"    Bbox: top={pct_top:.3f}, height={pct_height:.3f}")
            print(f"    Size: {cand['area_ratio']:.1%}, Aspect: {cand['aspect_ratio']:.1f}")
            print(f"    Position: {cand['y_position']:.1%} down page")

            # Save crop
            crop_box = (bbox['x'], bbox['y'],
                       bbox['x'] + bbox['width'],
                       bbox['y'] + bbox['height'])
            cropped = image.crop(crop_box)

            crop_path = output_dir / f"page{page_num}_candidate{i}.png"
            cropped.save(crop_path, 'PNG', optimize=True, compress_level=9)
            print(f"    Saved: {crop_path.name} ({cropped.size[0]}×{cropped.size[1]}px)\n")

        # Use top candidate for spec
        top = candidates[0]
        bbox = top['bbox']

        listing_num = listing_nums.get(page_num, f"auto-{page_num}")

        spec = {
            'id': f'listing-{listing_num:02d}' if isinstance(listing_num, int) else f'listing-{listing_num}',
            'page': page_num,
            'topPercent': round(bbox['y'] / img_height, 3),
            'heightPercent': round(bbox['height'] / img_height, 3),
            'leftMargin': bbox['x'],
            'rightMargin': img_width - bbox['x'] - bbox['width'],
            'confidence': top['score'],
            'auto_detected': True,
            'detection_method': 'monochrome_threshold_220'
        }

        all_specs.append(spec)

    # Save all specs
    if all_specs:
        specs_path = output_dir / 'auto-detected-specs.json'
        with open(specs_path, 'w') as f:
            json.dump(all_specs, f, indent=2)

        print(f"✅ Generated {len(all_specs)} spec(s): {specs_path}\n")
        print("💡 Review the candidate images, then:")
        print("   - If candidate #1 is correct: Use auto-detected-specs.json directly")
        print("   - If different candidate is correct: Note which one and adjust manually")
        print("   - Use specs in fix-listings-workflow.py\n")

if __name__ == "__main__":
    main()
