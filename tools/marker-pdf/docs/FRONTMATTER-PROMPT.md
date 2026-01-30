# PDF Frontmatter Extraction Prompt

**Purpose**: Extract metadata from academic PDF and generate YAML frontmatter for markdown files.

**Input**: First 2 pages of academic PDF
**Output**: YAML frontmatter block

---

## Prompt for Claude

```
You are extracting metadata from an academic paper PDF to generate YAML frontmatter.

INPUT:
- PDF file: [FILENAME]
- Pages to analyze: First 2 pages (contains all metadata)

TASK:
Extract the following metadata and format as YAML frontmatter:

1. **title**: Full paper title (clean, no line breaks)
2. **authors**: List of author names with affiliations
   Format: "FirstName LastName, Institution, Country"
3. **year**: Publication year (4 digits)
4. **venue**: Conference/journal name (full name, not abbreviation)
5. **doi**: DOI if present (format: "10.xxxx/xxxxx")
6. **pages**: Total page count (from PDF)
7. **abstract**: Paper abstract (optional, if space allows)
8. **keywords**: Key terms from "Keywords" or "Index Terms" section
9. **type**: Document type ("conference", "journal", "preprint", "thesis")

EXTRACTION RULES:

**Title**:
- Usually at top of first page in larger font
- Remove line breaks (rejoin multi-line titles)
- Preserve subtitle if present (use colon separator)

**Authors**:
- Format each as: "Name, Institution, Country"
- Preserve author order
- Extract affiliations from superscript numbers or footnotes
- If affiliations complex, use institution name only

**Year**:
- Check: Copyright notice, citation box, header/footer
- If multiple years (submission/publication), use publication year

**Venue**:
- Conference: Full name (e.g., "ACM International Conference on Software Engineering")
- Journal: Full name (e.g., "ACM Transactions on Software Engineering and Methodology")
- Preprint: "arXiv" or service name

**DOI**:
- Format: "10.xxxx/xxxxx" (no https://)
- Usually in: Footer, citation box, or copyright notice

**Keywords**:
- Section labeled: "Keywords", "Key Words and Phrases", "Index Terms", or "CCS Concepts"
- Keep as comma-separated list

**Type**:
- "conference" if proceedings/workshop
- "journal" if journal article
- "preprint" if arXiv/technical report
- "thesis" if PhD/Master's thesis

OUTPUT FORMAT:

```yaml
---
title: "Exact paper title here"
authors:
  - "FirstName LastName, Institution, Country"
  - "FirstName LastName, Institution, Country"
year: 2025
venue: "Full Conference or Journal Name"
doi: "10.1145/3748256"
pages: 35
type: "conference"
keywords:
  - "version control systems"
  - "software merge"
  - "conflict resolution"
abstract: |
  Paper abstract here if extracted.
  Can span multiple lines.
---
```

IMPORTANT:
- Use double quotes for string values
- Use proper YAML list syntax (- for list items)
- If field not found, omit it (don't use null or empty)
- Preserve original capitalization for names and titles
- Abstract is optional (include only if clearly identifiable)

CONFIDENCE:
For each field, if uncertain:
- Omit the field rather than guessing
- Add comment: # [field]: Could not determine from first 2 pages

Now extract frontmatter from the provided PDF pages.
```

---

## Usage Example

```python
# Read first 2 pages of PDF
import pypdfium2 as pdfium

pdf_doc = pdfium.PdfDocument("paper.pdf")
first_two_pages = [pdf_doc[0], pdf_doc[1]]

# Extract text or render to image for Claude
# Then send to Claude with the prompt above
```

---

## Post-Processing Script

After Claude generates the frontmatter, prepend it to the markdown file:

```python
def add_frontmatter(markdown_file, frontmatter_yaml):
    """Prepend YAML frontmatter to existing markdown file"""

    # Read existing markdown
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Combine frontmatter + content
    output = frontmatter_yaml + "\n\n" + content

    # Write back
    with open(markdown_file, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"✅ Frontmatter added to {markdown_file}")
```

---

## Why First 2 Pages Are Sufficient

**Page 1 typically contains**:
- ✅ Title (header)
- ✅ Authors with affiliations
- ✅ Abstract
- ✅ Keywords/CCS Concepts
- ✅ DOI (footer or citation box)
- ✅ Copyright/venue info (footer)

**Page 2 typically contains**:
- ✅ Continuation of introduction (if page 1 was full)
- ✅ Sometimes DOI in header
- Usually just confirming info from page 1

**Last pages NOT needed for frontmatter**:
- References (for bibliography, not metadata)
- Author bios (redundant with page 1 affiliations)
- Page count (can get from PDF.pages attribute)

**Exception**: If page 1 is a cover page without metadata, you might need page 2-3.

---

## Integration with marker-pdf

Can be combined with the conversion workflow:

```bash
# 1. Convert PDF with marker-pdf
marker_single "paper.pdf" --output_dir output

# 2. Extract frontmatter from first 2 pages
python extract-frontmatter.py "paper.pdf" --output frontmatter.yaml

# 3. Prepend to markdown
python add-frontmatter.py output/paper.md frontmatter.yaml
```

Or automated in batch conversion script!
