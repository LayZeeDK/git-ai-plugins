# PDF to Markdown Conversion Plan

## Current Status

### Pilot Document: camposjunior2025.pdf ✅ APPROVED
- **Pages rendered**: 35 pages at 3x scale
- **Figures extracted**: 17 figures + 2 listings (all bounding boxes refined)
- **Text converted**: ~119KB markdown
- **Mermaid diagram**: Created for Figure 2
- **Figure 1**: Converted to headers + code blocks
- **Listings 4-5**: Code diff tables with color markup + image fallback
- **All figures verified**: Pass review checklist

### Key Lessons from Pilot 1

#### Bounding Box Guidelines
1. **Header zone extends to y=165**: Page headers include page number and running title
2. **Figures start at y=240-300**: Well below header zone
3. **Multi-panel figures need x=60**: To capture left y-axis labels
4. **Fine-tuning requires 10-20 pixel increments**: Balance between caption exclusion and axis inclusion
5. **Caption zone is tight**: Often only 15-30 pixels between figure bottom and caption text
6. **Output path**: Script outputs to `images/` subdirectory

#### Figure Representation Strategies
| Content Type | Approach |
|--------------|----------|
| Flowcharts/diagrams | Mermaid (e.g., Figure 2) |
| Code-heavy figures | Headers + code blocks (e.g., Figure 1) |
| Charts/graphs/plots | Image only |
| Code diff tables | HTML markup + "View as image" fallback |

Always provide "View as image" collapsible after markdown representation.

#### Code Listings
1. **Line numbers**: Consistent spacing (e.g., `1   code`)
2. **Continuation lines**: Use `↪` arrows after indentation before continued text
3. **Diff color convention**: `<b>bold</b>`=green (additions), `<i>italic</i>`=black (matches), `<del>strikethrough</del>`=red (deletions)

#### Tables
- **Multi-row headers**: Flatten to single row with combined names (e.g., "Worst: Parents" instead of colspan)

#### Special Characters
- **Greek letters**: Italicize (e.g., *ρ*)

### Refined Bbox Guidelines by Figure Type

| Type | x | width | y | height |
|------|---|-------|---|--------|
| Single boxplot | 105 | 1250 | 260-300 | 600-720 |
| Scatter plot | 105 | 1250 | 260 | 800-900 |
| Multi-panel (2 plots) | 60 | 1340 | 260-280 | 450-500 |
| Heatmap grid (4 panels) | 60 | 1340 | 280 | 900-920 |
| Histogram | 105 | 1250 | 260 | 680-720 |
| Flowchart/diagram | 80 | 1300 | 260 | varies |
| Table figure | 105 | 1250 | 240 | varies |
| Two-figure page (fig 2) | varies | varies | 1100+ | varies |

---

## Phase 1: PDF Conversion ⚠️ UPDATED APPROACH

> **Note:** The Node.js approach described below was experimental and has been **archived** (see `NODE_JS_PDF_EXPERIMENTS.md`). After 79 hours of development and extensive testing, we adopted **marker-pdf** (vision transformers) as the primary conversion tool for superior quality and maintainability.

### Step 1.1: Pilot 1 (camposjunior2025.pdf) - Node.js ✅ COMPLETE (Archived)
- [x] Render 35 pages at 3x scale
- [x] Create figures-manifest.json with 17 figure bboxes
- [x] Iteratively refine all bounding boxes
- [x] Verify all 17 figures pass review checklist
- [x] Create Mermaid diagram for Figure 2

**Result:** Successful conversion but required extensive manual effort. See `papers/search-based-2025.md` (113KB) for output.

### Step 1.2: NEW APPROACH - marker-pdf + Automated Listing Fixes ✅ ADOPTED

**Current Workflow**:
```bash
# 1. Convert PDF with marker-pdf (ARM64 native)
marker_single paper.pdf output/ --batch_multiplier 4

# 2. Automatically fix listings (OpenCV detection)
/fix-markdown-listings output/paper.md

# 3. Add frontmatter (automated extraction)
# (Future: /pdf-to-markdown skill with auto-frontmatter)
```

**Benefits:**
- 40 minutes per paper (vs 4 hours with Node.js)
- 98% accuracy out-of-box
- Minimal manual intervention
- Scales to batch processing

### Step 1.3: Pilot 1 Follow-up - Refine marker-pdf Workflow ⏳ NEXT

**Goal:** Improve marker-pdf workflow to match or exceed the quality of the Node.js Pilot 1 output (`papers/search-based-2025.md`)

**Tasks:**
- [ ] Convert `camposjunior2025.pdf` with marker-pdf workflow
- [ ] Compare output to existing `papers/search-based-2025.md` (Node.js baseline)
- [ ] Identify quality gaps (figures, listings, tables, equations, formatting)
- [ ] Iterate on workflow improvements:
  - [ ] Listing detection and OCR fixes
  - [ ] Figure extraction and placement
  - [ ] Table formatting
  - [ ] Frontmatter automation
  - [ ] Math equation rendering
- [ ] Document workflow refinements in marker-pdf tools/
- [ ] Validate final output matches or exceeds Node.js quality

**Success Criteria:**
- ✅ All 17 figures correctly extracted and placed
- ✅ Listings 4-5 (diff visualizations) properly handled
- ✅ Tables accurately formatted
- ✅ Frontmatter complete and accurate
- ✅ Overall markdown quality ≥ Node.js output
- ✅ Reproducible workflow for batch processing

**Why This Matters:** Ensures marker-pdf workflow is production-ready before converting 13+ papers.

### Step 1.4: Pilot 2 (life-cycle-2019) - marker-pdf Validation ⏳ PENDING

**Goal:** Validate refined marker-pdf workflow on a second paper with different characteristics

**Previous Node.js Attempt (Archived):**
- [x] Tested Node.js pipeline - identified scalability issues
- [x] Output was untracked experimental files (deleted during cleanup)

**marker-pdf Validation:**
- [ ] Convert `life-cycle-2019.pdf` (or `Nelson2019*.pdf`) with refined marker-pdf workflow
- [ ] Apply `/fix-markdown-listings` if needed
- [ ] Add frontmatter
- [ ] Validate quality meets success criteria from Step 1.3
- [ ] Commit final output to repository

**Success Criteria:**
- ✅ Workflow works on different paper type/layout
- ✅ Quality comparable to Pilot 1
- ✅ No paper-specific heuristics needed
- ✅ Conversion time ≤ 1 hour

### Step 1.5: Batch Process Remaining 13 PDFs
**Prerequisites:** Steps 1.3 and 1.4 complete (workflow refined and validated)

For each PDF:
1. Convert with marker-pdf: `marker_single <pdf> output/ --batch_multiplier 4`
2. Fix listings: `/fix-markdown-listings output/<paper>.md`
3. Add frontmatter (manual or using `/pdf-to-markdown` skill)
4. Review output quality
5. Commit to repository

**Expected Timeline:** 13 papers × ~45 minutes = ~10 hours total

---

## Phase 2: Research Synthesis

### Step 2.1: Create SYNTHESIS.md
Consolidate findings from all 16 analysis documents:
- `research/analysis/*.md` - existing analysis files

Structure:
```markdown
# Research Synthesis

## Conflict Detection Techniques
- [findings from papers]

## Resolution Strategies
- [findings from papers]

## Evaluation Methods
- [findings from papers]

## Implementation Patterns
- [findings from papers]

## Open Problems
- [gaps identified across papers]
```

### Step 2.2: Extract Actionable Improvements
From the 76 actionable improvements mentioned in analysis files:
- Group by feature area
- Prioritize by impact and feasibility
- Cross-reference with existing ATTRIBUTIONS.md

---

## Phase 3: Feature Roadmap

### Step 3.1: Create FEATURES.md
```markdown
# Feature Clusters

## Cluster 1: Detection Enhancement
- Feature A (paper X, paper Y)
- Feature B (paper Z)

## Cluster 2: Resolution Strategies
- ...

## Cluster 3: Evaluation & Metrics
- ...
```

### Step 3.2: Initialize GSD Planning Structure
```
.planning/
├── PROJECT.md       # Project overview, goals, constraints
├── REQUIREMENTS.md  # Functional and non-functional requirements
├── ROADMAP.md       # Phased implementation plan
├── STATE.md         # Current progress, blockers
└── phases/
    ├── phase-1/     # Detection improvements
    ├── phase-2/     # Resolution strategies
    └── phase-3/     # Evaluation framework
```

---

## Tools (Updated)

### Archived Node.js Scripts (See `NODE_JS_PDF_EXPERIMENTS.md`)
- `scripts/render-pdf-pages.mjs` - Rendered PDF pages as PNG (deleted)
- `scripts/crop-figures.mjs` - Cropped figures using bbox manifest (deleted)
- `scripts/generate-markdown.mjs` - Embedded figures in markdown (deleted)
- 44 additional experimental scripts (all archived)

### Current Tools (marker-pdf Workflow)
- **marker-pdf** - Vision transformer-based PDF conversion (Python, ARM64)
- **`/fix-markdown-listings`** - Claude skill for automated listing detection and fixing (OpenCV)
- **`/pdf-to-markdown`** - Claude skill for full PDF conversion workflow
- **marker-pdf tools/** - Setup and configuration scripts in `tools/marker-pdf/`

---

## Next Actions

1. ~~**Step 1.1**: Pilot 1 (Node.js)~~ ✅ COMPLETE (Node.js approach)
2. ~~**Step 1.2**: Adopt marker-pdf~~ ✅ COMPLETE (workflow defined)
3. **NEXT**: **Step 1.3 - Pilot 1 Refinement** - Re-convert camposjunior2025.pdf with marker-pdf and iterate until quality matches Node.js baseline
4. **Then**: **Step 1.4 - Pilot 2 Validation** - Convert life-cycle-2019 with refined workflow to validate on second paper
5. **Then**: **Step 1.5 - Batch Processing** - Convert remaining 13 PDFs with validated workflow (~10 hours)
6. **Future**: **Phase 2** - Research synthesis (create SYNTHESIS.md)
7. **Future**: **Phase 3** - Feature roadmap (create FEATURES.md, initialize GSD structure)
