# SemDiff Semantic Differencing Tool Analysis

**Repository:** D:/projects/github/LayZeeDK/git-ai-plugins/plugins/lz-git.conflict/research/repos/SemDiff/
**Date:** 2026-01-28
**Codebase Size:** 103 Java files

## Key Findings

### What Makes It "Semantic"

SemDiff differs fundamentally from text-based diff tools by operating on Abstract Syntax Trees (ASTs) rather than raw text. The tool:

1. **Parses both file versions** using Eclipse JDT's parser into full ASTs
2. **Wraps Eclipse AST nodes** in custom `DiffNode` classes that track difference state
3. **Compares structural equivalence** rather than textual equivalence
4. **Ignores formatting changes** completely (whitespace, comments, ordering of independent declarations)
5. **Detects semantic operations** like renames, moves, and structural modifications

### Architecture Overview

**Core Pipeline:**
```
Source File → Eclipse JDT Parser → CompilationUnit (AST)
           → DiffNode Wrapper Tree → Structural Comparison
           → Difference Annotation → Summary Output
```

**Key Components:**

1. **AST Wrapper Layer** (`za.ac.sun.cs.semdiff.ast.*`)
   - 74 custom `DiffNode` subclasses mirroring JDT's AST node types
   - Each wraps an Eclipse AST node and tracks its `Difference` state
   - Implements visitor pattern for traversal

2. **Comparison Engine** (`za.ac.sun.cs.semdiff.compare.*`)
   - `CompareNodes.java`: Main comparison orchestrator
   - Type-specific comparators: `CompareBodyDeclarations`, `CompareStatements`, `CompareExpressions`
   - Rename detectors: `TypeDeclRenames`, `MethodDeclRenames`, `FieldDeclRenames`

3. **Matching Algorithm** (`za.ac.sun.cs.semdiff.matcher.DiffASTMatcher.java`)
   - 874-line structural equality checker
   - Deep recursive matching of AST subtrees
   - Type-aware comparison (only matches nodes of same type)

4. **Similarity Metrics** (`za.ac.sun.cs.semdiff.similarity.*`)
   - `LcsDistance`: Token-based LCS edit distance
   - `LevenshteinDistance`: String edit distance
   - `DamerauDistance`: String distance with transpositions

5. **LCS Implementation** (`za.ac.sun.cs.semdiff.lcs.*`)
   - Generic Longest Common Subsequence algorithm
   - Used for both token-level and node-level comparison
   - Dynamic programming approach (O(m*n) time/space)

### How Eclipse JDT Enables Semantic Diff

**JDT Parser Integration:**
```java
ASTParser parser = ASTParser.newParser(AST.JLS4);
parser.setSource(source.toCharArray());
Map options = JavaCore.getOptions();
JavaCore.setComplianceOptions(JavaCore.VERSION_1_7, options);
parser.setCompilerOptions(options);
CompilationUnit cu = (CompilationUnit) parser.createAST(null);
```

**Benefits:**
- Handles all Java 7 syntax constructs
- Produces well-typed AST with semantic information
- Resolves ambiguities that text diffs can't
- Provides structural navigation (parent/child relationships)

**Limitations:**
- Java-only (requires language-specific parser)
- JLS4 (Java 7) locked-in (outdated for modern Java)
- Parser errors block semantic diff entirely

### Core Comparison Algorithm

**Three-Phase Approach:**

**Phase 1: Exact Match Removal**
```java
// Remove identical body declarations
while (index < original_body.size()) {
    if (revised_body.contains(original_body.get(index))) {
        revised_body.remove(original_body.get(index));
        original_body.remove(index);
    }
}
```

**Phase 2: Identifier-Based Matching**
```java
// Match by name and type
if (original_identifier.equals(revised_identifier)
    && CompareNodes.isSameType(original, revised)) {
    CompareNodes.compareNodes(original, revised);
}
```

**Phase 3: Similarity-Based Matching**
```java
// Use LCS distance for fuzzy matching
protected static double MINIMUM_SIMILARITY_RATIO = 0.85;
protected static int MINIMUM_NUMBER_OF_TOKENS = 25;

if (similarity > MINIMUM_SIMILARITY_RATIO
    && tokens > MINIMUM_NUMBER_OF_TOKENS) {
    return true; // Nodes are similar
}
```

**Rename Detection:**
- Temporarily swaps identifiers to test equality
- If bodies match with different names, marks as RENAMED
- Tracks rename relationship via `setRelatedReference()`

### Difference State Model

**Five Diff States:**
```java
enum DifferenceEnum {
    UNCHANGED,  // Exact match
    ADDED,      // Only in revised
    DELETED,    // Only in original
    RENAMED,    // Same structure, different identifier
    MOVED       // Relocated in tree (e.g., method moved between classes)
}
```

Each `DiffNode` maintains:
- Current difference state
- Reference to related node (for renames/moves)
- Start/end position in original source
- Child nodes with their own states

### Token-Based Similarity

**TokenVisitor Strategy:**
- Traverses AST and collects node type names
- Example: `MethodInvocation` → token "MethodInvocation"
- Ignores actual identifiers and literals
- Produces ordered sequence representing structure

**LCS Distance Calculation:**
```java
double ratio = 1.0 - ((double) lcs.getMinEditDistance()
    / Math.max(original_tokens.size(), revised_tokens.size()));
```

**Why This Works:**
- Captures structural similarity independent of names
- Two methods with same logic but different variable names = high similarity
- Refactored code maintaining structure = high similarity
- Formatting changes = zero effect on tokens

## Techniques Table

| Technique | Implementation | Strength | Weakness |
|-----------|---------------|----------|----------|
| **AST Wrapping** | Custom `DiffNode` hierarchy mirrors Eclipse JDT nodes | Full structural information; visitor pattern support | 74 wrapper classes to maintain; tight coupling to JDT |
| **Type-Specific Comparison** | Separate comparators for statements, expressions, body declarations | Handles language-specific semantics correctly | Complex dispatch logic; hard to extend |
| **LCS-Based Matching** | Dynamic programming LCS on token/node sequences | Optimal alignment; handles reordering | O(m*n) complexity; memory intensive |
| **Similarity Thresholds** | 85% similarity + 25 token minimum | Reduces false matches; avoids trivial nodes | Magic numbers; no tuning mechanism |
| **Lazy Evaluation** | Three-phase comparison (exact → named → similar) | Fast path for common cases; defers expensive computation | Complex control flow; hard to debug |
| **Rename Detection** | Identifier swapping + equality test | Precise rename detection; tracks relationships | Only works for single renames; can't handle chained renames |
| **Move Detection** | Post-comparison pass on added/deleted nodes | Finds relocated code blocks | Runs after main comparison; limited to top-level declarations |
| **Token Abstraction** | Visitor extracts AST node types as tokens | Language-independent metric; ignores syntax details | Loses semantic information; can't distinguish logic changes |
| **Structural Equality** | Recursive subtree matching via `DiffASTMatcher` | Deep comparison; handles nested structures | 874 lines of matching code; brittle to AST changes |
| **Difference Annotations** | Each node tracks its own diff state | Fine-grained difference tracking; supports partial diffs | State management complexity; can be inconsistent |

## Actionable Improvements for lz-git.conflict

### 1. Adopt Multi-Phase Comparison Strategy

**Current SemDiff approach:**
```
Phase 1: Remove exact matches (fast)
Phase 2: Match by identifier + type (medium)
Phase 3: Match by similarity (slow)
```

**Adaptation for conflict resolution:**
- Phase 1: Detect identical hunks (no conflict)
- Phase 2: Match method/function signatures
- Phase 3: Use similarity for renamed code
- Phase 4: Flag low-similarity conflicts for human review

**Benefit:** Reduces false conflicts where code was moved/renamed but not changed.

### 2. Language-Agnostic Similarity Metrics

**SemDiff limitation:** Hard-coded for Java via JDT

**Improvement:** Abstract the token extraction
```javascript
// Pseudo-code for lz-git.conflict
function extractTokens(code, language) {
    if (language === 'java') return extractJavaTokens(code);
    if (language === 'typescript') return extractTSTokens(code);
    // Fallback to simple tokenization
    return extractGenericTokens(code);
}
```

**Benefit:** Semantic diff across languages without full parser for each.

### 3. Threshold-Based Confidence Scoring

**SemDiff approach:** Fixed 85% similarity threshold

**Improvement for conflicts:**
```
Confidence = similarity_score * structural_weight + identifier_weight
if (Confidence > 0.90) → auto-resolve
if (Confidence > 0.70) → suggest resolution with warning
if (Confidence < 0.70) → require human decision
```

**Benefit:** Transparent conflict resolution with safety margins.

### 4. Incremental Comparison

**SemDiff limitation:** Full re-parse and comparison every time

**Improvement:** Cache parsed ASTs
- Store AST for base, ours, theirs
- Only re-parse if file modified
- Reuse comparison results across conflict blocks

**Benefit:** Performance improvement for large files.

### 5. Conflict-Specific Node Types

**SemDiff tracks:** ADDED, DELETED, RENAMED, MOVED, UNCHANGED

**Add for conflicts:**
- `CONFLICTED` - Both sides modified
- `OURS_ONLY` - Only in our branch
- `THEIRS_ONLY` - Only in their branch
- `RESOLVED` - Conflict resolved automatically

**Benefit:** Clearer conflict visualization and tracking.

### 6. Contextual Similarity

**SemDiff limitation:** Compares nodes in isolation

**Improvement:** Consider surrounding context
```javascript
function contextAwareSimilarity(node1, node2) {
    let nodeSim = structuralSimilarity(node1, node2);
    let parentSim = structuralSimilarity(node1.parent, node2.parent);
    let siblingsSim = siblingSimilarity(node1, node2);
    return (nodeSim * 0.6) + (parentSim * 0.3) + (siblingsSim * 0.1);
}
```

**Benefit:** Better disambiguation when multiple similar nodes exist.

### 7. Whitespace-Aware Output

**SemDiff limitation:** Loses all formatting information

**Improvement for conflict resolution:**
- Track original indentation/formatting
- Preserve style from winning side
- Normalize only when merging incompatible styles

**Benefit:** Cleaner merged output that respects project conventions.

### 8. Partial Conflict Resolution

**SemDiff approach:** All-or-nothing comparison

**Improvement:**
- Resolve non-conflicting sub-nodes first
- Leave only truly conflicted parts unresolved
- Example: Method signature changed vs. method body changed

**Benefit:** Reduces manual conflict resolution burden.

## Anti-Patterns and Warnings

### 1. Magic Numbers Without Justification

**Location:** `CompareNodes.java:20-21`
```java
protected static int MINIMUM_NUMBER_OF_TOKENS = 25;
protected static double MINIMUM_SIMILARITY_RATIO = 0.85;
```

**Problem:** No explanation for why 25 tokens or 85% similarity. Likely tuned empirically for specific datasets.

**Risk for adaptation:** These thresholds may not generalize to other codebases or languages.

### 2. O(m*n) Complexity Without Bounds

**Location:** `LongestCommonSubsequence.java`

**Problem:** Dynamic programming LCS allocates `m * n` matrix. For large methods (1000+ tokens each), this is 1M integers (4MB+ memory).

**Risk:** Memory exhaustion on large files; no early termination for obviously dissimilar nodes.

### 3. Silent Error Handling

**Location:** `Utils.java:34-35`
```java
} catch (Exception e) {
}
```

**Problem:** File read errors are swallowed, returning `null`. Parser errors also ignored.

**Risk:** Silently produces incorrect diffs when input files are inaccessible or malformed.

### 4. Global State in Visitors

**Location:** `BodyDeclarationVisitor.java`

**Pattern:** Visitor uses instance variable `bodyDeclaration` to store result
```java
atd.accept(BodyDeclarationVisitor.getBodyDeclarationVisitor());
this.types.add(BodyDeclarationVisitor.getBodyDeclarationVisitor()
    .getBodyDeclaration());
```

**Problem:** Not thread-safe; reuses singleton visitor instance.

**Risk:** Concurrent comparison operations would corrupt state.

### 5. Type Explosion

**Problem:** 74 `DiffNode` subclasses, each requiring:
- Constructor wrapping JDT node
- `subtreeMatch0()` implementation
- `accept0()` visitor method
- Custom comparison logic

**Maintenance burden:** Adding new Java language features requires touching dozens of files.

**Alternative:** Generic node with type metadata would reduce code by 50%+.

### 6. Identifier Mutation for Comparison

**Location:** `CompareBodyDeclarations.java:334-340`
```java
DiffSimpleName actualName = revisedBodyDecl.getIdentifier();
revisedBodyDecl.setIdentifier(originalBodyDecl.getIdentifier());
boolean equalDifferentIdentifiers = originalBodyDecl.equals(revisedBodyDecl);
revisedBodyDecl.setIdentifier(actualName); // Set it back
```

**Problem:** Temporarily mutates node state to test hypothetical equality.

**Risk:**
- Not thread-safe
- Breaks if comparison throws exception before restoration
- Violates principle of least surprise

**Better approach:** Compare with identity-ignoring comparator.

### 7. Hard-Coded Java Version

**Location:** `Utils.java:52-56`
```java
ASTParser parser = ASTParser.newParser(AST.JLS4); // Java 7
JavaCore.setComplianceOptions(JavaCore.VERSION_1_7, options);
```

**Problem:** Locked to Java 7 (released 2011). Modern Java has:
- JLS8: Lambdas, streams, default methods
- JLS9: Modules, private interface methods
- JLS10+: var, records, pattern matching, sealed classes

**Risk:** Silently fails or misparses modern Java code.

### 8. No Incremental Update

**Problem:** Full re-parse and re-comparison on every change.

**Missed opportunity:** Eclipse JDT supports incremental parsing. Could reuse unchanged subtrees.

### 9. Move Detection Runs Too Late

**Location:** `CompareNodes.java:26`
```java
compareNodes(original, revised);
movedBodyDeclarations(original, revised); // After main comparison
```

**Problem:** Nodes already marked ADDED/DELETED before move detection runs. Move detection has to search through already-processed nodes.

**Better approach:** Detect moves first, then compare remaining nodes.

### 10. No Reporting of Ambiguity

**Problem:** When multiple nodes match with similar scores, tool picks first match arbitrarily.

**Missing feature:** Should flag ambiguous matches for human review (e.g., "Method A could match either Method B or Method C with 87% similarity each").

## Relevance Score

**Overall Relevance: 8/10** for lz-git.conflict plugin

### High Relevance (9-10/10)

1. **Multi-phase comparison strategy** - Directly applicable to conflict resolution
2. **Similarity-based matching** - Essential for detecting equivalent changes
3. **LCS algorithm for alignment** - Useful for conflicting blocks
4. **Rename detection pattern** - Common conflict source
5. **Difference state model** - Clear taxonomy of change types

### Medium Relevance (6-8/10)

6. **AST wrapper architecture** - Concept useful, but language-specific
7. **Token-based similarity** - Works without full parsing, good fallback
8. **Structural equality checking** - Helpful but requires language support

### Lower Relevance (4-5/10)

9. **Eclipse JDT integration** - Java-specific, not directly portable
10. **Visitor pattern implementation** - Implementation detail, not core algorithm

### Why Not 10/10?

- **Language specificity:** SemDiff is Java-only via Eclipse JDT. Git conflicts occur across all languages.
- **No conflict resolution:** SemDiff only computes diffs, doesn't merge or resolve conflicts.
- **No three-way merge:** Compares two versions, but Git conflicts need base + ours + theirs.
- **Performance concerns:** O(m*n) complexity problematic for large conflict regions.

### Key Takeaways for lz-git.conflict

**Do Adopt:**
- Multi-phase comparison (exact → named → similar)
- Similarity thresholds with confidence scoring
- Token-based metrics for language-agnostic comparison
- Rename/move detection patterns

**Adapt Carefully:**
- AST parsing (need fallbacks when parser unavailable)
- LCS algorithm (add complexity bounds)
- Structural comparison (make language-pluggable)

**Avoid:**
- Java-specific coupling
- Magic numbers without configuration
- Silent error handling
- State mutation during comparison
- Type explosion with wrapper classes

**Novel Contributions:**
- Three-way merge support (SemDiff only does two-way)
- Interactive conflict resolution (SemDiff is batch-only)
- Cross-language support (SemDiff is Java-only)
- IDE integration patterns (SemDiff is CLI-only)

## Conclusion

SemDiff demonstrates that **structural comparison is feasible and valuable** for detecting semantically equivalent code. The core insight—using ASTs and similarity metrics instead of text diffs—directly addresses the problem lz-git.conflict aims to solve.

However, SemDiff's Java-specific implementation via Eclipse JDT limits direct code reuse. The **algorithmic patterns and architectural decisions** are more valuable than the actual code.

For lz-git.conflict, the key lesson is: **semantic awareness requires language-specific knowledge, but you can achieve 80% of the benefit with generic token-based heuristics and save full AST parsing for ambiguous cases.**

The tool's three-phase comparison strategy (exact → named → similar) and its rename detection via identifier swapping are immediately applicable patterns. The LCS-based similarity scoring provides a solid foundation, though the fixed thresholds should be made configurable with user-visible confidence scores.

Most importantly, SemDiff proves that **semantic diff tools can be practical and performant** when carefully designed with phase separation and lazy evaluation. This validates the core vision of lz-git.conflict.
