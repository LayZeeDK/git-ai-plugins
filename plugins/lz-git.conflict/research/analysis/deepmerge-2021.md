# DeepMerge: Learning to Merge Programs (2021) - Analysis

**Paper**: DeepMerge: Learning to Merge Programs
**Authors**: Dinella, Mytkowicz, Svyatkovskiy, Bird, Naik, Lahiri
**Venue**: arXiv:2105.07569v3 (IEEE TSE submission)
**Year**: 2021

## Key Findings

### Core Insight: Resolution Composition Pattern
The paper's foundational discovery is that **80% of merge conflict resolutions do not introduce new lines** - they consist entirely of (potentially rearranged) lines from the conflicting region (A and B variants). This aligns with prior studies showing 87% of Java resolutions use only input lines.

This observation enables framing merge resolution as a **sequence selection and ordering problem** rather than code generation, dramatically reducing the output space.

### Architecture: Pointer Network for Line Selection
DeepMerge uses a novel encoder-decoder architecture that:
1. **Outputs line indices** rather than generating tokens - the decoder produces tuples `(i, W)` where `W in {A, B}` and `i` is the line number
2. **Uses edit-aware embeddings** (Merge2Matrix) that encode the three-way diff structure
3. **Achieves 36.5% top-1 accuracy** on non-trivial JavaScript merges (9x better than structured approaches)
4. **78% accuracy on small conflicts** (<=3 lines, comprising 24% of dataset)

### Critical Dataset Insights
- **Trivial resolutions filtered**: 70% of raw merges were "ours/theirs" resolutions (taking A or B entirely) - these were excluded as not representing genuine merge reasoning
- **Resolution localization algorithm**: Novel algorithm to extract ground truth by finding unique prefix/suffix bookends in resolved files
- **8,719 non-trivial JavaScript merge tuples** from ~20,000 GitHub repositories

### Confidence-Based Precision Control
At confidence threshold 0.5:
- **72% precision** (correct 3 out of 4 times when providing resolution)
- **34% recall** (provides resolution 1/3 of the time)
- This trade-off is critical for practical deployment where false positives erode trust

## Techniques

| Technique | Description | Implementation Complexity | Relevance to LLM Plugin |
|-----------|-------------|---------------------------|-------------------------|
| **Merge2Matrix (Aligned Linearized)** | Edit-aware input encoding using diff alignment symbols (=, +, -, <->) with linear combination of embeddings | Medium | High - Can inform prompt structure for showing conflicts to LLM |
| **Pointer Network Decoder** | Outputs indices pointing to input lines rather than generating tokens | High (training required) | Medium - Validates "copy from input" assumption; LLMs can follow similar constraint via prompting |
| **BPE Tokenization** | Byte-pair encoding for sub-word tokenization handling camelCase/snake_case | Low | Low - LLMs have built-in tokenizers |
| **Resolution Localization Algorithm** | Finds unique prefix/suffix to bookend resolution region in merged file | Medium | High - Useful for extracting training examples from Git history |
| **Confidence Thresholding** | Softmax probability cutoff to suppress low-confidence predictions | Low | High - LLMs provide logprobs; can implement similar confidence gating |
| **Bi-directional GRU Encoder** | Captures both forward and backward context in conflict region | High | Low - LLMs already have bidirectional attention |
| **Beam Search Decoding** | Produces top-k resolution candidates | Medium | Medium - Can prompt LLM for multiple alternatives |
| **CONCAT vs OTHER Classification** | Distinguishes simple concatenation (AB/BA) from complex interleaving | Low | High - Quick heuristic check before invoking full resolution |

## Actionable Improvements for lz-git.conflict

### Priority 1: High Impact, Low Effort

1. **Implement Resolution Pattern Detection**
   - Check if conflict can be resolved by simple concatenation (AB or BA order)
   - DeepMerge shows 27% of non-trivial resolutions are CONCAT class with 44% accuracy
   - **Action**: Add heuristic in conflict-resolver agent to try concat patterns first

2. **Add Confidence-Based Gating**
   - Only auto-apply resolutions when LLM confidence is high
   - Present uncertain cases with multiple options for user selection
   - **Action**: Parse LLM response for confidence indicators; implement `--auto-threshold` flag

3. **Structure Prompts with Edit-Aware Format**
   - Present conflicts showing explicit edit operations (additions, deletions, modifications)
   - DeepMerge's aligned linearized format improved accuracy by 21% over naive concatenation
   - **Action**: Enhance prompt template to include diff-style markers and edit summaries

### Priority 2: Medium Impact, Medium Effort

4. **Implement Line-Level Output Constraint**
   - Instruct LLM to construct resolution only from existing lines in A and B
   - Validate output contains only input lines (80% of real resolutions follow this)
   - **Action**: Add post-processing validation; reject resolutions with novel code unless explicitly requested

5. **Build Resolution Localization for Learning**
   - Use paper's algorithm to extract historical resolutions from repository
   - Build project-specific few-shot examples
   - **Action**: Create `/conflict learn` command to mine repository history

6. **Size-Based Strategy Selection**
   - Route small conflicts (<=3 lines) to aggressive auto-resolution (78% accuracy expected)
   - Route large conflicts (>10 lines) to human review with suggestions
   - **Action**: Add conflict size analysis to status command; adjust resolution strategy

### Priority 3: Lower Priority / Future Research

7. **Multi-Candidate Generation**
   - Generate top-3 resolution candidates (improves hit rate from 36.5% to 43.2%)
   - Present ranked options to user
   - **Action**: Add `--candidates` flag to resolve command

8. **Semantic Validation Integration**
   - Paper notes need for parsing/typechecking to prune invalid resolutions
   - Combine with existing lint/build checks
   - **Action**: Hook into project's CI validation post-resolution

9. **Repository-Specific Pattern Mining**
   - Track resolution patterns per repository/team
   - Build project-specific heuristics (similar to SCANMERGE baseline)
   - **Action**: Future feature for team patterns prediction

## Integration Opportunities with LLM-Based Approaches

### Prompt Engineering Insights

The paper validates several principles directly applicable to LLM prompting:

1. **Edit-Aware Context**: Structure prompts to explicitly show:
   ```
   BASE (common ancestor):
   [lines]

   OURS (your changes):
   [lines with +/- markers showing edits from BASE]

   THEIRS (incoming changes):
   [lines with +/- markers showing edits from BASE]
   ```

2. **Output Constraint**: Explicitly instruct:
   ```
   Construct the resolution using ONLY lines from OURS and THEIRS.
   Do not write new code unless both versions are semantically incompatible.
   ```

3. **Confidence Elicitation**: Request:
   ```
   Rate your confidence (HIGH/MEDIUM/LOW) in this resolution.
   If LOW, explain what additional context would help.
   ```

### Few-Shot Learning Adaptation

DeepMerge's training data approach can inform few-shot example selection:

1. **Filter trivial cases**: Don't use "ours/theirs" resolutions as examples
2. **Stratify by size**: Include examples from each size bucket (1-3, 4-5, 6-7, 8-10, 10+ lines)
3. **Include CONCAT and OTHER**: Show both simple concatenation and complex interleaving patterns
4. **Use repository-local examples**: Mine from current repo's merge history for domain relevance

### Hybrid Architecture Potential

The paper suggests combining approaches:
- Use LLM for semantic understanding (intent, dependencies, side effects)
- Use DeepMerge-style constraints for output construction
- Use structured merge for syntax validation

**Proposed pipeline**:
```
1. LLM analyzes conflict semantics -> determines resolution strategy
2. If strategy is "combine both":
   - LLM determines line ordering
   - Validate output uses only input lines
3. If strategy is "choose one":
   - LLM explains which version and why
4. If strategy is "rewrite needed":
   - LLM generates new code
   - Flag for human review
```

## Evaluation Metrics for Plugin

Adopt DeepMerge's metrics for measuring plugin effectiveness:

| Metric | Definition | Target |
|--------|------------|--------|
| **Top-1 Accuracy** | Exact match with actual resolution | >40% (exceeds DeepMerge's 36.5%) |
| **Top-3 Accuracy** | Correct resolution in top 3 suggestions | >50% |
| **Precision@threshold** | Correctness when confidence > threshold | >70% at 0.5 threshold |
| **Recall@threshold** | Coverage when confidence > threshold | >30% at 0.5 threshold |
| **BLEU-4 Score** | N-gram similarity for partial matches | >50% |
| **Size-stratified accuracy** | Accuracy by conflict size | >75% for <=3 lines |

## Limitations and Caveats

1. **JavaScript-specific training**: Results may not transfer directly to other languages
2. **Line-level granularity**: Cannot handle token-level merges within lines
3. **No semantic verification**: Syntactic correctness doesn't guarantee semantic correctness
4. **Dataset bias**: Filtered to "valid merges" incorporating both changes; may miss legitimate "drop one side" cases
5. **30-line limit**: Model trained with max 30 lines in resolution

## Relevance Score

**Overall Relevance: 9/10**

| Aspect | Score | Rationale |
|--------|-------|-----------|
| Architectural Insights | 8/10 | Pointer network concept validates line-selection approach; directly applicable to prompt design |
| Training Data Methodology | 9/10 | Resolution localization algorithm highly useful for building few-shot examples |
| Evaluation Framework | 10/10 | Comprehensive metrics directly adoptable for plugin evaluation |
| Semantic Analysis | 6/10 | Limited semantic understanding; LLMs can exceed this |
| Practical Integration | 9/10 | Confidence thresholding, size-based routing immediately implementable |
| LLM Enhancement Potential | 10/10 | Paper explicitly notes future direction of combining with program analysis - LLMs fill this gap |

The paper provides the strongest empirical foundation for the core assumption that merge resolution is primarily a **selection and ordering problem**, not a generation problem. This insight should fundamentally shape how the lz-git.conflict plugin prompts and validates LLM outputs.
