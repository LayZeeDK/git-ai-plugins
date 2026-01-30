# ConflictLens: An LLM-Based Method for Detecting Semantic Merge Conflicts (2025)

**Authors:** Sun, Lu, Mao, Zhang, Zhang, Zhou
**Source:** SEKE 2025 (DOI: 10.18293/SEKE2025-012)
**Focus:** Two-stage LLM-based semantic conflict detection combining static analysis and dynamic test generation

---

## Key Findings

### 1. Four Semantic Conflict Patterns Identified

The paper conducts an empirical study on 137 high-confidence conflict instances from 195 Java repositories (56,129 merge scenarios), identifying four reusable conflict patterns:

**Bidirectional Interference (57.66% of conflicts):**
- **Pattern 1: Overlap Contamination (37.22%)** - Both branches modify the same object, creating a hybrid/anomalous "contaminated" state that aligns with neither branch's intent
- **Pattern 2: Confluent Interference (20.44%)** - Different branches modify different data objects that are jointly used in the same logic (conditionals, function calls), resulting in unexpected behavior

**Unidirectional Interference (32.12% of conflicts):**
- **Pattern 3: Assignment Override (10.95%)** - Both branches assign to the same variable, but merge ordering causes one to overwrite the other
- **Pattern 4: Execution Perturbation (21.17%)** - No direct data dependency, but merged control flow (early returns, conditionals) alters execution timing/conditions of one branch

### 2. Two-Stage Detection Architecture

**Stage 1: Semantic Conflict Localizer (SC-Localizer)**
- Uses LLMs with few-shot examples and Chain-of-Thought (CoT) prompting
- Four-step CoT reasoning process:
  1. Modification Identification - Extract changes from both branches
  2. Interaction Analysis - Identify shared variables, overlapping logic, interdependent control flows
  3. Pattern Matching - Map interactions to the four conflict patterns
  4. Conflict Localization - Pinpoint specific code regions (variables/statements)
- Output: JSON with detected pattern, affected components, and reasoning trace

**Stage 2: Targeted Conflict Validator (TC-Validator)**
- Generates pattern-specific test cases via LLM prompts
- Uses iterative feedback loop (up to 7 iterations) to refine tests based on execution results
- Pattern-specific validation strategies:
  - Bidirectional: Test must PASS on merged, FAIL on both left and right branches
  - Unidirectional: Test must PASS on affected branch, FAIL on base and merged branches

### 3. Performance Results

| Method | Precision | Recall | F1 Score | Accuracy |
|--------|-----------|--------|----------|----------|
| DSC (static analysis) | 0.43 | 0.61 | 0.51 | 0.61 |
| SAM (dynamic/EvoSuite) | 0.75 | 0.31 | 0.44 | 0.73 |
| Vanilla-LLM | 0.44 | 0.41 | 0.43 | 0.62 |
| **ConflictLens** | **0.91** | **0.76** | **0.82** | **0.89** |

### 4. Component Synergy

| Component | Precision | Recall | F1 Score |
|-----------|-----------|--------|----------|
| SC-Localizer only | 0.64 | 0.86 | 0.73 |
| TC-Validator only | 0.85 | 0.58 | 0.69 |
| **Combined** | **0.91** | **0.76** | **0.82** |

- Localization reduces search space for TC-Validator by 63%
- Test validation eliminates 71% of false positives from SC-Localizer

### 5. LLM Backend Comparison

| Model | Precision | Recall | F1 Score |
|-------|-----------|--------|----------|
| GPT-4o-Mini | 0.86 | 0.65 | 0.75 |
| DeepSeek-V3 | 0.87 | 0.69 | 0.77 |
| **DeepSeek-R1** | **0.91** | **0.76** | **0.82** |

DeepSeek-R1 (reasoning-oriented) excels at synthesizing semantically meaningful test cases that distinguish benign overlaps from true conflicts.

---

## Techniques

| Technique | Description | Implementation Complexity | Plugin Applicability |
|-----------|-------------|---------------------------|---------------------|
| **Four Conflict Patterns** | Taxonomy for classifying semantic conflicts (Overlap Contamination, Confluent Interference, Assignment Override, Execution Perturbation) | Low | High - Can be embedded in prompts for conflict-resolver agent |
| **Few-Shot + CoT Prompting** | 8 examples (2 per pattern) with 4-step reasoning chain for conflict localization | Low | High - Directly applicable to current LLM-based approach |
| **Structured JSON Output** | Constrained output format with pattern, affected components, and reasoning trace | Low | High - Improves parsing and reliability of agent responses |
| **Pattern-Specific Test Oracles** | Different pass/fail expectations based on conflict directionality | Medium | Medium - Could inform resolution validation |
| **Iterative Feedback Refinement** | Up to 7 rounds of test regeneration based on execution errors | Medium | Medium - Applicable for complex resolutions |
| **Merge Code Markers** | Annotations highlighting which changes came from left/right branches | Low | High - Already available via git conflict markers |
| **Branch-Specific Execution** | Running tests across base/left/right/merged versions | High | Low - Requires build infrastructure |

---

## Actionable Improvements (Prioritized)

### Priority 1: Integrate Conflict Patterns into Resolution Agent (Low Effort, High Impact)

**Current gap:** The conflict-resolver agent lacks structured understanding of semantic conflict types.

**Implementation:**
1. Add the four conflict patterns to the agent's system prompt
2. Include pattern identification as the first step before resolution
3. Tailor resolution strategies per pattern:
   - **Overlap Contamination**: Identify the contaminated variable, trace both branch intentions, determine correct scope
   - **Confluent Interference**: Analyze joint dependencies, may require refactoring shared logic
   - **Assignment Override**: Determine precedence or merge assignment logic
   - **Execution Perturbation**: Restructure control flow to preserve both branch behaviors

**Example prompt addition:**
```markdown
Before resolving, classify the conflict into one of four patterns:
1. Overlap Contamination - Both branches modify same object, creating hybrid state
2. Confluent Interference - Disjoint modifications interact through shared logic
3. Assignment Override - Competing assignments to same variable
4. Execution Perturbation - Control flow changes suppress one branch's logic
```

### Priority 2: Implement Four-Step CoT Reasoning (Low Effort, High Impact)

**Current gap:** Resolution may skip critical analysis steps.

**Implementation:** Structure the conflict-resolver agent to follow the paper's reasoning chain:
1. **Modification Identification**: "What did each branch change?"
2. **Interaction Analysis**: "Where do these changes interact?"
3. **Pattern Matching**: "Which conflict pattern does this match?"
4. **Resolution Localization**: "What specific code needs modification?"

### Priority 3: Add Structured Output Format (Low Effort, Medium Impact)

**Implementation:** Request JSON-structured analysis before resolution:
```json
{
  "conflict_pattern": "overlap_contamination | confluent_interference | assignment_override | execution_perturbation | unknown",
  "affected_variables": ["variable1", "variable2"],
  "affected_statements": ["line X", "line Y"],
  "left_branch_intent": "description",
  "right_branch_intent": "description",
  "recommended_resolution": "description",
  "confidence": "high | medium | low",
  "reasoning_trace": ["step1", "step2", "step3", "step4"]
}
```

### Priority 4: Pattern-Aware Validation Hooks (Medium Effort, High Impact)

**Current gap:** No automated validation that resolution preserves both branch intents.

**Implementation:**
1. Create a PostToolUse hook that validates resolutions
2. For bidirectional patterns: Check that resolution addresses both branch modifications
3. For unidirectional patterns: Ensure the affected branch's intent is preserved
4. Flag low-confidence resolutions for human review

### Priority 5: Semantic Conflict Detection Command (Medium Effort, High Impact)

**New feature:** Add a `/detect` or `/analyze` command that identifies potential semantic conflicts before resolution.

**Implementation:**
1. Extract changes from both branches (git diff)
2. Use LLM with few-shot examples to classify conflict pattern
3. Report findings with confidence level
4. Optionally auto-trigger appropriate resolution strategy

### Priority 6: Resolution Quality Metrics (Medium Effort, Medium Impact)

**Adopt paper's metrics for tracking:**
- Resolution correctness (manual validation initially)
- Pattern distribution across conflicts
- Confidence calibration (high confidence should correlate with correct resolutions)

### Priority 7: Team Pattern Analytics (High Effort, Future)

**Long-term opportunity:** Track conflict patterns per repository/team to:
- Identify recurring conflict hotspots
- Suggest workflow improvements
- Predict high-risk merges

---

## Relevance Score

| Dimension | Score (1-5) | Rationale |
|-----------|-------------|-----------|
| **Direct Applicability** | 5 | Four conflict patterns and CoT prompting directly enhance conflict-resolver agent |
| **Technical Depth** | 4 | Comprehensive methodology with empirical validation |
| **Implementation Feasibility** | 4 | Core techniques (patterns, prompting) require no infrastructure; test validation requires more effort |
| **Performance Evidence** | 5 | Strong experimental results (0.91 precision, 0.76 recall) on real-world conflicts |
| **Novel Contribution** | 4 | First LLM-based two-stage semantic conflict detection with pattern-driven prompting |

**Overall Relevance: 4.4/5**

This paper provides immediately actionable techniques for improving the lz-git.conflict plugin. The four conflict patterns offer a taxonomy that can structure both detection and resolution. The few-shot + CoT prompting strategy is directly applicable. The two-stage architecture (localize then validate) suggests a valuable enhancement where resolutions are validated before being applied.

---

## Key Quotes

> "SC-Localizer leverages LLMs to overcome the limitations of rule-based static analyzers in reasoning about cross-branch code interactions and contextual semantics."

> "By demonstrating how to trace interferences through CoT, few-shot examples help enforce pattern-aligned reasoning."

> "The structured reasoning process of DeepSeek-R1 enables it to better understand the subtle behavioral implications of each conflict type, resulting in more effective test oracles that distinguish between benign overlaps and true semantic conflicts."

---

## References for Further Investigation

- [7] Silva et al. - SAM: Detecting semantic conflicts with unit tests (baseline comparison)
- [3] De Jesus et al. - DSC: Static analysis for semantic conflicts
- [11] DeepSeek-R1 - Reasoning-oriented LLM that performs best in this domain
- [15] Zhang et al. - Multimodal chain-of-thought reasoning in language models
