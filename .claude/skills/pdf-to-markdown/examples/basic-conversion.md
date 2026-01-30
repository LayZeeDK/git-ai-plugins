# Example: Basic PDF Conversion

## User Request
"Convert the camposjunior2025 PDF to markdown"

## Skill Response

### Step 1: Locate PDF
```
Found: plugins/lz-git.conflict/research/Towards a feasible evaluation function for search-based merge conflict resolution (2025) by Campos Junior, de Menezes, Barros, van der Hoek, Murta [camposjunior2025].pdf
```

### Step 2: Run Conversion
```bash
cd plugins/lz-git.conflict/research
export CRYPTOGRAPHY_OPENSSL_NO_LEGACY=1

./venv-marker-py312/Scripts/marker_single \
  "Towards a feasible evaluation function for search-based merge conflict resolution (2025) by Campos Junior, de Menezes, Barros, van der Hoek, Murta [camposjunior2025].pdf" \
  --output_format markdown \
  --output_dir output-marker-native
```

### Step 3: Monitor Progress
```
Loaded layout model ✅
Loaded texify model ✅
Loaded recognition model ✅
Loaded table recognition model ✅
Loaded detection model ✅
Recognizing layout: 100% (35 pages)
Total time: 184.82 seconds
```

### Step 4: Verify Output
```
Output: output-marker-native/Towards a feasible.../
  - Paper.md (632 lines, 37KB)
  - Paper_meta.json (metadata)
  - Images: _page_X_Picture_Y.jpeg

Sections found:
  - Introduction
  - Background
  - Materials and Methods
  - Results (with 6 RQs)
  - Discussion
  - Related Work
  - Conclusion
  - Acknowledgments
  - References

Quality: Excellent ✅
```

### Step 5: Offer Frontmatter
```
Question: Would you like to add YAML frontmatter with metadata?
  - Yes, add frontmatter (Recommended)
  - No, markdown is fine as-is
  - Show me what frontmatter would include

User selects: Yes

Running: python add-frontmatter-cli.py ...
Result: Frontmatter added (title, authors, venue, DOI, keywords)
```

### Final Output
```markdown
---
title: "Towards a feasible evaluation function for search-based merge conflict resolution"
authors:
  - "Heleno de S. Campos Junior, Universidade Federal Fluminense, Brazil"
  ...
year: 2025
venue: "ACM Transactions on Software Engineering and Methodology"
doi: "10.1145/3748256"
pages: 35
---

HELENO DE S. CAMPOS JUNIOR, Universidade Federal Fluminense, Brazil
...
```

## Result Summary

✅ **Conversion successful!**
- Input: 35-page PDF
- Output: 653-line Markdown (with frontmatter)
- Time: 184.82 seconds (~5.3 sec/page)
- Quality: Publication-ready
- All sections preserved
- References formatted
- Ready for research analysis
