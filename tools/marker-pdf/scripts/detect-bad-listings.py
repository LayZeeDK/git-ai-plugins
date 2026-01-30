#!/usr/bin/env python3
"""
Detect poorly OCR'd code listings in marker-pdf output.
Identifies listings with characteristic OCR spacing artifacts.
"""

import re
import sys
from pathlib import Path

def has_ocr_artifacts(code_block):
    """Check if code block has OCR spacing artifacts like 'c o n t e n t'"""
    # Pattern: single letters separated by spaces
    pattern = r'\b[a-z] [a-z] [a-z]'
    return bool(re.search(pattern, code_block, re.IGNORECASE))

def find_bad_listings(md_file):
    """Find listings that need manual review"""
    content = Path(md_file).read_text(encoding='utf-8')

    # Find all code blocks
    code_blocks = re.finditer(r'```(.*?)```', content, re.DOTALL)

    bad_listings = []
    for match in code_blocks:
        code = match.group(1)
        start_pos = match.start()

        # Find the line number
        line_num = content[:start_pos].count('\n') + 1

        # Check for OCR artifacts
        if has_ocr_artifacts(code):
            # Try to find associated listing number
            before_text = content[max(0, start_pos-200):start_pos]
            listing_match = re.search(r'Listing (\d+)', before_text)
            listing_num = listing_match.group(1) if listing_match else "Unknown"

            bad_listings.append({
                'listing': listing_num,
                'line': line_num,
                'preview': code[:100].replace('\n', ' ')
            })

    return bad_listings

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python detect-bad-listings.py <markdown_file>")
        sys.exit(1)

    md_file = sys.argv[1]
    bad_listings = find_bad_listings(md_file)

    if bad_listings:
        print(f"\n❌ Found {len(bad_listings)} listings with OCR artifacts:\n")
        for item in bad_listings:
            print(f"  Listing {item['listing']} (line {item['line']})")
            print(f"    Preview: {item['preview']}...\n")
        print("💡 Recommendation: Replace these with images from the PDF")
    else:
        print("\n✅ No OCR artifacts detected in code listings")
