---
name: pdf-to-markdown
description: Convert academic PDFs to Markdown using native ARM64 marker-pdf
version: 1.0.0
when-to-use: |
  Use this skill when the user asks to:
  - Convert a PDF to Markdown
  - Extract text from a research paper PDF
  - Process a PDF document
  - "marker" or "marker-pdf" a document

  If no PDF is mentioned, suggest research papers from plugins/lz-git.conflict/research/
model: sonnet
tools:
  - Bash
  - Read
  - Write
  - Glob
  - AskUserQuestion
---

# PDF to Markdown Conversion Skill

Convert academic research PDFs to high-quality Markdown using the native ARM64 marker-pdf setup.

## Prerequisites Check

Before starting, verify the marker-pdf setup exists:

1. Check if `tools/marker-pdf/venv-marker-py312/` exists (use git repo root)
2. Check if `tools/marker-pdf/setup/apply-patches.py` exists
3. If missing, guide user to run setup scripts first

**Check command**:
```bash
REPO_ROOT=$(git rev-parse --show-toplevel)
test -d "$REPO_ROOT/tools/marker-pdf/venv-marker-py312" && echo "✓ venv exists"
test -f "$REPO_ROOT/tools/marker-pdf/setup/apply-patches.py" && echo "✓ patches exist"
```

## Workflow

### Step 1: Identify PDF File

**If user specified a PDF**:
- Use the provided path
- Verify the file exists

**If no PDF specified**:
- Search for PDFs in `plugins/lz-git.conflict/research/`
- Exclude subdirectories like `repos/`, `output-*/`, `papers/*/`
- Show user a list of available research papers
- Use AskUserQuestion to let them select which PDF to convert

**PDF Discovery**:
```bash
find plugins/lz-git.conflict/research -maxdepth 1 -name "*.pdf" -type f
```

### Step 2: Determine Output Location

Ask user where to save the output:
- Default: `plugins/lz-git.conflict/research/output-marker-native/`
- Alternative: Custom directory

Use AskUserQuestion with options:
- "output-marker-native/ (default)" (Recommended)
- "papers-markdown/ (batch location)"
- "Custom directory (specify path)"

### Step 3: Run marker-pdf Conversion

**Command**:
```bash
cd plugins/lz-git.conflict/research

# Set required environment variable
export CRYPTOGRAPHY_OPENSSL_NO_LEGACY=1

# Get repo root and construct path to marker tool
REPO_ROOT=$(git rev-parse --show-toplevel)
MARKER_CMD="${REPO_ROOT}/tools/marker-pdf/venv-marker-py312/Scripts/marker_single"

# Run conversion
"$MARKER_CMD" \
  "<pdf_file>" \
  --output_format markdown \
  --output_dir <output_directory>
```

**Monitor**:
- Run in background for large PDFs
- Show progress updates
- Report when complete

**Expected performance**:
- Simple papers: ~5 sec/page
- Complex papers: ~30 sec/page
- All 5 ML models load (layout, texify, recognition, table_rec, detection)

### Step 4: Check Output Quality

After conversion completes:

1. **Verify output exists**:
   - Check for `.md` file in output directory
   - Check for `_meta.json` file

2. **Quick quality check**:
   - Count lines in markdown
   - Preview first 100 lines
   - Check for proper headers (#, ##, ###)
   - Verify sections are present

3. **Report to user**:
   - File location
   - File size and line count
   - Conversion time
   - Any warnings or issues

### Step 5: Check for Listing OCR Issues (NEW)

After conversion completes, automatically check for poorly OCR'd listings:

```bash
REPO_ROOT=$(git rev-parse --show-toplevel)

# Check for OCR artifacts in code listings
PYTHONIOENCODING=utf-8 "$REPO_ROOT/tools/marker-pdf/venv-marker-py312/Scripts/python.exe" \
  "$REPO_ROOT/tools/marker-pdf/scripts/detect-bad-listings.py" \
  "<output_markdown_file>"
```

**If listings with OCR artifacts are found**:

Ask user with AskUserQuestion:
1. "Yes, fix automatically" (Recommended) - Run auto-fix-listings.py
2. "No, leave as-is" - Keep OCR'd text
3. "Show me the issues first" - Display detection results

**If user chooses to fix**:
```bash
PYTHONIOENCODING=utf-8 "$REPO_ROOT/tools/marker-pdf/venv-marker-py312/Scripts/python.exe" \
  "$REPO_ROOT/tools/marker-pdf/scripts/auto-fix-listings.py" \
  "<pdf_file>" \
  "<output_markdown_file>" \
  "<output_directory>/<basename>_meta.json" \
  "<output_directory>-fixed"
```

**Report**:
- ✅ Number of listings auto-fixed
- 🖼️ Image locations and sizes
- 📄 Fixed markdown location
- 💡 Detection method: OpenCV monochrome (99.8% accurate)

### Step 6: Add Frontmatter (Automatic)

Always add YAML frontmatter with structured metadata to the converted markdown:

```bash
cd plugins/lz-git.conflict/research

# Check if frontmatter already exists
FIRST_LINE=$(head -1 <markdown_file>)

if [[ "$FIRST_LINE" == "---" ]]; then
  echo "✓ Frontmatter already present"
else
  # Get repo root and construct path to script
  REPO_ROOT=$(git rev-parse --show-toplevel)

  # Add frontmatter automatically
  # marker-pdf often auto-generates frontmatter, but if missing:
  python "$REPO_ROOT/tools/marker-pdf/scripts/add-frontmatter-cli.py" "<pdf_file>" "<markdown_file>"

  echo "✓ Frontmatter added"
fi
```

**Note**: marker-pdf v1.2.7 often includes frontmatter automatically in its output.
Verify with `head -20 <markdown_file>` to check for `---` delimiters at the start.

### Step 7: Final Summary

Provide user with:
- ✅ Conversion success confirmation
- 📁 Output file path
- 📊 Stats (pages, lines, time)
- 🔍 Quality assessment:
  - Sections found, formatting quality
  - Frontmatter present (should always be yes)
  - Listing quality (if OCR artifacts detected and fixed)
- 💡 Next steps suggestions:
  - View the markdown
  - Compare with original PDF
  - Convert more PDFs
  - Use for research/analysis

**Example summary**:
```
✅ PDF Conversion Complete!

📄 Output: output-marker-native/paper.md (652 lines)
📊 Stats: 35 pages, 29 sections, 16 figures extracted
✅ Frontmatter: Present with full metadata
⚠️ Listings: 2 detected with OCR artifacts → Auto-fixed with images
🖼️ Images: 16 figures + 2 listings = 18 total

💡 Next: Review the markdown in your editor
```

## Error Handling

### Common Issues

**Issue 1: venv not found**
```
Solution: Guide user to run setup:
  cd tools/marker-pdf
  ./setup/setup-windows-arm64.ps1  # or .sh
  python setup/apply-patches.py venv-marker-py312
```

**Issue 2: CRYPTOGRAPHY_OPENSSL_NO_LEGACY not set**
```
Error: OpenSSL 3.0's legacy provider failed to load
Solution: Export environment variable before running
```

**Issue 3: Models fail to load**
```
Solution: Clear Python cache
  find tools/marker-pdf/venv-marker-py312/Lib/site-packages -name __pycache__ -type d -exec rm -rf {} +
```

**Issue 4: PDF not found**
```
Solution: Use Glob tool to find PDFs, show user available files
```

**Issue 5: Path too long on Windows**
```
Solution: Use shorter output directory name or move closer to drive root
```

## Example Interaction

**User**: "Convert camposjunior2025.pdf to markdown"

**Skill Actions**:
1. ✅ Find PDF: `plugins/lz-git.conflict/research/Towards a feasible...camposjunior2025].pdf`
2. ✅ Run marker-pdf conversion to `output-marker-native/`
3. ✅ Monitor progress (shows: 35 pages processed in ~3 minutes)
4. ✅ Report output: 632 lines, all sections present
5. ❓ Ask: "Add YAML frontmatter with metadata?"
6. ✅ If yes: Extract and prepend frontmatter
7. ✅ Show final file location and stats

**User**: "Convert a research paper"

**Skill Actions**:
1. 🔍 Search for PDFs in research directory
2. 📋 Show list of available papers
3. ❓ Ask user to select which one
4. ✅ Proceed with conversion workflow

## Files Used

- **Marker venv**: `${REPO_ROOT}/tools/marker-pdf/venv-marker-py312/`
- **Conversion command**: `marker_single` (in venv Scripts directory)
- **Frontmatter script**: `${REPO_ROOT}/tools/marker-pdf/scripts/add-frontmatter-cli.py`
- **Documentation**: `${REPO_ROOT}/tools/marker-pdf/README.md`

Note: `REPO_ROOT` is obtained via `git rev-parse --show-toplevel`

## Performance Reference

Based on tested conversions:
- Retrospective-ChangeDistiller: 6 pages in 29s (4.8 sec/page)
- camposjunior2025: 35 pages in 185s (5.3 sec/page)

Native ARM64 is ~6x faster than Docker x86_64 emulation!
