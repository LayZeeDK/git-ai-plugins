# SemDiff: Binary Similarity Detection by Diffing Key-Semantics Graphs (2023)

**Authors:** Liu, Zhang, Ma, Liu, Zhang, Chen, Liu, Ahmed, Xiang
**Source:** arXiv:2308.01463v1
**Domain:** Binary code similarity detection
**Relevance Score:** 6/10 (Indirect - binary analysis techniques transferable to source code)

---

## Key Findings

### Core Innovation
SemDiff addresses the challenge of detecting similar code despite syntactic/structural differences caused by different compilers, optimization levels, or obfuscation. The key insight: **preserve semantic behavior while ignoring syntactic variations**.

### Main Contributions

1. **Key Instructions Abstraction**: Not all instructions matter equally. SemDiff identifies four types of "key instructions" that capture essential program behavior:
   - **Calling behavior**: Function calls with their arguments
   - **Comparing manner**: Comparison operations (cmp, test)
   - **Indirect branch**: Dynamic jump targets
   - **Memory store**: Memory write operations

2. **Key-Semantics Graph**: A directed graph where nodes are key instructions (with symbolic expressions as attributes) and edges represent control flow between key instructions.

3. **LSH-Based Graph Comparison**: Locality-Sensitive Hashing enables efficient similarity computation for variable-length semantic expressions.

### Performance Results
- Outperforms BinDiff, Asm2Vec, Gemini, Palmtree, and functionsimsearch
- 73% average precision across different optimization levels (O0-O3)
- 81% precision across different compilers (GCC vs CLANG)
- Highly effective against obfuscation (92.5% on SUB, 77.9% on BCF, 71.4% on FLA)

---

## Techniques

| Technique | Description | Implementation Complexity | Transferability to Source Code |
|-----------|-------------|--------------------------|-------------------------------|
| **Key Instruction Extraction** | Identify semantically significant instructions (calls, comparisons, memory stores, branches) | Medium | High - Can identify "key statements" in source: function calls, conditionals, assignments |
| **Symbolic Execution** | Extract symbolic expressions for instruction operands | High | Medium - Source has explicit semantics; simpler to extract |
| **Key Expression Translation** | Convert symbolic expressions to normalized form using expression synthesis | High | Medium - Source AST provides similar abstraction |
| **Key-Semantics Graph** | Graph with key instructions as nodes, control flow as edges | Medium | High - Maps directly to reduced CFG/AST with semantic annotations |
| **Lightweight Loop Processing** | Execute loops twice to detect loop counters (ITER symbol) | Low | High - Identify loop variables through static analysis |
| **Topological Sort Serialization** | Convert graph to sequence preserving structural relations | Low | High - Standard graph algorithm |
| **LSH Tokenization** | Split expressions into tokens with type prefixes (RET_, cmp, branch, =) | Low | High - Tokenize AST nodes with semantic type annotations |
| **Jaccard Similarity via LSH** | Hash token sequences for efficient similarity computation | Low | High - Direct application to any token sequence |
| **Expression Synthesis** | Simplify complex expressions (e.g., x OR y - x AND y => x XOR y) | High | Low - Source code typically already in simplified form |

---

## Actionable Improvements for lz-git.conflict

### Priority 1: High Impact, Low Complexity

#### 1.1 Key Statement Identification
**Concept:** Not all lines in a merge conflict matter equally. Identify "key statements" that capture semantic intent.

**Implementation:**
```javascript
const KEY_STATEMENT_TYPES = {
  FUNCTION_CALL: 'call',      // Function/method invocations
  ASSIGNMENT: 'assign',        // Variable assignments (especially to shared state)
  CONDITIONAL: 'cmp',          // If/switch conditions
  RETURN: 'ret',               // Return statements
  IMPORT: 'import'             // Module imports/requires
};
```

**Application:** When resolving conflicts, prioritize preserving key statements from both sides. Non-key statements (formatting, comments, intermediate variables) can be more aggressively merged.

#### 1.2 Semantic Tokenization with Type Prefixes
**Concept:** SemDiff prefixes tokens with their semantic type (RET_, cmp, etc.) to preserve context during comparison.

**Implementation for conflict resolution:**
```javascript
// Token format: TYPE_token
// "cmp_userId", "call_validateInput", "assign_result"

function tokenizeConflict(code, language) {
  const ast = parse(code, language);
  return extractKeyStatements(ast).map(stmt => ({
    type: getStatementType(stmt),
    tokens: stmt.tokens.map(t => `${stmt.type}_${t}`)
  }));
}
```

**Benefit:** When comparing ours vs theirs, semantic tokens enable better matching even with renamed variables.

#### 1.3 LSH for Conflict Block Similarity
**Concept:** Use Locality-Sensitive Hashing to quickly identify if conflict regions are semantically similar (minor refactoring) vs fundamentally different (true conflict).

**Implementation:**
```javascript
function computeConflictSimilarity(oursCode, theirsCode) {
  const oursTokens = semanticTokenize(oursCode);
  const theirsTokens = semanticTokenize(theirsCode);

  const oursLSH = computeMinHash(oursTokens);
  const theirsLSH = computeMinHash(theirsTokens);

  return jaccardSimilarity(oursLSH, theirsLSH);
}

// High similarity (>0.8): Likely formatting/refactoring - auto-resolve
// Medium (0.4-0.8): Semantic overlap - suggest merge
// Low (<0.4): True conflict - require human review
```

### Priority 2: Medium Impact, Medium Complexity

#### 2.1 Key-Semantics Graph for Conflict Analysis
**Concept:** Build a reduced graph of key statements to understand semantic structure.

**Implementation:**
```javascript
class KeySemanticsGraph {
  constructor(code) {
    this.nodes = [];  // Key statements
    this.edges = [];  // Control flow between key statements
  }

  addKeyStatement(stmt, symbolicExpr) {
    this.nodes.push({
      id: stmt.location,
      type: stmt.type,
      expression: normalizeExpression(symbolicExpr)
    });
  }

  serialize() {
    // Topological sort -> token sequence
    return topologicalSort(this.nodes, this.edges)
      .flatMap(node => tokenize(node.expression));
  }
}
```

**Application:** Compare key-semantics graphs of ours/theirs/base to identify:
- Added key statements
- Removed key statements
- Modified key statements
- Reordered key statements

#### 2.2 Loop Counter Detection (ITER Symbol)
**Concept:** Identify loop variables to handle conflicts in loop constructs intelligently.

**Application:** When conflicts involve loops:
1. Identify loop counter variables
2. Check if both versions iterate similarly (ITER pattern matches)
3. Focus conflict resolution on loop body differences

```javascript
function analyzeLoopConflict(oursLoop, theirsLoop) {
  const oursIter = identifyLoopCounter(oursLoop);
  const theirsIter = identifyLoopCounter(theirsLoop);

  if (loopPatternsMatch(oursIter, theirsIter)) {
    return {
      type: 'BODY_CONFLICT',
      resolution: 'merge_loop_bodies'
    };
  }
  return {
    type: 'STRUCTURE_CONFLICT',
    resolution: 'require_human_review'
  };
}
```

### Priority 3: Research/Future Investigation

#### 3.1 Expression Synthesis for Normalization
**Concept:** Simplify equivalent expressions to canonical form before comparison.

**Challenge:** Requires symbolic math library (e.g., mathjs for JavaScript).

**Potential Application:**
```javascript
// Before comparison, normalize:
// x + 0 -> x
// x * 1 -> x
// x || false -> x
// !(a && b) -> !a || !b
```

#### 3.2 Cross-Optimization Robustness
**Concept:** SemDiff handles code compiled with different optimizations. For source code, this translates to handling different coding styles.

**Research Direction:** Build a "style-invariant" representation that recognizes:
- `if (x) { return true; } return false;` === `return x;`
- `arr.map(x => f(x))` === `arr.map(f)`
- `const a = x; const b = a;` === `const b = x;`

---

## Evaluation Metrics (Transferable)

| Metric | Original Use | Application to Conflict Resolution |
|--------|-------------|-----------------------------------|
| **Precision@1** | Correctly finding the most similar function | Correctly identifying the semantically equivalent resolution |
| **NCD Score** | Measuring syntactic dissimilarity | Quantifying how different conflict versions appear textually |
| **Jaccard Similarity** | Comparing LSH values | Comparing semantic token sets between conflict regions |
| **Top-k Accuracy** | Finding similar function in top-k results | Ranking multiple possible resolutions |

### Suggested Metrics for lz-git.conflict

1. **Semantic Preservation Score**: % of key statements preserved after auto-resolution
2. **Conflict Complexity Index**: Based on key-semantics graph differences
3. **Auto-Resolution Confidence**: LSH similarity threshold for automatic merging
4. **Human Review Rate**: % of conflicts requiring manual intervention

---

## Limitations and Considerations

### From the Paper
1. Limited mnemonic support affects accuracy
2. Loop unrolling creates matching difficulties
3. Relies on IDA Pro for binary analysis (we use language-specific parsers)

### For Source Code Application
1. **Language Dependency**: Need language-specific parsers for AST extraction
2. **Semantic Equivalence**: Source-level semantic equivalence is easier than binary but still non-trivial
3. **Context Sensitivity**: Merge conflicts often require understanding broader context than a single function

---

## Integration Recommendations

### Phase 1: Quick Wins
1. Implement semantic tokenization with type prefixes
2. Add LSH-based similarity scoring to conflict-resolver agent
3. Create key statement extractor for JavaScript/TypeScript

### Phase 2: Enhanced Analysis
1. Build key-semantics graph for conflict regions
2. Implement topological serialization for graph comparison
3. Add loop structure analysis

### Phase 3: Advanced Features
1. Expression normalization/synthesis
2. Style-invariant comparison
3. Learning from resolved conflicts (team patterns)

---

## References for Implementation

- **LSH Libraries**:
  - JavaScript: `minhash`, `locality-sensitive-hashing`
  - Python: `datasketch`

- **AST Parsing**:
  - JavaScript/TypeScript: `@babel/parser`, `typescript`
  - Multi-language: `tree-sitter`

- **Expression Synthesis** (paper reference):
  - msynth: https://github.com/mrphrazer/msynth
  - For JS: Consider `mathjs` for algebraic simplification

---

## Summary

SemDiff's core insight - focusing on **key semantics** rather than syntactic details - transfers well to merge conflict resolution. The techniques of semantic tokenization, graph-based representation, and LSH similarity computation can improve the lz-git.conflict plugin's ability to:

1. Distinguish true conflicts from formatting/refactoring changes
2. Identify semantically equivalent code written differently
3. Prioritize preservation of important statements during auto-resolution
4. Provide confidence scores for automatic vs manual resolution decisions

The most immediately applicable techniques are key statement identification, semantic tokenization with type prefixes, and LSH-based similarity scoring.
