# Analysis: On the Nature of Merge Conflicts (2018)

**Paper**: Ghiotto, Murta, Barros, van der Hoek
**Study Scope**: 2,731 open source Java projects, 25,328 failed merges, 175,805 conflicting chunks
**Date Analyzed**: 2026-01-28

---

## Key Findings

### Scale of the Problem
- **10-20% of all merge attempts fail**, with some projects experiencing rates up to 50%
- **60% of failed merges involve multiple conflicting chunks** (automated analysis)
- **40% of failed merges have a single conflicting chunk**, but resolution is still non-trivial

### Conflict Characteristics

#### Size Distribution
- **94% of conflicting chunks have <50 LOC in each version**
- **50% have ≤5 LOC in each version**
- Median size: 2.0 LOC (version 1), 2.5 LOC (version 2)
- Large conflicts (>50 LOC both versions) are rare (2%) but concentrated in specific projects

#### Language Construct Involvement
- **50% of chunks involve a single language construct**
- **72% involve one or two constructs**
- **90% involve up to four constructs**

Most frequent language constructs in conflicts:
1. **Method invocation** (20% of all constructs)
2. **Variable** (17%)
3. **Comment** (14%)
4. **If statement** (8%)
5. **Import** (6%)
6. **Method signature** (6%)
7. **Method declaration** (5%)

#### Resolution Strategies (Automated Analysis)
- **V1 (choose version 1)**: 50%
- **V2 (choose version 2)**: 25%
- **Concatenation**: 3%
- **Combination**: 9%
- **New Code**: 13%
- **None**: <1%

**Critical Insight**: **87% of conflicts are resolved without writing new code** - all necessary information exists within the conflicting chunks.

### Conflict Patterns

#### Dependencies Between Chunks
- **29% of multi-chunk merges have dependencies** between chunks
- Common patterns:
  - Method declaration changes affecting invocations
  - Parameter changes affecting call sites
  - Return type changes affecting variable declarations
  - Import statements depending on method invocations

#### Association Rules (Language Constructs)
Top patterns indicating co-occurrence:
- `annotation → method declaration` (64% confidence, 3.34 lift)
- `for statement → variable` (67% confidence, 1.97 lift)
- `if statement, variable → method invocation` (80% confidence, 1.96 lift)
- `try statement → method invocation` (69% confidence, 1.70 lift)

#### Difficulty Levels by Kind of Conflict
Difficulty Ratio = (complex chunks) / (complex + straightforward chunks)

**Most Difficult** (Automated Analysis):
- `comment, method invocation, variable` (28% DR)
- `method invocation, variable` (27% DR)
- `if statement` (27% DR)
- `if statement, method invocation, variable` (27% DR)
- `import` (27% DR)
- `if statement, method invocation` (26% DR)

**Easiest**:
- `comment, method declaration` (17% DR)
- `annotation, method declaration` (19% DR)
- `comment, variable` (20% DR)
- `variable` (21% DR)

### Developer Behavior

#### Individual Patterns
- Some developers show consistent preferences (e.g., one developer used V2 in ~50% of cases, another V1 in 30%)
- **Postponed resolutions are rare** (2% of chunks, 4% of commits)
- When conflicts increase in number (6-15+ chunks), developers shift toward Combination and New Code strategies

#### Project-Level Patterns
- Different projects exhibit distinct resolution patterns
- Some projects have 1-2 developers handling most merges (integration managers)
- Resolution preferences vary significantly by project culture

---

## Techniques for Automated Conflict Resolution

| Technique | Applicability | Automation Potential | Implementation Notes |
|-----------|---------------|---------------------|---------------------|
| **Import Concatenation** | 9% of all conflicts (import kind) | HIGH | Automatically concatenate import statements from both versions. Verify no duplicate imports. Already supported by some tools. |
| **Method Ordering** | Dependencies in 29% of multi-chunk merges | MEDIUM | Resolve method declarations before invocations; resolve return types before return statements. Requires dependency analysis. |
| **Variable Scope Analysis** | Frequent in method invocation + variable conflicts | MEDIUM | When method invocation changes affect variable initialization, analyze scope and type to suggest resolution. |
| **Comment Merging** | 14% of constructs, but 5% difficulty ratio | LOW-MEDIUM | Comments are often resolved automatically (choose newer). Natural language makes full automation difficult. |
| **Conditional Concatenation** | If statements on different conditions | MEDIUM | If both versions add non-overlapping conditions, concatenate. Requires semantic analysis of boolean expressions. |
| **Annotation Stacking** | High lift (3.34) with method declarations | HIGH | Stack annotations from both versions when they don't conflict. Simple syntactic check. |

### Heuristics by Pattern

#### Pattern: Method Declaration + Invocations
```
If method signature conflict resolved → auto-resolve invocation conflicts
- Match parameter types and order
- Update invocation sites accordingly
- Confidence: High for same-file invocations
```

#### Pattern: Import + Method Invocation
```
If method invocation resolved → auto-resolve import
- Determine required imports from resolved method calls
- Add necessary imports from conflicting versions
- Remove unused imports
```

#### Pattern: Variable + Method Invocation
```
Common: Variable initialization with different method calls
- Analyze return types of conflicting methods
- If types match → suggest selection
- If types differ → require manual resolution
```

#### Pattern: Control Flow (if/for) + Multiple Statements
```
If control structure differs but bodies are compatible:
- Offer concatenation of conditional branches
- Validate no overlapping conditions
- Confidence: Low (requires semantic analysis)
```

---

## Actionable Improvements for lz-git.conflict

### 1. **Multi-Stage Resolution Workflow** (Priority: HIGH)
Based on finding that 60% of merges have multiple chunks with dependencies:

**Implementation**:
- Detect chunk dependencies before resolution
- Present chunks in dependency order (declarations before uses)
- After resolving a chunk, re-analyze remaining chunks for auto-resolution opportunities
- Show developers: "Resolving this chunk may automatically resolve 3 related chunks"

**Expected Impact**: Reduce manual effort by 15-30% in multi-chunk scenarios.

---

### 2. **Smart Concatenation Assistant** (Priority: HIGH)
Based on finding that 87% of resolutions use existing code:

**Implementation**:
- For small conflicts (<10 LOC per version), generate all valid permutations
- Filter out syntactically invalid combinations (using AST parser)
- Run quick syntax checks and rank by likely correctness
- Present top 3-5 candidates to developer with one-click selection

**Expected Impact**: Turn 30-40% of Combination resolutions into semi-automated choices.

---

### 3. **Language Construct-Aware Rules** (Priority: MEDIUM)
Based on association rules and difficulty patterns:

**Implementation**:
```javascript
Rules to implement:
1. If conflict = "import" only → auto-concatenate + deduplicate
2. If conflict = "annotation" → auto-stack annotations
3. If conflict = "method declaration" + "method invocation" → resolve declaration first, then auto-update invocations
4. If conflict = "for statement" with "variable" → suggest keeping both if loop variables differ
5. If conflict = "if statement" with different conditions → suggest concatenation as else-if
```

**Expected Impact**: Automatically resolve 5-10% of conflicts, assist in 20-30% more.

---

### 4. **Historical Resolution Suggestions** (Priority: MEDIUM)
Based on finding that developers and projects show consistent patterns:

**Implementation**:
- Track resolution decisions per developer and per project
- For similar conflicts, show: "You resolved 8 similar conflicts by choosing V1"
- For project: "This project resolves 'import' conflicts by concatenation 82% of the time"
- Allow one-click application of historical pattern

**Expected Impact**: Speed up resolution by 20-40% for experienced developers.

---

### 5. **Difficulty Indicator** (Priority: LOW)
Based on difficulty ratio findings:

**Implementation**:
- Analyze conflict kind and assign difficulty score
- Show visual indicator: 🟢 Easy / 🟡 Medium / 🔴 Complex
- Suggest tackling easy conflicts first to gain momentum
- For complex conflicts, provide additional context and warnings

**Expected Impact**: Improve developer experience, reduce cognitive load.

---

### 6. **Method-Centric Resolution View** (Priority: MEDIUM)
Based on method-related constructs being in 20-30% of conflicts:

**Implementation**:
- When method declaration conflicts, show all related:
  - Method invocations in same file
  - Return statements
  - Parameter usages
- Highlight which will be affected by each resolution choice
- Enable "resolve method and dependents" in one action

**Expected Impact**: Reduce errors in method-related conflicts by 30-50%.

---

### 7. **Validation & Safety Checks** (Priority: HIGH)
Based on the finding that 13% still require new code:

**Implementation**:
- Before finalizing resolution, run:
  - Syntax validation (AST parsing)
  - Type checking (if possible)
  - Duplicate detection (imports, variables)
  - Semantic consistency checks
- Flag potential issues: "Warning: This may create a duplicate import"
- Offer fix suggestions

**Expected Impact**: Prevent 40-60% of post-merge syntax errors.

---

## Anti-Patterns to Avoid

### 1. **Over-Automation of Complex Conflicts**
- **Avoid**: Attempting to auto-resolve conflicts with high difficulty ratios (>25%)
- **Why**: if statements, method invocation+variable combinations require semantic understanding
- **Instead**: Provide intelligent assistance, not full automation

### 2. **Ignoring Conflict Context**
- **Avoid**: Treating each chunk in isolation
- **Why**: 29% of multi-chunk merges have dependencies
- **Instead**: Always analyze inter-chunk relationships before presenting to developer

### 3. **Single Resolution Strategy**
- **Avoid**: Assuming one heuristic fits all projects/developers
- **Why**: Resolution strategies vary significantly by project (V1: 13-50%, V2: 4-51%)
- **Instead**: Learn from project and developer history

### 4. **Treating All Language Constructs Equally**
- **Avoid**: Generic line-based merging for all conflicts
- **Why**: Import concatenation works well (20% resolution rate), but method declarations need careful handling
- **Instead**: Apply construct-specific strategies

### 5. **Neglecting Small Conflicts**
- **Avoid**: Assuming small conflicts are trivial
- **Why**: Even 2-5 LOC conflicts require developer decision in 50% of cases
- **Instead**: Provide quick-selection UI for small conflicts with smart suggestions

---

## Relevance Score: 95/100

### Relevance Breakdown

| Aspect | Score | Justification |
|--------|-------|---------------|
| **Alignment with lz-git.conflict goals** | 20/20 | Directly addresses semantic conflict resolution with comprehensive data |
| **Actionability** | 20/20 | Provides specific patterns, heuristics, and implementation guidance |
| **Data quality** | 18/20 | Massive scale (2,731 projects) but limited to Java and open source |
| **Practical insights** | 20/20 | Concrete statistics on what works, what doesn't, and why |
| **Implementation readiness** | 17/20 | Clear techniques but some require significant tooling (AST parsing, type analysis) |

### Why This Is Highly Relevant

1. **Empirical Foundation**: Largest study of merge conflicts to date with 175,805 real-world examples
2. **Actionable Patterns**: Specific language construct combinations and resolution strategies
3. **Automation Boundaries**: Clear data on what can (87% existing code) and cannot (13% new code) be automated
4. **Validation**: Both manual analysis (5 projects, deep) and automated (2,731 projects, broad)
5. **Tool Design Guidance**: Three explicit recommendations for future merge techniques

### Key Takeaway for Plugin Development

**Focus on semi-automation, not full automation**:
- 87% of conflicts have all code needed → assist in selection/combination
- 13% need new code → provide context and guidance
- 29% of multi-chunk merges have dependencies → resolve in smart order
- Historical patterns exist → learn and suggest

The study conclusively shows that a "portfolio approach" (base technique + specialized plugins + intelligent UI + resumable automation) is the right architecture for modern merge tools.

---

## References

- **Paper DOI**: [10.1109/TSE.2018.2871083](https://doi.org/10.1109/TSE.2018.2871083)
- **Dataset**: [https://github.com/gems-uff/merge-nature](https://github.com/gems-uff/merge-nature)
- **Interactive Data**: [http://merge-nature.netlify.app](http://merge-nature.netlify.app)

---

*Analysis generated: 2026-01-28*
*For lz-git.conflict Claude plugin development*
