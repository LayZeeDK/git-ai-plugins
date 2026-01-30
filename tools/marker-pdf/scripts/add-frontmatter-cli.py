#!/usr/bin/env python3
"""
Add YAML frontmatter to marker-pdf converted markdown files
Uses Claude CLI (no API key needed!)

Usage:
    python add-frontmatter-cli.py <pdf_file> <markdown_file>
    python add-frontmatter-cli.py --batch <markdown_dir>

Requirements:
    pip install pypdfium2 pyyaml
    claude CLI must be authenticated (run 'claude auth' if needed)
"""

import sys
import subprocess
import yaml
from pathlib import Path
import pypdfium2 as pdfium

def extract_pdf_metadata(pdf_path):
    """Extract metadata directly from PDF file"""
    doc = pdfium.PdfDocument(pdf_path)
    meta = doc.get_metadata_dict()

    # Parse date to year
    year = None
    creation_date = meta.get('CreationDate', '')
    if creation_date.startswith('D:'):
        year = int(creation_date[2:6])

    # Clean title
    title = meta.get('Title', '').strip()
    title = ' '.join(title.split())  # Normalize whitespace

    return {
        'title': title or None,
        'subject': meta.get('Subject', '').strip() or None,
        'year': year,
        'pages': len(doc),
    }

def extract_first_pages_text(pdf_path, num_pages=2):
    """Extract text from first N pages of PDF"""
    doc = pdfium.PdfDocument(pdf_path)
    text_parts = []

    for i in range(min(num_pages, len(doc))):
        page = doc[i]
        textpage = page.get_textpage()
        text = textpage.get_text_range()
        text_parts.append(f"=== PAGE {i+1} ===\n{text}\n")

    return '\n'.join(text_parts)

def generate_frontmatter_with_claude_cli(pdf_text, pdf_metadata):
    """Use Claude CLI to extract structured metadata"""

    prompt = f"""You are extracting metadata from an academic paper PDF to generate YAML frontmatter.

PDF METADATA (from file):
- Title: {pdf_metadata.get('title') or 'Not in metadata'}
- Year: {pdf_metadata.get('year') or 'Not in metadata'}
- Pages: {pdf_metadata.get('pages')}
- Subject/CCS: {pdf_metadata.get('subject') or 'Not in metadata'}

PDF TEXT (first 2 pages):
{pdf_text[:8000]}

TASK:
Extract the following and output ONLY valid YAML (no explanation, no markdown code blocks):

Required fields:
- title: Full paper title (use PDF metadata if good, otherwise extract)
- authors: List in format "Name, Institution, Country"
- year: Publication year
- pages: Total page count (use PDF metadata: {pdf_metadata.get('pages')})

Optional fields (include if found):
- venue: Full conference/journal name
- doi: Format "10.xxxx/xxxxx"
- type: "conference", "journal", or "preprint"
- keywords: List from Keywords/CCS/Index Terms section

RULES:
- Use PDF metadata values where available
- Extract authors with affiliations from page 1
- Find DOI from footer or citation box
- Output ONLY valid YAML starting with ---
- If field not found, omit it

OUTPUT FORMAT (no code blocks, just raw YAML):
---
title: "Exact title"
authors:
  - "Name, Institution, Country"
year: 2025
venue: "Full Name"
doi: "10.1145/xxxxx"
pages: 35
type: "conference"
keywords:
  - "keyword1"
---"""

    # Call claude CLI
    result = subprocess.run(
        ['claude', '-m', 'Output ONLY the YAML frontmatter, nothing else:', prompt],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )

    if result.returncode != 0:
        raise Exception(f"Claude CLI error: {result.stderr}")

    response_text = result.stdout.strip()

    # Extract YAML (remove markdown code blocks if Claude added them)
    if '```yaml' in response_text:
        start = response_text.find('```yaml') + 7
        end = response_text.find('```', start)
        yaml_text = response_text[start:end].strip()
    elif '```' in response_text:
        start = response_text.find('```') + 3
        end = response_text.find('```', start)
        yaml_text = response_text[start:end].strip()
    else:
        yaml_text = response_text

    # Ensure it starts with ---
    if not yaml_text.startswith('---'):
        yaml_text = '---\n' + yaml_text
    if not yaml_text.endswith('---'):
        yaml_text = yaml_text + '\n---'

    return yaml_text

def prepend_frontmatter(markdown_file, frontmatter_yaml):
    """Add frontmatter to markdown file"""

    # Read existing content
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if frontmatter already exists
    if content.startswith('---'):
        print(f"    [WARN] {Path(markdown_file).name} already has frontmatter, skipping")
        return False

    # Combine frontmatter + content
    output = frontmatter_yaml.strip() + '\n\n' + content

    # Write back
    with open(markdown_file, 'w', encoding='utf-8') as f:
        f.write(output)

    return True

def process_single_pdf(pdf_path, markdown_path):
    """Process a single PDF and add frontmatter to its markdown"""

    print(f"\n[*] Processing: {Path(pdf_path).name}")
    print(f"    Markdown: {Path(markdown_path).name}")

    # 1. Extract PDF metadata
    print("    1/4: Extracting PDF metadata...")
    pdf_meta = extract_pdf_metadata(pdf_path)
    title_preview = pdf_meta['title'][:60] + '...' if pdf_meta['title'] and len(pdf_meta['title']) > 60 else pdf_meta['title']
    print(f"         [OK] Title: {title_preview}" if pdf_meta['title'] else "         [WARN] No title")
    print(f"         [OK] Year: {pdf_meta['year']}")
    print(f"         [OK] Pages: {pdf_meta['pages']}")

    # 2. Extract first 2 pages text
    print("    2/4: Extracting first 2 pages text...")
    try:
        pdf_text = extract_first_pages_text(pdf_path, num_pages=2)
        print(f"         [OK] Extracted {len(pdf_text)} characters")
    except Exception as e:
        print(f"         [FAIL] Error: {e}")
        return False

    # 3. Generate frontmatter with Claude CLI
    print("    3/4: Calling Claude CLI to generate frontmatter...")
    try:
        frontmatter = generate_frontmatter_with_claude_cli(pdf_text, pdf_meta)
        print(f"         [OK] Generated {len(frontmatter)} characters")

        # Validate YAML
        yaml.safe_load(frontmatter)
        print("         [OK] YAML validated")
    except Exception as e:
        print(f"         [FAIL] Error: {e}")
        return False

    # 4. Prepend to markdown
    print("    4/4: Adding frontmatter to markdown...")
    if prepend_frontmatter(markdown_path, frontmatter):
        print("         [OK] Frontmatter added successfully!")
        return True
    else:
        return False

def process_batch(markdown_dir):
    """Process all markdown files in directory that don't have frontmatter"""

    markdown_dir = Path(markdown_dir)

    # Find all markdown files (not meta.json)
    md_files = []
    for md_file in markdown_dir.rglob("*.md"):
        if '_meta.json' not in md_file.name:
            md_files.append(md_file)

    if not md_files:
        print(f"[X] No markdown files found in {markdown_dir}")
        return

    print(f"Found {len(md_files)} markdown file(s)")

    successful = 0
    failed = 0
    skipped = 0

    for md_file in md_files:
        # Try to find corresponding PDF
        # Look in parent directories
        pdf_candidates = [
            md_file.parent.parent / (md_file.stem + '.pdf'),
            md_file.parent.parent.parent / (md_file.stem + '.pdf'),
        ]

        # Also try to find by pattern matching filename
        # (marker-pdf creates long directory names)
        potential_pdf = None
        for pdf in md_file.parent.parent.parent.glob('*.pdf'):
            if md_file.stem in pdf.stem:
                potential_pdf = pdf
                break

        pdf_file = potential_pdf
        if not pdf_file:
            for candidate in pdf_candidates:
                if candidate.exists():
                    pdf_file = candidate
                    break

        if not pdf_file:
            print(f"[WARN] No PDF found for {md_file.name}, skipping")
            skipped += 1
            continue

        try:
            if process_single_pdf(pdf_file, md_file):
                successful += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"    [FAIL] Error: {e}")
            failed += 1

    print(f"\n=== Batch Complete ===")
    print(f"Successful: {successful}/{len(md_files)}")
    print(f"Skipped: {skipped}/{len(md_files)}")
    print(f"Failed: {failed}/{len(md_files)}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    if sys.argv[1] == '--batch':
        if len(sys.argv) < 3:
            print("Usage: python add-frontmatter-cli.py --batch <markdown_dir>")
            sys.exit(1)
        process_batch(sys.argv[2])
    else:
        if len(sys.argv) < 3:
            print("Usage: python add-frontmatter-cli.py <pdf_file> <markdown_file>")
            sys.exit(1)

        pdf_file = sys.argv[1]
        md_file = sys.argv[2]

        if not Path(pdf_file).exists():
            print(f"[X] PDF file not found: {pdf_file}")
            sys.exit(1)

        if not Path(md_file).exists():
            print(f"[X] Markdown file not found: {md_file}")
            sys.exit(1)

        success = process_single_pdf(pdf_file, md_file)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
