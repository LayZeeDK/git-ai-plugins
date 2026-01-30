# Detecting Semantic Conflicts with Unit Tests (2024)

**Authors:** Da Silva, Borba, Maciel, Mahmood, Berger, Moisakis, Gomes, Leite
**Source:** Journal of Systems and Software 214 (2024) 112070
**Focus:** SAM (SemAntic Merge) - A semantic merge tool using automated unit test generation to detect behavioral conflicts

---

## Key Findings

### 1. Semantic Conflicts Definition and Detection Challenge

Semantic conflicts occur when textually merged code compiles successfully but exhibits unexpected behavior due to unplanned interference between developers' changes. Unlike textual/merge conflicts (incompatible text in same file area) or build conflicts (syntax/static semantic errors), semantic conflicts require understanding program behavior.

**Formal Definition:** Two contributions to a base program semantically conflict when the specifications they individually satisfy are not jointly satisfied by the merged program.

**Key Insight:** Generated unit tests serve as "partial specifications" of the changes to be merged, enabling conflict detection without explicit behavior specifications.

### 2. SAM Architecture and Workflow

SAM operates on merge scenarios (quadruple of Base, Left, Right, Merge commits):

1. **Starting Point**: Invoked after successful textual merge via post-merge git hook
2. **Change Mining**: Uses DiffJ to identify mutually changed class elements (methods, constructors, fields)
3. **Build Generation**: Creates executable JARs for all four commits
4. **Test Generation**: Invokes EvoSuite, Differential EvoSuite, Randoop, and Randoop Clean
5. **Test Execution**: Runs generated tests against all four versions
6. **Conflict Detection**: Applies interference criteria heuristics
7. **Reporting**: Warns developers with test case revealing the conflict

### 3. Conflict Detection Criteria

**Criterion 1 (Primary - detected all 9 conflicts):**
- Test passes on parent commit (Left or Right)
- Test fails on Base commit
- Test fails on Merge commit
- Interpretation: Change intended by parent is not preserved after integration

**Criterion 2:**
- Test passes on Base, Left, and Right commits
- Test fails on Merge commit
- Interpretation: Behavior preserved by both parents individually is broken when combined

### 4. Experimental Results

**Dataset:** 85 change pairs from 51 merge scenarios across 31 GitHub Java projects

| Metric | Value |
|--------|-------|
| True Positives (detected conflicts) | 9 of 29 (31%) |
| False Positives | 3 |
| True Negatives | 53 of 56 |
| Precision | 0.75 |
| Recall | 0.31 |
| Accuracy | 0.43 |

**Tool Performance Comparison:**

| Tool | Conflicts Detected | False Positives |
|------|-------------------|-----------------|
| EvoSuite | 6 | 1 |
| Differential EvoSuite | 6 | 0 |
| Randoop | 2 | 0 |
| Randoop Clean | 2 | 1 |

**Key Finding:** Combining only Differential EvoSuite + EvoSuite detects all 9 conflicts detected by SAM.

### 5. Testability Transformations

Three transformations improve conflict detection:

1. **Access Modifier Transformation**: Replace non-public modifiers with `public` (classes, methods, constructors, fields)
2. **Empty Constructor Addition**: Add parameterless constructors to classes lacking them
3. **Inner Class Extraction**: Extract inner classes to outer level (manual)

**Impact:** Testability transformations contributed to detecting 3 additional conflicts not found with original executables.

### 6. Serialization Technique

OSean.EX tool serializes complex objects during project test execution:
1. Instruments target method to capture `this` object and parameters
2. Runs project tests to collect serialized objects
3. Creates deserialization class added to project
4. Test generation tools use deserialized objects

**Result:** Helped detect 15 additional behavior changes (not conflicts) but no new conflicts in the evaluated subsample.

### 7. Randoop Clean Modifications

Extended version of Randoop with two optimizations:

1. **Maximized Target Method Calls**: Reduces randomness by inserting calls to target method at intervals
2. **Increased Object Diversity**: Adds constructor/method calls returning required object types

**Metrics:** More calls to target methods, more diverse objects, but no additional conflicts detected.

### 8. False Negative Analysis

Of 20 false negatives, 13 could be detected with manually adapted tests. Main limitations:

1. **Inability to create relevant objects**: Complex object graphs with internal/external dependencies
2. **Missing relevant assertions**: Tests reach interference but assertions don't explore propagated state
3. **External resource dependencies**: Database sessions, mocks not set up
4. **Arguments that prevent reachability**: Null arguments cause early exceptions

---

## Techniques

| Technique | Description | Implementation Complexity | Plugin Applicability |
|-----------|-------------|---------------------------|---------------------|
| **Tests as Partial Specifications** | Generated tests capture intended behavior of changes, enabling conflict detection without explicit specs | Medium | High - LLMs can generate targeted tests for conflict validation |
| **Four-Version Comparison** | Compare test results across Base, Left, Right, Merge to detect interference | High | Low - Requires executable builds of all versions |
| **Interference Criteria Heuristics** | Specific pass/fail patterns indicate conflicts (e.g., pass-parent, fail-base, fail-merge) | Low | Medium - Logic can inform LLM validation prompts |
| **Testability Transformations** | Make private members public, add empty constructors, extract inner classes | Medium | Low - Requires code modification infrastructure |
| **Object Serialization** | Capture runtime objects from existing tests for use in generated tests | High | Low - Requires project test suite execution |
| **Target Method Focus** | Generate tests specifically exercising mutually changed methods | Medium | High - LLMs can focus on conflict-affected methods |
| **Regression Test Generation** | Use EvoSuite/Randoop for automated test creation | High | Low - Language-specific tools, build requirements |
| **Differential Testing** | Compare behavior between program versions to detect changes | Medium | Medium - LLM can reason about behavioral differences |
| **Flaky Test Detection** | Run tests 3x, discard inconsistent results | Low | Medium - Useful for any automated test approach |

---

## Actionable Improvements (Prioritized)

### Priority 1: Implement LLM-Based Test Generation for Conflict Validation (Medium Effort, High Impact)

**Current gap:** Plugin resolves conflicts but doesn't validate that resolution preserves both branch intents.

**Implementation:**
1. After resolution, use LLM to generate targeted test cases exploring the resolved code
2. Apply SAM's interference criteria conceptually: describe expected behavior for each branch
3. Ask LLM to verify resolution satisfies both intents

**Example prompt addition:**
```markdown
After resolving, validate the resolution:
1. What behavior did the LEFT branch intend? (partial specification)
2. What behavior did the RIGHT branch intend? (partial specification)
3. Does the resolution preserve both intents?
4. Generate a test scenario that would detect if either intent is violated.
```

### Priority 2: Adopt "Tests as Partial Specifications" Mental Model (Low Effort, High Impact)

**Current gap:** Resolution process may not explicitly capture intended behaviors.

**Implementation:**
1. Before resolution, ask LLM to articulate each branch's intent as a testable specification
2. Frame conflict as "how to satisfy both partial specifications"
3. Validate resolution against these specifications

**Example analysis structure:**
```markdown
## Branch Intents (Partial Specifications)
- LEFT intent: "When X, the system should Y"
- RIGHT intent: "When A, the system should B"

## Potential Interference
- LEFT modifies variable V which RIGHT reads
- If both execute, V may have unexpected value

## Resolution Validation
- Does resolution preserve LEFT's "X -> Y" behavior?
- Does resolution preserve RIGHT's "A -> B" behavior?
```

### Priority 3: Focus Analysis on State Elements (Low Effort, Medium Impact)

**Learning from paper:** All 9 detected conflicts occurred because parent commits impacted values stored in the same variables or object fields.

**Implementation:**
1. Identify shared state elements (variables, fields) modified by both branches
2. Analyze how each branch expects the state to evolve
3. Flag state conflicts explicitly in analysis

**Example prompt:**
```markdown
Identify shared state:
1. What variables/fields does LEFT modify?
2. What variables/fields does RIGHT modify?
3. Is there overlap? If so, analyze:
   - What value does LEFT expect after its changes?
   - What value does RIGHT expect after its changes?
   - Can both expectations be satisfied simultaneously?
```

### Priority 4: Add Conflict Severity Assessment (Low Effort, Medium Impact)

**Learning from paper:** Some conflicts only observable through specific object states or execution paths.

**Implementation:** Classify conflicts by likelihood of triggering:
- **High**: Direct state overlap, always triggers
- **Medium**: Conditional paths, triggers under specific conditions
- **Low**: Requires complex object states, rare triggering

### Priority 5: Implement Behavioral Diff Description (Medium Effort, High Impact)

**Learning from paper:** Detecting behavior change between commits is easier than detecting interference.

**Implementation:**
1. Describe behavioral changes introduced by each branch
2. Analyze how these changes interact when combined
3. Use this as input for resolution strategy

**New command suggestion:** `/conflict analyze` that provides:
- LEFT behavioral delta from BASE
- RIGHT behavioral delta from BASE
- Interaction analysis
- Conflict classification

### Priority 6: Assertion-Focused Resolution Review (Medium Effort, Medium Impact)

**Learning from paper:** Tests often reach interference location but assertions don't explore propagated state.

**Implementation:**
1. After resolution, identify what assertions would verify correctness
2. Describe observable differences that would indicate incorrect resolution
3. Recommend manual verification steps

### Priority 7: Document Complex Object Requirements (Low Effort, Low Impact)

**Learning from paper:** Complex object dependencies cause many false negatives.

**Implementation:**
1. Identify if conflict involves complex object graphs
2. Flag these for extra human attention
3. Note required setup/context for proper resolution testing

---

## Relevance Score

| Dimension | Score (1-5) | Rationale |
|-----------|-------------|-----------|
| **Direct Applicability** | 3 | Core technique (test generation) is Java-specific; conceptual model highly applicable |
| **Technical Depth** | 5 | Comprehensive methodology with rigorous empirical evaluation |
| **Implementation Feasibility** | 3 | Test generation requires build infrastructure; mental models easily adoptable |
| **Performance Evidence** | 4 | Solid results on 85 cases; 31% recall shows room for improvement |
| **Novel Contribution** | 4 | Tests as partial specifications is powerful conceptual framework |

**Overall Relevance: 3.8/5**

This paper provides a rigorous foundation for understanding semantic conflicts and their detection. While the automated test generation approach requires significant infrastructure (builds, Java-specific tools), the conceptual framework of "tests as partial specifications" directly informs how an LLM-based resolver should reason about conflicts. The interference criteria (pass/fail patterns across versions) can be translated into prompting strategies that ask the LLM to verify resolution correctness.

**Key limitation for LLM approach:** SAM detects only 31% of conflicts, indicating that even sophisticated automated testing has significant blind spots. This reinforces the value of LLM semantic understanding as a complementary approach, as demonstrated by ConflictLens (2025) achieving 76% recall.

---

## Key Quotes

> "The core idea we propose and assess in this paper is the use of generated tests as partial specifications of the code revisions to be integrated -- tests then partially capture the effect of the changes in the revisions."

> "Two contributions (sets of changes) to a base program semantically conflict -- that is, interfere in an unplanned way -- when the specifications they are individually supposed to satisfy are not jointly satisfied by the program that integrates them."

> "A special benefit of our regression testing approach to detect conflicts is that one ends up with a test case that reveals a conflict, when the tool reports one. This decreases the effort to understand how a conflict occurs."

> "The testability transformations contribute to increasing the testability of the code under analysis, allowing the tools to directly access and call all elements of a target class."

> "All nine detected conflicts have common aspects: the conflicts occur because the parent commits' changes impact the values stored in the same variables or object fields."

---

## References for Further Investigation

- **SafeMerge** (Sousa et al., 2018) - Static analysis approach with compositional verification, 28% precision but 66% recall
- **Semex** (Nguyen et al., 2015) - Variability-aware execution for conflict detection using feature toggles
- **Crystal** (Brun et al., 2013) - Early conflict detection through speculative analysis
- **Palantir** (Sarma et al., 2012) - Workspace awareness for parallel change notification
- **DiffJ** - Tool for mining mutually changed Java elements (used by SAM)
- **EvoSuite** / **Differential EvoSuite** - Best performing test generation tools in study
- **Online Appendix** - Dataset available at https://spgroup.github.io/papers/sam-semantic-merge-tool.html

---

## Comparison with ConflictLens (2025)

| Aspect | SAM (2024) | ConflictLens (2025) |
|--------|------------|---------------------|
| Approach | Automated test generation | LLM-based detection + test validation |
| Precision | 0.75 | 0.91 |
| Recall | 0.31 | 0.76 |
| F1 Score | 0.44 | 0.82 |
| Infrastructure | Requires builds, Java-specific | LLM API access |
| Output | Conflict-revealing test case | Pattern classification + test case |
| Conflict Taxonomy | None explicit | 4 patterns (Overlap Contamination, etc.) |

**Implication:** LLM-based approaches (ConflictLens) significantly outperform automated test generation (SAM) for semantic conflict detection, suggesting the lz-git.conflict plugin's LLM-centric approach is well-positioned for this problem domain.
