# TIM: Semantic Merge Conflict Detection Analysis

**Paper**: Semantic Merge Conflict Detection
**Authors**: Shikha Mody, Bradley Mont, Jivan Gubbi, Brendon Ng (UCLA)
**Year**: 2022
**Repository**: [CS230-TIM-Improves-Merging](https://github.com/shikham-8/CS230-TIM-Improves-Merging)

---

## Key Findings

### 1. Semantic Conflict Definition

The paper formalizes semantic merge conflicts using the equation:

```
Delta[M + B] != Delta[(M + A) + B]
```

Where:
- M = Main branch state
- A = New commit to main branch
- B = Feature branch changes

**Insight**: A semantic conflict exists when the behavioral change introduced by feature branch B differs depending on whether commit A has been applied to main. This captures "silent" conflicts that pass textual merge but alter program behavior.

### 2. Two-Track Detection Approach

TIM implements separate strategies for refactoring vs. non-refactoring changes:

| Change Type | Detection Method | Tool Used |
|-------------|------------------|-----------|
| **Refactoring** | `diffbehavior` - find single counterexample showing behavioral difference | CrossHair diffbehavior |
| **Non-refactoring** | `cover` - generate exhaustive test cases, compare outputs across versions | CrossHair cover |

**Refactoring Flow**:
1. Compare M vs M+B (should be identical for valid refactor)
2. Compare M+A vs M+A+B (detects semantic conflict)

**Non-refactoring Flow**:
1. Generate test cases via symbolic execution on M, M+B, M+A, M+A+B
2. Take union of all test cases
3. Run all functions with unified test set
4. Compare output differences: `diff(M, M+B)` should equal `diff(M+A, M+A+B)`

### 3. Symbolic Execution for Test Generation

CrossHair generates tests that cover all execution paths without requiring a pre-existing test suite. This addresses a key limitation of traditional approaches that assume comprehensive tests exist.

**Implementation Pattern** (from `parse.py`):
```python
# Generate shell script to run CrossHair cover on each function
f.write("crosshair cover " + splitFilepath[-1] + " > " + os.getcwd() + "/tmp/crosshair-results.out \n")
```

### 4. CI/CD Integration Architecture

The GitHub Actions workflow demonstrates a complete pipeline:

```
buildmain -> buildbranch -> runmain -> runbranch -> comparediffs
```

1. Generate tests from main branch
2. Generate tests from feature branch
3. Run combined test set on main
4. Run combined test set on feature branch
5. Diff results to detect semantic conflicts

### 5. Critical Limitations Identified

| Limitation | Impact | Workaround Potential |
|------------|--------|---------------------|
| **Type annotations required** | Python dynamic typing not supported; dict must specify key/value types | Low - fundamental to symbolic execution |
| **Inheritance/Polymorphism** | Cannot detect behavioral differences in overridden methods | Medium - LLM can reason about inheritance |
| **Recursion** | Only generates single test case due to infinite search space | Medium - bounded unrolling possible |
| **Lambda functions** | Cannot generate symbolic callable values | Low - complex to address |
| **Parameter reordering** | Reports false positives for renamed/reordered parameters | High - LLM can detect intent |
| **Python-only** | No support for TypeScript, Go, etc. | High - LLM is language-agnostic |

---

## Techniques Table

| Technique | Description | Implementation in TIM | Complexity for Claude Plugin | Potential Value |
|-----------|-------------|----------------------|------------------------------|-----------------|
| **Behavioral Equivalence Check** | Verify two function versions produce identical outputs | `crosshair diffbehavior func1 func2` | Low - Claude can compare semantic intent | High |
| **Path Coverage Test Generation** | Generate inputs covering all execution paths | `crosshair cover function_name` | Medium - would need external tool or LLM reasoning | High |
| **Four-Version Comparison** | Compare M, M+B, M+A, M+A+B to isolate conflict source | Shell scripts orchestrating CrossHair | Medium - Claude can manage branch states | High |
| **Refactoring Detection via Commit Message** | Check if commit message contains "refactor" | `if "refactor" in commitObject["message"].lower()` | Low - trivial pattern matching | Low |
| **Function Extraction via Inspection** | Dynamically load modules to find callable functions | `imp.load_source()` + `callable(val)` inspection | Medium - Claude can use AST parsing | Medium |
| **CI Pipeline Integration** | Automated detection on every push | GitHub Actions workflow | Low - existing hook infrastructure | High |
| **Artifact-Based State Management** | Store test outputs as build artifacts for comparison | GitHub Actions artifacts | Low - can use temp files or git stash | Medium |

---

## Actionable Improvements for lz-git.conflict

### Priority 1: LLM-Based Semantic Diff (High Value, Medium Complexity)

**Current Gap**: The plugin resolves textual conflicts but does not detect semantic conflicts that merge cleanly.

**Proposed Enhancement**: Add a `/semantic-check` command that:

1. Identifies functions/methods modified in both branches
2. Uses Claude to analyze behavioral intent of each version
3. Flags potential semantic conflicts (e.g., "Branch A changes return type, Branch B adds caller assuming old type")

**Implementation Approach**:
```markdown
# In a new command: commands/semantic-check.md

1. Get diff between merge base and HEAD: `git diff $(git merge-base HEAD MERGE_HEAD)...HEAD`
2. Get diff between merge base and MERGE_HEAD: `git diff $(git merge-base HEAD MERGE_HEAD)...MERGE_HEAD`
3. For overlapping functions/files:
   - Prompt Claude: "Analyze if these changes could interact semantically"
   - Check for: type changes, API contracts, shared state, control flow assumptions
```

**Advantage over TIM**: Claude can reason about inheritance, polymorphism, cross-file dependencies, and multi-language codebases where symbolic execution fails.

### Priority 2: Pre-Merge Conflict Prediction (High Value, Low Complexity)

**Current Gap**: Conflicts are only detected after merge attempt.

**Proposed Enhancement**: Add `/predict-conflicts` command before merge:

1. Identify overlapping changed files between branches
2. Use AST-level or text-level diff to find overlapping change regions
3. Classify conflict likelihood: None, Low, Medium, High
4. Suggest resolution strategy before merge begins

**Implementation**:
```bash
# Get files changed in both branches
git diff --name-only main...feature-branch > /tmp/feature_files.txt
git diff --name-only main...target-branch > /tmp/target_files.txt
comm -12 <(sort /tmp/feature_files.txt) <(sort /tmp/target_files.txt)
```

### Priority 3: Behavioral Test Generation Hook (Medium Value, High Complexity)

**Current Gap**: No automated test generation for conflict resolution validation.

**Proposed Enhancement**: PostToolUse hook that generates minimal test cases after conflict resolution:

1. After `Edit` tool resolves a conflict in source file
2. Identify affected functions
3. Generate 2-3 test cases covering the merged logic
4. Output as suggestions (not auto-commit)

**Integration Point**:
```json
// hooks/hooks.json
{
  "hooks": [{
    "event": "PostToolUse",
    "tool": "Edit",
    "script": "scripts/suggest-tests.js"
  }]
}
```

### Priority 4: Resolution History for Pattern Learning (Medium Value, Medium Complexity)

**Current Gap**: No learning from past resolutions.

**Proposed Enhancement**: Track resolution decisions:

```json
// .claude/lz-git.conflict.history.json
{
  "resolutions": [{
    "timestamp": "2024-01-15T10:30:00Z",
    "file": "src/utils.ts",
    "conflictType": "import-merge",
    "strategy": "union",
    "accepted": true
  }]
}
```

Use history to adjust default strategy suggestions per file/pattern.

### Priority 5: Four-Version Analysis Command (Medium Value, Medium Complexity)

**Proposed**: `/analyze-semantic` command implementing TIM's core algorithm but using LLM instead of symbolic execution:

1. Identify merge base, HEAD, MERGE_HEAD, and merged state
2. For functions in conflicted files:
   - Extract each version
   - Prompt: "Does the behavioral delta from base->HEAD differ from base->merged?"
3. Flag discrepancies as potential semantic conflicts

---

## Integration Patterns for Claude-Based Detection

### Pattern 1: Intent-Based Conflict Analysis

Replace symbolic execution with LLM semantic understanding:

```
Prompt: Given these two changes to function X:
- Branch A: [diff A]
- Branch B: [diff B]

1. What is the intent of change A?
2. What is the intent of change B?
3. Can both intents be satisfied in a single merged version?
4. If merged textually, would the combined behavior match both intents?
```

### Pattern 2: Cross-Reference Validation

After textual merge, validate semantic integrity:

```
Prompt: The following code was merged from two branches:
[merged code]

Check for:
1. Undefined references (variables, functions, types used but not defined)
2. Type mismatches (function called with wrong argument types)
3. Dead code (unreachable branches due to conflicting conditions)
4. Missing imports
```

### Pattern 3: Refactoring Verification

Special handling for refactoring commits:

```
Prompt: Branch A claims to be a refactoring (no behavioral change).
Before: [original code]
After: [refactored code]

Verify: Is this truly behavior-preserving? Flag any subtle behavioral changes.
```

---

## Evaluation Metrics for Resolution Quality

Based on TIM's approach and general SE metrics:

| Metric | Description | Measurement Method |
|--------|-------------|-------------------|
| **Syntactic Validity** | Resolved code parses without errors | Run language-specific linter/parser |
| **Semantic Preservation** | Both branch intents preserved | Manual review or test suite execution |
| **Conflict Marker Removal** | All `<<<<<<<` markers eliminated | `grep -c "<<<<<<<" file` |
| **Build Success** | Project builds after resolution | `npm run build` / equivalent |
| **Test Pass Rate** | Existing tests still pass | `npm test` / equivalent |
| **False Positive Rate** | Flagged conflicts that weren't real | Requires ground truth dataset |
| **False Negative Rate** | Missed semantic conflicts | Requires post-hoc bug tracking |
| **Resolution Time** | Time from conflict detection to resolution | Timestamp comparison |
| **Human Intervention Rate** | % of conflicts requiring manual review | Track autonomous vs. flagged resolutions |

---

## Relevance Score

| Aspect | Score (1-5) | Rationale |
|--------|-------------|-----------|
| **Applicability to lz-git.conflict** | 4 | Core concept directly applicable; symbolic execution approach not transferable but LLM can fill gap |
| **Implementation Feasibility** | 4 | Most techniques achievable without external tooling; semantic analysis via prompting |
| **Novelty for Plugin** | 5 | Plugin currently lacks semantic detection; this would be a differentiating feature |
| **User Value** | 5 | Addresses 26x bug multiplier from semantic conflicts (per cited research) |
| **Technical Complexity** | 3 | Medium - requires careful prompt engineering and branch state management |

**Overall Relevance**: **4.2/5**

The paper's core insight (behavioral equivalence across branch states) is highly applicable. While the symbolic execution implementation (CrossHair) has significant limitations, Claude can provide more flexible semantic analysis that handles inheritance, multiple languages, and complex control flow that symbolic execution cannot. The CI integration pattern is directly reusable.

---

## Recommended Next Steps

1. **Immediate**: Add `/semantic-check` command prototype using LLM-based analysis
2. **Short-term**: Implement conflict prediction before merge attempts
3. **Medium-term**: Build resolution history tracking for pattern learning
4. **Long-term**: Develop test generation suggestions for resolved conflicts

The combination of TIM's theoretical framework with LLM capabilities could provide semantic conflict detection that exceeds what pure symbolic execution achieves.
