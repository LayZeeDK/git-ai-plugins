# GumTree Analysis: Fine-grained and Accurate Source Code Differencing (2014)

**Paper**: Falleri, Morandat, Blanc, Martinez, Monperrus (2014)
**Relevance to**: lz-git.conflict plugin - Git merge conflict resolution using semantic analysis

---

## Key Findings

### Core Algorithm Approach

GumTree introduces a **two-phase AST differencing algorithm** designed to reflect developer intent rather than finding theoretically shortest edit scripts:

1. **Top-down phase**: Greedy search for isomorphic subtrees of decreasing height (anchor mappings)
2. **Bottom-up phase**: Container mappings based on common descendants, followed by recovery mappings using optimal algorithms on small subtrees

### Performance Characteristics

- **Complexity**: O(n²) worst-case, where n = max(|T1|, |T2|)
- **Practical speed**: 20ms mean on Java files, 74ms on JavaScript files
- **Memory**: Works within 4GB RAM (unlike RTED which fails ~5% of cases)
- **Scalability**: Handles fine-grained ASTs with thousands of nodes

### Empirical Validation

- **Manual evaluation**: 95.1% "good job" rating from 3 independent raters on 144 file pairs
- **Automated evaluation**: 12,792 differencing scenarios
  - Finds more mappings than ChangeDistiller in 65.49% of cases (fine-grained ASTs)
  - Produces shorter edit scripts in 80.97% of cases
  - Better at detecting move operations (52 cases with GT-only moves vs 1 opposite)

---

## Applicable Techniques

| Technique | Description | Application to Conflict Resolution | Implementation Priority |
|-----------|-------------|-----------------------------------|------------------------|
| **Height-based matching** | Match subtrees starting from greatest height, using isomorphism check | Identify unchanged code blocks in BASE/OURS/THEIRS to anchor conflict analysis | HIGH |
| **Dice coefficient** | Measure similarity: `dice(t1,t2,M) = 2×|common|/(|s1|+|s2|)` | Quantify how similar conflicting regions are; helpful for confidence scoring | HIGH |
| **Container mappings** | Match parent nodes when descendants have significant common anchors | Match containing functions/classes even when they have conflicts inside | MEDIUM |
| **Recovery mappings** | Apply optimal algorithm (RTED) on small unmatched subtrees (< 100 nodes) | Fine-grained matching within conflict regions after coarse matching | MEDIUM |
| **Move detection** | Explicitly track node movements, not just add/delete | Detect when code moved between branches (common in refactoring conflicts) | LOW |
| **Two-phase approach** | Coarse-to-fine: big structures first, then details | First identify conflict boundaries, then analyze internal structure | HIGH |

---

## Actionable Improvements

### 1. Implement Height-Indexed Matching for Conflict Analysis

**Current state**: Plugin likely uses line-based or simple AST comparison
**Improvement**: Add height-based subtree matching to identify "anchor" code blocks that are identical across BASE/OURS/THEIRS

```javascript
// Pseudocode for conflict analysis
function analyzeConflict(base, ours, theirs) {
  // Phase 1: Find anchor mappings (unchanged code)
  const anchors = findIsomorphicSubtrees(base, ours, theirs, minHeight=2);

  // Phase 2: Container mappings around conflicts
  const containers = findContainerMappings(base, ours, theirs, anchors, minDice=0.5);

  // Phase 3: Recovery mappings in conflict regions
  const details = findRecoveryMappings(base, ours, theirs, containers, maxSize=100);

  return { anchors, containers, details };
}
```

**Expected benefit**: Better understanding of conflict context, especially what *didn't* change

---

### 2. Use Dice Coefficient for Conflict Similarity Scoring

**Current state**: Conflicts are likely treated as binary (conflict/no-conflict)
**Improvement**: Compute dice coefficient between OURS/THEIRS relative to BASE to quantify conflict severity

```javascript
function assessConflictDifficulty(base, ours, theirs, mappings) {
  const oursVsBase = dice(ours, base, mappings);
  const theirsVsBase = dice(theirs, base, mappings);
  const oursVsTheirs = dice(ours, theirs, mappings);

  // High score = easy conflict (parties agree more than disagree)
  // Low score = hard conflict (parties made very different changes)
  return {
    severity: 1 - oursVsTheirs,
    oursDeviation: 1 - oursVsBase,
    theirsDeviation: 1 - theirsVsBase
  };
}
```

**Expected benefit**: Prioritize which conflicts need human review vs. can be auto-resolved

---

### 3. Adopt Recommended Thresholds

GumTree paper recommends empirically-validated thresholds:

- **minHeight = 2**: Avoid matching single identifiers everywhere
- **minDice = 0.5**: Below 50% common nodes, containers are probably different
- **maxSize = 100**: Limit cubic algorithm to avoid performance issues

**Action**: Expose these as configurable parameters in plugin with these defaults

---

### 4. Detect Move Operations in Conflicts

**Current state**: Plugin likely sees moved code as delete+add
**Improvement**: Implement move detection to recognize when both branches moved the same code

**Use case**: Branch A refactors function from file1.js → utils.js; Branch B modifies same function. Instead of showing delete+add conflict, show "moved and modified" conflict.

**Implementation**: After finding mappings, detect when matched node has different parent in OURS vs THEIRS

---

### 5. Leverage Fine-Grained ASTs

**Key insight from paper**: GumTree performs **significantly better** on fine-grained ASTs than coarse-grained ones
- Fine-grained: Every expression is a node (e.g., `InfixExpression:+`, `NumberLiteral:1`)
- Coarse-grained: Whole statements are nodes (e.g., `return "Foo!" + i;` as single node)

**Recommendation**: Ensure lz-git.conflict parser generates fine-grained ASTs, not just statement-level ASTs

---

### 6. Implement Two-Phase Analysis for Conflict Regions

**Application to conflicts**:

```
BASE:    function foo(x) { return x * 2; }
OURS:    function foo(x) { return x * 3; }  // Changed multiplier
THEIRS:  function foo(y) { return y * 2; }  // Renamed parameter

Phase 1 (top-down): Match function declaration node, parameter type, return statement structure
Phase 2 (bottom-up): Container mapping on function body
                     Recovery mappings on expression details (multiplication vs parameter name)

Result: Identify this as TWO independent changes that both can be applied
        → Auto-resolve to: function foo(y) { return y * 3; }
```

---

## Anti-Patterns to Avoid

### 1. **Don't Optimize for Shortest Edit Script**

**Quote from paper**: "She [the developer] is never interested in the theoretical shortest edit script. She is rather interested in having an edit script that reflects well the actual changes that happened."

**Application**: When resolving conflicts, don't aim for minimal diff. Aim for *semantically meaningful* resolution that matches developer intent.

**Example**: If both branches reformatted code differently, don't try to merge formatting changes character-by-character. Pick one formatting style consistently.

---

### 2. **Don't Use Cubic Algorithms on Large Subtrees**

**Quote**: "The best known algorithm with add, delete and update actions has a O(n³) time complexity... RTED undergoes out of memory errors in 5% of cases and timeouts in 12% of cases."

**Application**: Limit expensive optimal algorithms (like RTED) to small subtrees (< 100 nodes). Use heuristics for larger structures.

**Action**: Add size guards before applying computationally expensive analysis:

```javascript
if (subtreeSize(node) > MAX_SIZE_FOR_OPTIMAL) {
  return heuristicMatch(node); // Fast but approximate
} else {
  return optimalMatch(node);   // Slow but exact
}
```

---

### 3. **Don't Ignore Move Operations**

**Quote**: "Since moving code is a frequent action performed when editing code, it should also be taken into account."

**Application**: In conflict analysis, recognize when code was moved (refactoring) vs. truly added/deleted. Moved code that's identical shouldn't conflict.

**Example**: If BASE has `function utils()` in main.js, OURS moves it to utils.js, and THEIRS also moves it to helpers.js, recognize this as a "move conflict" not "delete + add + add" conflict.

---

### 4. **Don't Treat All AST Granularities Equally**

**Quote**: "The main advantage in using the AST granularity is that the edit script directly refers to the structure of the code."

**Key data**: At fine-grained AST level, GumTree outperforms ChangeDistiller in 65.49% of cases. At coarse-grained level, only 31.32%.

**Application**: Use fine-grained ASTs (expression-level) not coarse-grained (statement-level) for conflict analysis. Parser choice matters.

---

### 5. **Don't Use Text-Line Diff for Semantic Conflicts**

**Quote**: "The limitations of diff are twofold. First, it only computes additions and deletions... Second, it works at a granularity (the text line) that is both coarse grain and not aligned with the source code structure."

**Application**: While line-based diff is fast, it's insufficient for semantic conflict resolution. Always parse to AST before attempting automated resolution.

**Exception**: For very large files or performance-critical scenarios, consider hybrid approach (line-based pre-filter, AST-based for conflicts only).

---

## Relevance Score

**Overall Relevance**: 9/10

**Breakdown**:
- **Algorithm applicability**: 10/10 - Directly applicable to 3-way merge conflict analysis
- **Performance**: 9/10 - Fast enough for interactive use (20-74ms), scales to large files
- **Empirical validation**: 10/10 - Extensively validated on real codebases
- **Implementation complexity**: 7/10 - Moderate complexity, requires robust AST infrastructure
- **Move detection**: 6/10 - Less critical for conflict resolution than general diffing (conflicts usually in-place)

**Why not 10/10**: Paper focuses on 2-way diff (version1 → version2), while conflict resolution needs 3-way merge (BASE → OURS vs BASE → THEIRS). Adaptation required.

---

## Recommended Next Steps

1. **Immediate (High ROI)**:
   - Implement height-based subtree matching to identify conflict boundaries
   - Add dice coefficient scoring to measure conflict severity
   - Ensure parser generates fine-grained ASTs (expression-level granularity)

2. **Short-term (Medium ROI)**:
   - Implement container mappings for context around conflicts
   - Add recovery mappings for detailed analysis within small conflict regions
   - Expose minHeight, minDice, maxSize as configuration parameters

3. **Long-term (Lower ROI for conflicts, but valuable)**:
   - Implement move detection for refactoring-related conflicts
   - Build confidence scoring system based on mapping quality
   - Add visualization similar to GumTree's web-based diff view

---

## Key Quotes for Reference

> "Our objective is not to find the shortest sequence of actions between two versions, but a sequence that reflects well the developer intent."

> "Moving code is a frequent action performed when editing code, it should also be taken into account."

> "GumTree is inspired by the way developers manually look at changes between two files. First they search for the biggest unmodified pieces of code. Then they deduce which container of code can be mapped together. Finally they look at precise differences in what is leftover in each container."

> "In 95.1% of cases, GumTree has a good output. In 19.4% of cases, GumTree better highlights changes than diff."

---

## References

- **Tool**: github.com/jrfaller/gumtree
- **Paper DOI**: 10.1145/2642937.2642982
- **Citations**: 445 (as of 2026-01-28)
- **Related Work**: ChangeDistiller [13], RTED [27], Chawathe et al. [6], Diff/TS [15]

---

*Analysis generated for lz-git.conflict plugin development - 2026-01-28*
