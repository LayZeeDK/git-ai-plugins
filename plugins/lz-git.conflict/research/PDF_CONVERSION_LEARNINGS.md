# PDF to Markdown Conversion: Windows ARM64 Learnings

**Device**: Surface Laptop 7 (Snapdragon X Elite, 32GB RAM)
**Date**: January 2025
**Goal**: Find a native PDF-to-Markdown converter for academic papers

---

## Executive Summary

**Marker remains the best option** for converting academic PDFs to Markdown, despite the complex installation on Windows ARM64. Alternative tools either fail to install or produce significantly lower quality output.

---

## Tools Evaluated

### 1. MinerU ❌ Failed (Tested January 2025)

**Promise**: High-quality PDF extraction with ML models, recommended for academic papers.

**Reality**: Installation fails immediately due to PyTorch Windows ARM64 gap:
```
torch>=2.6.0 has no wheels with a matching platform tag (e.g., `win_arm64`)
```

**Available PyTorch platforms** (as of v2.10.0):
- `manylinux_2_28_aarch64` (Linux ARM64) ✅
- `manylinux_2_28_x86_64` (Linux x64) ✅
- `macosx_11_0_arm64` (Apple Silicon) ✅
- `win_amd64` (Windows x64) ✅
- `win_arm64` (Windows ARM64) ❌ **Missing**

**Conclusion**: MinerU cannot be installed on Windows ARM64 until PyTorch publishes `win_arm64` wheels. This is a PyTorch ecosystem limitation, not a MinerU issue.

---

### 2. Docling (IBM/LF AI) ❌ Failed

**Promise**: Explicit ARM64 support, simple installation, IBM backing.

**Reality**: Installation fails due to dependency chain:
```
Failed to build: docling-parse, opencv-python, Shapely
```

**Root causes**:
- `opencv-python`: No ARM64 wheel; source build fails on ARM64 NEON intrinsics
- `Shapely`: Requires GEOS library not available on Windows ARM64
- `docling-parse`: Native code dependencies without ARM64 wheels

**Conclusion**: Despite documentation claiming ARM64 support, the dependency ecosystem isn't ready.

---

### 3. PyMuPDF4LLM ❌ Build Fails (Tested January 2025)

**Status**: No `win_arm64` wheel on PyPI (only `win_amd64` and `win32`).

**Source build attempted**: Fails with multiple issues:
```
platform.machine()='ARM64' → but builds for "Release|x64"
MSB8020: The build tools for Visual Studio 2019 (Platform Toolset = 'v142') cannot be found
```

**Root causes**:
1. No prebuilt ARM64 wheels available
2. Source build scripts assume x64 even on ARM64 machines
3. Requires VS 2019 build tools (v142) even with VS 2022 installed

**Source**: [PyMuPDF PyPI](https://pypi.org/project/PyMuPDF/#files)

**Conclusion**: PyMuPDF source builds don't support ARM64 compilation. Would require significant patches to the build system.

---

### 4. pdfplumber ✅ Installs, ⚠️ Poor Quality

**Installation**: Works with a workaround:
```powershell
# Must install cryptography from pre-built wheel first
pip install --only-binary :all: cryptography
pip install pdfplumber
```

**Key settings discovered**:
| Setting | Default | Optimal | Effect |
|---------|---------|---------|--------|
| `x_tolerance` | 3 | 1 | Proper word spacing in justified text |
| Column detection | Per-page | Document-wide from page 2+ | Title pages have full-width headers |
| Right margin | 5px | 15px | Captures trailing characters |

**Output quality comparison**:

| Aspect | pdfplumber | Marker |
|--------|------------|--------|
| Two-column reflow | ❌ Sequential columns | ✅ Natural paragraph flow |
| Title extraction | ❌ Fragmented | ✅ Complete |
| Markdown formatting | ⚠️ Basic headings | ✅ Italics, bold, lists |
| Image extraction | ❌ None | ✅ Yes |
| References | ❌ Plain text | ✅ Formatted list |

**Verdict**: Usable for quick extraction but requires significant post-processing for academic papers.

---

### 5. Marker ✅ Best Quality (Current Setup)

**Installation**: Complex but documented in `MARKER_SETUP_NOTES.md` (700+ lines of patches).

**Output quality**: Publication-ready Markdown with:
- Proper two-column text reflow
- Rich formatting (italics, bold, heading levels)
- Image extraction
- Structured references

**Why it's better**: Uses ML-based layout detection (surya-ocr) that understands document structure and reading order, not just geometry.

---

## Key Technical Learnings

### 1. Windows ARM64 Python Ecosystem Status (January 2025)

| Package | ARM64 Wheel | Notes |
|---------|-------------|-------|
| PyTorch | ❌ No | No `win_arm64` wheels (Linux/macOS only) |
| cryptography | ✅ Yes | v46.0.3+, use `--only-binary` |
| Pillow | ✅ Yes | Works out of box |
| opencv-python | ❌ No | Build fails on ARM64 intrinsics |
| Shapely | ❌ No | Requires GEOS library |
| PyMuPDF | ❌ No | Only x64/x86 wheels; source build hardcoded x64 |

**Correction**: Earlier notes suggested PyTorch had CPU ARM64 wheels since April 2025. Testing confirms this applies to **Linux ARM64** (`manylinux_2_28_aarch64`) and **macOS ARM64** (`macosx_11_0_arm64`), but **NOT Windows ARM64** (`win_arm64`).

### 2. Two-Column PDF Extraction Challenges

**Problem**: Academic papers use two-column layouts with:
- Full-width titles and headers on page 1
- Full-width headers/footers on all pages
- Justified text with variable character spacing

**Geometric extraction (pdfplumber) limitations**:
1. Detects columns but extracts left-then-right sequentially
2. Title pages confuse column detection
3. Justified text may lack explicit space characters

**ML-based extraction (Marker) advantages**:
1. Understands logical reading order across columns
2. Merges columns into natural paragraph flow
3. Handles complex layouts (figures, tables, captions)

### 3. Character Spacing in PDFs

PDFs don't always store explicit space characters. Spacing can be:
- Explicit space glyphs
- Positional gaps between characters
- Kerning adjustments

**Solution for pdfplumber**: Use `x_tolerance=1` (stricter than default 3) to detect word boundaries in justified text.

---

## Recommendations

### For Windows ARM64 Users

1. **Use Marker with WSL2/Docker** if quality matters
2. **Use pdfplumber** only for quick text extraction where formatting doesn't matter
3. **Wait** for the ARM64 ecosystem to mature before expecting native tools

### For This Project

Continue using the existing setup:
- **Marker** (via patched native install or Docker) for PDF conversion
- **Node.js scripts** for post-processing
- **Claude** for table/listing transcription where needed

---

## Files in This Research Directory

| File/Directory | Purpose |
|----------------|---------|
| `output-marker-native/` | Marker conversion output (high quality) |
| `MARKER_SETUP_NOTES.md` | Installation patches for Marker on ARM64 |
| `scripts/` | Node.js post-processing scripts |
| `papers/` | Source PDFs and intermediate files |

---

## Conclusion

The Windows ARM64 Python ecosystem is still maturing. PyTorch only has ARM64 wheels for Linux and macOS, **not Windows**. Many computer vision and document processing libraries lag behind. For academic PDF conversion, the quality gap between ML-based tools (Marker) and geometric extraction (pdfplumber) is significant enough to justify the complex Marker installation.

**Key insight**: Document structure understanding requires ML, not just geometry. pdfplumber can extract text accurately but cannot reconstruct the logical reading order of a two-column academic paper.
