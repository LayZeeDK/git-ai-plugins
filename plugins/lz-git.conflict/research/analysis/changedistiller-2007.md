# ChangeDistiller Analysis (2007)

**Paper:** Change Distilling: Tree Differencing for Fine-Grained Source Code Change Extraction
**Authors:** Beat Fluri, Michael Würsch, Martin Pinzger, Harald C. Gall
**Year:** 2007
**Source:** IEEE Transactions on Software Engineering, Vol. 33, No. 11

**Implementation:** https://bitbucket.org/sealuzh/tools-changedistiller/

---

## Key Findings

### 1. Core Algorithm Improvements

ChangeDistiller improves upon the Chawathe et al. (1996) tree differencing algorithm specifically for source code:

- **Original algorithm:** Designed for hierarchically structured documents (LaTeX), not source code
- **45% improvement:** Over baseline in approximating minimum edit script
- **34% error rate:** Mean absolute percentage error (vs 79% for original)
- **Tree edit operations:** INSERT, DELETE, MOVE, ALIGNMENT, UPDATE

### 2. Tree Differencing Approach

The algorithm operates in two phases:

1. **Matching Phase:** Find matching nodes between original AST (T1) and modified AST (T2)
2. **Edit Script Generation:** Compute minimum conforming edit script to transform T1 → T2

#### Matching Criteria

**Leaf Matching (Criterion 1):**
```
match₁(x,y) = true if:
  - l(x) = l(y) [same label/type]
  - sim(v(x), v(y)) ≥ f [values similar above threshold]
```

**Inner Node Matching (Criterion 2):**
```
match₂(x,y) = true if:
  - l(x) = l(y) [same label]
  - |common(x,y)| / max(|x|,|y|) ≥ t [subtree similarity]
```

### 3. String Similarity: N-Grams vs Levenshtein

**Bigram Similarity (chosen approach):**
- Runtime: O(n + m) - one order of magnitude faster
- Robust to word order changes (e.g., `verticalDrawAction` → `drawVerticalAction`)
- Similarity = 2 × |n-grams(a) ∩ n-grams(b)| / |n-grams(a) ∪ n-grams(b)|
- Example: bigram similarity = 0.82, Levenshtein = 0.56

**Why N-grams work better for code:**
- Common refactorings involve reordering words in identifiers
- Captures character-level similarity independent of position
- Less susceptible to identifier renaming patterns

### 4. Best Match Algorithm

**Problem:** Original algorithm uses "first match" - violates Assumption 1 for source code
**Solution:** Find best matching partner with highest similarity

```java
// Implementation pattern from BestLeafTreeMatcher.java
List<LeafPair> matchedLeafs = matchLeaves(left, right);
Collections.sort(matchedLeafs); // Sort by similarity descending
markMatchedLeaves(matchedLeafs); // Take best matches first
```

**Benefits:**
- Reduces false matches for duplicate statements
- Prevents propagation of mismatches to parent nodes
- Critical for handling print statements, logging, common patterns

### 5. Dynamic Thresholds for Small Subtrees

**Problem:** Small subtrees (≤4 leaves) prone to mismatch propagation

**Example failure case:**
```java
// Original
if (a > b) {
    foo.getHuga();
    foo.doNothing();  // Changed line
}

// Modified
if (a > b) {
    foo.getHuga();
    foo.bar();        // Changed line
}
```

With static threshold t=0.6, similarity = 1/2 = 0.5 → entire if-statement mismatched

**Solution:** Dynamic thresholds
- n > 4 leaves: threshold = 0.6
- n ≤ 4 leaves: threshold = 0.4

**Impact:** Prevents cascading deletion/insertion of entire subtrees for single-statement changes

### 6. Inner Node Similarity Weighting

**Problem:** Condition expression changes cause if-statement mismatches

**Solution:** Weight subtree similarity higher than value similarity
```
If simString < threshold BUT simNode ≥ 0.8:
  → Match anyway (condition changed, but structure preserved)
```

**Rationale:** Structure more important than exact condition for matching

### 7. Change Classification Taxonomy

ChangeDistiller classifies 35 change types with significance levels:

**Significance Levels:**
- NONE: Comments, documentation
- LOW: Statement insert, ordering change
- MEDIUM: Statement delete, condition change, parameter renaming
- HIGH: Parameter type change, removed functionality
- CRUCIAL: Parent class/interface changes, removing derivability

**Body vs Declaration Changes:**
- Body changes: Inside method bodies (statement-level)
- Declaration changes: Method/class signatures (API-level)

---

## Techniques Applicable to Conflict Resolution

| Technique | Description | Applicability | Priority |
|-----------|-------------|---------------|----------|
| **Bigram Similarity** | Use n-grams for identifier/statement matching | HIGH - handles refactored identifiers in conflicts | 🔴 Critical |
| **Best Match Algorithm** | Find optimal pairing vs first match | HIGH - prevents false matches in conflict regions | 🔴 Critical |
| **Dynamic Thresholds** | Lower similarity thresholds for small subtrees | MEDIUM - conflict regions often small | 🟡 Medium |
| **Inner Node Weighting** | Prioritize structure over exact values | HIGH - structure preserved across branches | 🔴 Critical |
| **AST-based Differencing** | Compare structure, not text lines | HIGH - semantic understanding of conflicts | 🔴 Critical |
| **Change Classification** | Categorize by significance level | MEDIUM - prioritize resolution by impact | 🟡 Medium |
| **Post-order Traversal** | Bottom-up tree processing | MEDIUM - handle leaf conflicts before parent | 🟡 Medium |
| **Matching Set** | Track matched node pairs | HIGH - identify common vs conflicting nodes | 🔴 Critical |

---

## Java AST Handling Patterns

### 1. Intermediate Tree Representation

**Problem:** JDT AST doesn't provide uniform parent-child access

**Solution:** Create intermediate labeled & valued tree
```java
// From implementation
class Node {
    Label label;        // Statement type (IF, METHOD_INVOCATION)
    String value;       // Statement content or condition
    List<Node> children;
}
```

**Benefits:**
- Uniform traversal interface
- Decouples algorithm from JDT specifics
- Enables language-independent core algorithm

### 2. Label vs Value Distinction

**Labels:** Node type (IF, THEN, METHOD_INVOCATION, ASSIGNMENT)
**Values:**
- Leaf nodes: Full statement text (`"foo.bar();"`)
- Inner nodes: Condition expressions (`"a > b"`)

**Matching strategy:**
1. Check label equality first (prevent matching different types)
2. Calculate value similarity second (actual content)

### 3. Comment Handling

Separate similarity calculator for comments:
```java
// From BestLeafTreeMatcher.java
StringSimilarityCalculator commentCalc = new TokenBasedCalculator();
double COMMENT_THRESHOLD = 0.4; // Lower than code (0.6)
```

**Rationale:** Comments are natural language, need different matching

### 4. Postorder Enumeration Pattern

```java
// From BestLeafTreeMatcher.java
for (Enumeration<Node> leftNodes = left.postorderEnumeration();
     leftNodes.hasMoreElements();) {
    Node x = leftNodes.nextElement();
    // Process leaves first, then parents
}
```

**Benefits:**
- Leaf matches propagate to inner nodes
- Bottom-up builds complete picture
- Natural for edit script generation

### 5. Marking Matched Nodes

```java
if (!(x.isMatched() || y.isMatched())) {
    fMatch.add(pair);
    x.enableMatched();
    y.enableMatched();
}
```

**Prevents:**
- Double-matching nodes
- Conflicting pairings
- Cascading errors

---

## Actionable Improvements for lz-git.conflict

### 1. Adopt Bigram String Similarity (Priority: 🔴 Critical)

**Current State:** Plugin likely uses text-based diff or simple string equality

**Improvement:**
```javascript
// Implement n-gram similarity for statement matching
function bigramSimilarity(str1, str2) {
    const bigrams1 = generateBigrams(str1);
    const bigrams2 = generateBigrams(str2);
    const intersection = bigrams1.filter(b => bigrams2.includes(b)).length;
    const union = bigrams1.length + bigrams2.length;
    return (2 * intersection) / union;
}

// Use in conflict resolution
if (bigramSimilarity(ours, theirs) >= 0.6) {
    // Statements are similar despite refactoring
    // Apply intelligent merge
}
```

**Impact:** Handle identifier refactorings across branches (e.g., renamed methods in conflicts)

### 2. Implement Best Match for Duplicate Code (Priority: 🔴 Critical)

**Current State:** May match first occurrence of duplicate statement

**Improvement:**
```javascript
// Collect all candidate matches with scores
const candidates = [];
for (const theirsStmt of theirsBranch) {
    for (const oursStmt of oursBranch) {
        const similarity = calculateSimilarity(theirsStmt, oursStmt);
        if (similarity >= threshold) {
            candidates.push({ theirs: theirsStmt, ours: oursStmt, score: similarity });
        }
    }
}

// Sort by score descending, take best non-conflicting matches
candidates.sort((a, b) => b.score - a.score);
const matches = selectBestMatches(candidates); // Greedy algorithm
```

**Impact:** Correct matching for logging statements, repeated patterns in conflicts

### 3. Apply Dynamic Thresholds for Small Conflict Regions (Priority: 🟡 Medium)

**Current State:** Fixed threshold for all conflict sizes

**Improvement:**
```javascript
function getMatchingThreshold(conflictSize) {
    // Small conflicts need lower threshold to prevent complete mismatch
    return conflictSize <= 4 ? 0.4 : 0.6;
}

// In conflict resolution
const conflictStatements = countStatements(conflictRegion);
const threshold = getMatchingThreshold(conflictStatements);
```

**Impact:** Better handling of single-line or small block conflicts

### 4. Structure-Based Conflict Detection (Priority: 🔴 Critical)

**Current State:** Text-based diff identifies conflicts

**Improvement:**
```javascript
// Parse conflicting regions into AST
const baseAST = parseToAST(baseVersion);
const oursAST = parseToAST(oursVersion);
const theirsAST = parseToAST(theirsVersion);

// Identify structural differences
const oursChanges = extractChanges(baseAST, oursAST);
const theirsChanges = extractChanges(baseAST, theirsAST);

// Detect semantic conflicts
if (affectSameNode(oursChanges, theirsChanges)) {
    // True semantic conflict
    reportConflict(/* ... */);
} else {
    // Independent changes, auto-merge possible
    autoMerge(oursChanges, theirsChanges);
}
```

**Impact:** Reduce false conflicts from textual proximity but semantic independence

### 5. Change Significance Scoring (Priority: 🟡 Medium)

**Current State:** All conflicts treated equally

**Improvement:**
```javascript
// Classify changes by significance
const changeTypes = {
    STATEMENT_INSERT: { significance: 'LOW', bodyChange: true },
    STATEMENT_DELETE: { significance: 'MEDIUM', bodyChange: true },
    PARAMETER_TYPE_CHANGE: { significance: 'HIGH', bodyChange: false },
    // ... 35 total types
};

// Prioritize resolution
function getResolutionPriority(change) {
    const type = classifyChange(change);
    return type.significance === 'HIGH' ? 'MANUAL' : 'AUTO_CANDIDATE';
}
```

**Impact:** Focus user attention on high-impact conflicts, auto-resolve safe ones

### 6. Edit Script for Merge Preview (Priority: 🟢 Low)

**Current State:** Show conflicting text blocks

**Improvement:**
```javascript
// Generate human-readable edit script
const editScript = generateEditScript(baseAST, oursAST, theirsAST);

// Format for user
console.log("Ours: INSERT method call at line 45");
console.log("Theirs: UPDATE condition expression at line 42");
console.log("Conflict: Both modify if-statement structure");
```

**Impact:** Better user understanding of conflict nature

---

## Warnings & Anti-Patterns to Avoid

### 1. ⚠️ Small Tree Mismatch Propagation

**Anti-Pattern:** Using fixed high threshold (>0.6) for all subtrees

**Problem:** Single statement change in small block causes entire block to mismatch
```
Input: 1 changed statement in 3-statement if-block
Output: DELETE entire old block + INSERT entire new block = 8 operations
Expected: UPDATE 1 statement = 1 operation
```

**Mitigation:** Dynamic thresholds (implemented in ChangeDistiller)

### 2. ⚠️ First Match Assumption Violation

**Anti-Pattern:** Matching first similar node encountered in traversal

**Problem:** Common patterns matched incorrectly
```java
// Ours
System.out.println("foo");
doWork();
System.out.println("bar");  // Insert this

// Theirs
System.out.println("foo");
doWork();
```

First match pairs both `println("foo")`, misses actual unchanged line

**Mitigation:** Best match algorithm with similarity scoring

### 3. ⚠️ Ignoring Statement Position

**Anti-Pattern:** Matching statements regardless of position in method

**Problem:** Statement moved to end matches with similar statement at beginning
```java
// Version 1: statement at line 1 changes
// Version 2: same statement at line 50 unchanged
// Algorithm matches them → false UPDATE instead of DELETE + INSERT
```

**Mitigation:** Position heuristics in postprocessing (noted as limitation in paper)

### 4. ⚠️ Parameter List Mismatches

**Anti-Pattern:** Treating parameter lists as regular subtrees

**Problem:** Small tree problem + declaration context
```java
// Insert 3 new parameters
foo(a, b, c, d)  // Old: 1 param
foo(a, b, c, d, e, f, g)  // New: 7 params

// Similarity: 4/7 = 0.57 < 0.6 → complete mismatch
// Output: DELETE old list, INSERT new list, MOVE 4 params = 6 operations
// Expected: INSERT 3 params = 3 operations
```

**Mitigation:** Special handling for declaration contexts, lower thresholds

### 5. ⚠️ Relabel Operations Invalid for Code

**Anti-Pattern:** Using tree edit distance algorithms with RELABEL operation

**Problem:** Cannot change node type in AST
```java
// INVALID: Relabel IF_STATEMENT → WHILE_STATEMENT
// Valid: DELETE IF_STATEMENT + INSERT WHILE_STATEMENT
```

**Mitigation:** ChangeDistiller excludes RELABEL, uses only INSERT/DELETE/MOVE/UPDATE

### 6. ⚠️ Text-Based Conflict Detection

**Anti-Pattern:** Relying on line-based diff for conflict identification

**Problem:** Misses semantic conflicts, reports false conflicts
```java
// Textual conflict (same line changed differently)
// But semantically independent (different variables)

// Ours:  x = calculate();
// Theirs: y = compute();
```

**Mitigation:** AST-based semantic conflict detection

### 7. ⚠️ Inadequate String Similarity

**Anti-Pattern:** Using Levenshtein distance for identifier matching

**Problem:** Fails on word reordering (common in refactoring)
```
verticalDrawAction → drawVerticalAction
Levenshtein: 0.56 (below threshold)
Bigrams: 0.82 (matches)
```

**Mitigation:** N-gram similarity as shown in paper (45% improvement)

---

## Limitations Acknowledged in Paper

### 1. Statement Position Not Considered

**Issue:** Best match may pair statements not at same position
- First statement changes
- Same statement appears at end unchanged
- Algorithm matches them → incorrect pairing

**Status:** Authors investigating postprocessing with position heuristics

### 2. Deeply Nested Small Trees

**Issue:** Dynamic thresholds fail when depth > 4 but subtrees still small
- Nested if/loop statements
- Each level < 4 leaves but multiple levels deep

**Impact:** One method in benchmark responsible for most errors (acceptSourceMethod)

### 3. Declaration Changes in Small Lists

**Issue:** Parameter list insertions trigger complete mismatch
- Inserting 3 params into 4-param list
- Similarity 4/7 = 0.57 < 0.6
- Generates delete/insert/move instead of just 3 inserts

**Status:** Noted limitation, no solution in paper

### 4. Language-Specific Tuning Required

**Issue:** Thresholds (f=0.6, t=0.6, dynamic t=0.4) tuned for Java
- Other languages may need different values
- Would require separate benchmarking

---

## Relevance Score: 9/10

**Highly Relevant** - ChangeDistiller directly addresses automated conflict resolution challenges:

### ✅ Direct Applications:
1. **AST-based matching** - Core technique for semantic conflict detection
2. **Bigram similarity** - Handles identifier refactoring across branches
3. **Best match** - Critical for duplicate code patterns in conflicts
4. **Change classification** - Prioritize conflicts by significance

### ✅ Validated Approach:
- Extensive benchmark (1,064 changes, 219 revisions, 3 projects)
- 45% improvement over baseline
- Open source implementation available

### 🎯 Immediate Actions:
1. Adopt n-gram similarity for statement comparison
2. Implement best-match algorithm for conflict regions
3. Use dynamic thresholds for small conflicts
4. Classify conflicts by significance level

### ⚠️ Adaptations Needed:
1. Three-way merge context (base, ours, theirs) vs two-way diff
2. Conflict region boundaries vs full method comparison
3. Interactive resolution vs batch processing

---

## References

**Paper:** Fluri, B., Würsch, M., Pinzger, M., & Gall, H. C. (2007). Change distilling: Tree differencing for fine-grained source code change extraction. *IEEE Transactions on Software Engineering*, 33(11), 725-743.

**Implementation:** https://bitbucket.org/sealuzh/tools-changedistiller/

**Related:**
- Chawathe et al. (1996) - Original tree differencing algorithm
- [Taxonomy paper] - Fluri & Gall (2006) - Change type classification
