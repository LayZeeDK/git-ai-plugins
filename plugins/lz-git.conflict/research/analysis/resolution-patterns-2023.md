# Resolution Patterns Analysis: van Dok (2023)

**Paper**: In Conflict: An Empirical Study of Merge Conflict Resolutions in Open-Source Projects
**Author**: Yael van Dok
**Year**: 2023
**Institution**: University of Bern

## Key Findings

### Derivable Resolution Rates

The study analyzed 7,866 open-source projects on GitHub across multiple programming languages, examining 140,705 conflicting merges containing 644,203 conflicting files and 1,451,231 conflicting chunks.

**Core Statistics:**
- **75% of conflicting chunks** were resolved using derivable resolutions (canonical or semi-canonical)
- **66% of conflicting files** had all chunks resolved derivably with no context changes
- **35% of conflicting merges** were entirely derivable
- **80% of conflicting merges** contained between 1-5 conflicting chunks

**Complexity Distribution:**
- **45% of all conflicting merges** had exactly 1 conflicting chunk (49% derivability rate)
- **81% of all conflicting files** contained only 1 conflicting chunk (74% derivability rate)
- Derivability rates decreased with increasing conflict complexity
- For merges with >5 chunks: ~15% average derivability rate
- For files with >3 chunks: <30% derivability rates

### Resolution Categories

The study identified three types of conflicting chunk resolutions:

1. **Canonical** (2 options): Pick code from one branch or the other
2. **Semi-canonical** (3 options):
   - Include both code segments (concatenation, either order)
   - Remove all conflicting code (delete both)
3. **Non-canonical**: Custom developer-written code

**Key Insight**: 67% of chunks were resolved canonically, 9% semi-canonically, and 24% non-canonically.

### Context Changes

- **80% of contexts remained unchanged** during merge conflict resolution
- Changed contexts were a major factor preventing derivability at the file level
- Java projects showed highest rate of unchanged contexts (91%)
- JavaScript projects showed lowest rate (71%)

## Techniques for Automated Resolution

| Technique | Description | Applicability | Implementation Priority |
|-----------|-------------|---------------|------------------------|
| **Derivable Resolution Generation** | Generate all 5 possible derivable resolutions (2 canonical + 3 semi-canonical) per chunk | 75% of chunks | HIGH |
| **Single-Chunk Fast Path** | Optimize for single-chunk conflicts with minimal computation | 45% of merges, 81% of files | HIGH |
| **Computational Cost Assessment** | Calculate 5^K resolutions where K = total conflicting chunks | Essential for feasibility | HIGH |
| **Context Preservation Validation** | Verify no changes to non-conflicting code surrounding chunks | Required for 66% file derivability | HIGH |
| **Syntactic Validation** | Test generated resolutions for compilation/syntax errors | Improves ranking quality | MEDIUM |
| **Semantic Testing** | Run test suites on generated resolutions to rank by correctness | Best-performing selection | MEDIUM |
| **Dependency Analysis** | Identify independent chunks for parallel resolution generation | Reduces exponential cost | MEDIUM |
| **Low-Complexity Filtering** | Focus on merges with ≤5 chunks (80% of cases) for initial implementation | Manages scope | LOW |
| **File-Type Awareness** | Handle different resolution strategies for source vs. non-source files | Unknown impact | LOW |

## Actionable Improvements for lz-git.conflict

### Immediate Enhancements

1. **Expand Resolution Options**
   - Current: Likely supports ours/theirs (canonical)
   - Add: Semi-canonical options (both, neither, both-reversed)
   - Impact: Could handle 76% (67%+9%) of chunks automatically

2. **Context Change Detection**
   - Implement: Verify no modifications to non-conflicting lines
   - Purpose: Distinguish true derivable resolutions from partial manual edits
   - Impact: Improves accuracy of resolution recommendations

3. **Complexity-Based Routing**
   - For 1 chunk: Fast path with all 5 options (45% of merges)
   - For 2-5 chunks: Full generation (35% of merges, 5^2-5^5 = 25-3125 options)
   - For 6+ chunks: Warn about computational cost or use heuristics

4. **Multi-Granularity Analysis**
   - Track resolution success at chunk, file, and merge levels
   - Report: "3 of 4 files can be auto-resolved" vs. all-or-nothing
   - Benefit: Partial automation reduces developer workload

### Strategic Improvements

5. **Resolution Ranking System**
   - Generate all derivable options (5^K combinations)
   - Filter by: Syntax validity → Semantic correctness → Test passage
   - Present: Top 3-5 candidates ranked by quality
   - Fallback: If all fail, present best syntactic option

6. **Independent Chunk Detection**
   - Analyze: Do conflicting chunks reference each other?
   - If independent: Generate file-level resolutions separately (linear growth)
   - If dependent: Must generate all combinations (exponential growth)
   - Example: Chunks in different files are often independent

7. **Language-Specific Optimization**
   - Java: 78% canonical chunks, 91% unchanged contexts → highest automation potential
   - JavaScript: 45% canonical chunks, 71% unchanged contexts → more custom logic needed
   - Prioritize: Java, TypeScript, C++ for initial rollout

8. **Incremental Resolution Mode**
   - Resolve: Independent chunks/files first (low risk)
   - Present: Remaining conflicts to developer with context
   - Benefit: Reduces manual work even when full automation impossible

### Validation Approach

9. **Empirical Validation**
   - Test against: Historical merges from target projects
   - Measure: % of cases where generated resolution matches developer's choice
   - Target: >70% match rate for single-chunk conflicts

10. **User Experience Design**
    - Show: "This merge has 3 chunks, 125 possible resolutions"
    - Recommend: "Option A passes all tests, Option B has syntax warnings"
    - Allow: Developer override/refinement of generated resolution

## Warnings and Anti-Patterns

### Critical Limitations

**1. Computational Explosion**
- Generating 5^K resolutions becomes infeasible quickly
- At K=10 chunks: 9.7 million combinations
- Only 20% of merges have <10 chunks, but these have low derivability rates
- **Mitigation**: Cap at K≤5 (80% of merges), use heuristics beyond that

**2. Semantic Blindness**
- Line-based matching ignores syntactic/semantic equivalence
- Example: Variable renaming considered "non-canonical" but semantically equivalent
- Whitespace/formatting differences prevent matching
- **Mitigation**: Normalize code before comparison (auto-formatters)

**3. Context Sensitivity**
- 20% of contexts were changed during resolution
- Changed contexts prevent derivability even with canonical chunks
- Cannot detect if context changes are essential or incidental
- **Mitigation**: Flag changed contexts for human review

**4. False Positives Risk**
- Derivable ≠ Correct
- A resolution may be derivable but semantically wrong
- 24% of chunks required custom logic (non-canonical)
- **Mitigation**: Always run tests, never auto-commit without validation

### Anti-Patterns to Avoid

**Don't:**
- ❌ Auto-apply resolutions without showing the user
- ❌ Attempt full automation for merges with >5 chunks
- ❌ Ignore context changes when claiming derivability
- ❌ Generate all combinations for dependent chunks without warning
- ❌ Present only one "best" option without alternatives
- ❌ Skip syntax/semantic validation of generated resolutions
- ❌ Treat all file types identically (source vs. config vs. docs)

**Do:**
- ✅ Present ranked options for developer selection
- ✅ Clearly communicate confidence levels
- ✅ Validate generated resolutions before recommending
- ✅ Focus on high-frequency, low-complexity scenarios first
- ✅ Provide partial resolution for complex merges
- ✅ Learn from user selections to improve ranking
- ✅ Fail safely with clear explanations

### Study Limitations Affecting Plugin Design

1. **No Semantic Analysis**
   - Study used string comparison only
   - Actual derivability rates may be higher if semantically equivalent
   - Plugin should consider implementing AST-based comparison

2. **Mixed File Types**
   - Study analyzed all files (source, config, docs, binaries)
   - Source code conflicts may have different patterns
   - Plugin should track metrics separately by file type

3. **No Dependency Analysis**
   - Study assumed worst-case (all chunks dependent)
   - Many chunks may actually be independent
   - Plugin should implement dependency detection for better scaling

4. **Line-Based Granularity**
   - Conflicts tracked at line level, not AST node level
   - Semi-structured merging (AST-aware) could improve rates
   - Plugin could explore structured merge for supported languages

## Relevance Score: 9/10

**Rationale:**

This study is **highly relevant** to the lz-git.conflict plugin with the following strengths:

✅ **Direct Applicability**: Studies the exact problem domain (merge conflict resolution)
✅ **Large-Scale Data**: 7,866 projects, 1.4M chunks provides statistical significance
✅ **Multi-Language**: Covers diverse languages relevant to most users
✅ **Actionable Metrics**: Provides concrete percentages for automation potential
✅ **Granular Analysis**: Chunk/file/merge levels align with plugin's architecture
✅ **Feasibility Focus**: Directly addresses automation viability questions

**Minor Limitations** (why not 10/10):

⚠️ **No Algorithm Details**: Doesn't provide specific implementation algorithms
⚠️ **Limited Semantic Analysis**: Focuses on line-based matching only
⚠️ **No User Study**: Doesn't include developer feedback on automation preferences

**Recommendation**: This paper should be **core reading** for anyone working on the lz-git.conflict plugin. The 75% chunk derivability and 35% merge derivability rates provide clear target metrics. The complexity distribution (80% merges have ≤5 chunks) guides implementation priorities.

---

**Next Steps**:
1. Implement semi-canonical resolution options (currently missing)
2. Add context change detection before claiming derivability
3. Create fast path for single-chunk conflicts (45% of cases)
4. Validate approach on historical merges from target projects
5. Consider AST-based semantic analysis for future enhancement
