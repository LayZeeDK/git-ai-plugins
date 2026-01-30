# Manual Frontmatter Extraction Workflow

Since the automated script requires ANTHROPIC_API_KEY setup, here's a manual workflow using Claude Code directly.

## Quick Manual Process

### Step 1: Extract PDF First 2 Pages

```python
# Run in venv-marker-py312
import pypdfium2 as pdfium

pdf_file = "Towards a feasible evaluation function for search-based merge conflict resolution (2025) by Campos Junior, de Menezes, Barros, van der Hoek, Murta [camposjunior2025].pdf"
doc = pdfium.PdfDocument(pdf_file)

# Get metadata
meta = doc.get_metadata_dict()
print("PDF Metadata:")
print(f"  Title: {meta.get('Title')}")
print(f"  Year: {meta.get('CreationDate', '')[2:6]}")
print(f"  Pages: {len(doc)}")
print(f"  Subject: {meta.get('Subject')}")

# Extract first 2 pages
print("\n=== PAGE 1 ===")
print(doc[0].get_textpage().get_text_range()[:2000])
print("\n=== PAGE 2 ===")
print(doc[1].get_textpage().get_text_range()[:2000])
```

### Step 2: Ask Claude Code

Paste the output above and ask:

```
Based on this PDF metadata and first 2 pages text, generate YAML frontmatter with:
- title
- authors (list with affiliations)
- year
- venue
- doi
- pages
- type
- keywords

Format as valid YAML between --- markers.
```

### Step 3: Prepend to Markdown

Copy Claude's YAML response and:

```python
# Prepend frontmatter
frontmatter = '''---
title: "..."
authors:
  - "..."
...
---'''

markdown_file = "output-marker-native/.../paper.md"

with open(markdown_file, 'r', encoding='utf-8') as f:
    content = f.read()

with open(markdown_file, 'w', encoding='utf-8') as f:
    f.write(frontmatter + '\n\n' + content)

print("Frontmatter added!")
```

---

## For Automated Script

To use `add-frontmatter.py`, set API key first:

```powershell
# PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Git Bash
export ANTHROPIC_API_KEY="sk-ant-..."

# Or create .env file
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

Then run:
```bash
python add-frontmatter.py "paper.pdf" "output/paper.md"
```

---

## Alternative: Template-Based

For batch processing without API costs, use a template:

```python
def generate_template_frontmatter(pdf_path):
    """Generate frontmatter from PDF metadata + filename"""
    import pypdfium2 as pdfium

    doc = pdfium.PdfDocument(pdf_path)
    meta = doc.get_metadata_dict()

    # Parse filename for authors (crude but works)
    filename = Path(pdf_path).stem
    if " by " in filename:
        title_part = filename.split(" by ")[0]
        authors_part = filename.split(" by ")[1].split("[")[0]
        authors = [a.strip() for a in authors_part.split(",")]
    else:
        authors = []

    year = meta.get('CreationDate', '')[2:6] if meta.get('CreationDate') else None

    frontmatter = f"""---
title: "{meta.get('Title', title_part).strip()}"
authors:{chr(10).join(f'  - "{a}"' for a in authors) if authors else chr(10) + '  - "Unknown"'}
year: {year or 'Unknown'}
pages: {len(doc)}
---"""

    return frontmatter
```

This creates basic frontmatter from available data without API calls!
