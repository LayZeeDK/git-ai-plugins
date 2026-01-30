# Search-Based Merge Conflict Resolution Analysis

**Paper**: Towards a feasible evaluation function for search-based merge conflict resolution (2025)
**Authors**: Campos Junior, de Menezes, Barros, van der Hoek, Murta
**Published**: ACM Transactions on Software Engineering and Methodology, July 2025
**Dataset**: 9,998 conflict chunks from 1,062 open-source Java projects

## Key Findings

### 1. Parent Similarity as Quality Proxy

The paper's central discovery is that **conflict resolutions are approximately 70% similar to both parent versions (V1 and V2)**. This finding enables using parent similarity as a computationally cheap evaluation function for search-based approaches, avoiding expensive compilation and test execution.

Key statistics:
- Mean similarity to V1: 70.9%
- Mean similarity to V2: 70.2%
- Median similarity to both parents: ~79%
- 75% of resolutions have >60% similarity with both parents

### 2. Strong Correlation for Evaluation Functions

A strong median correlation (rho = 0.791) exists between:
- Candidate-to-parent similarity
- Candidate-to-resolution similarity

This means maximizing parent similarity effectively guides toward correct resolutions.

### 3. Mean Aggregation Function Performs Best

When aggregating similarity scores from both parents, the **mean function** shows the strongest correlation with resolution quality:

| Aggregation | Median Correlation |
|-------------|-------------------|
| **Mean**    | **0.791**         |
| Max         | 0.783             |
| Harmonic    | 0.755             |
| Min         | 0.695             |

### 4. Resolution Composition

87% of conflict resolutions are composed **only from existing conflicting lines** (no new content), making search-based line recombination highly applicable.

### 5. SBCR Performance Results

The Search-Based Conflict Resolution approach achieved:
- Median similarity to developer resolution: **86.5%**
- Exact match rate (100% similarity): **25.2%**
- Median execution time: **2.56 seconds**
- 75% resolved in under 10.5 seconds

### 6. Edge Cases Identified

Weak correlation scenarios:
- **Empty parent versions**: 93.3% of high Sim_r-p cases have one parent empty
- **Large size disparities**: When resolution is much smaller than conflict chunk
- Developer simplification patterns: removing unused code, consolidating operations

## Techniques

| Technique | Description | Implementation Complexity |
|-----------|-------------|--------------------------|
| **LCS-Based Gestalt Similarity** | Character-level Longest Common Subsequence with Gestalt pattern matching: `2*LCS(t1,t2) / (|t1|+|t2|)` | Low - O(m*n) algorithm, well-understood |
| **Partial Order Candidate Generation** | Random candidates preserving line order from V1/V2: randomly interleave lines while maintaining relative ordering | Low - Simple algorithm, 98.6% of resolutions preserve partial order |
| **Mean Parent Similarity Aggregation** | `(Sim(C,V1) + Sim(C,V2)) / 2` as single-objective fitness function | Trivial - Simple arithmetic |
| **Random Restart Hill Climbing (RRHC)** | Local search with neighborhood operations: add line, remove line, swap positions | Medium - Standard optimization algorithm |
| **Sim_r-p Discrepancy Analysis** | `Sim_r - Sim_p` metric to identify problematic conflicts where parent similarity fails | Low - Simple difference calculation |
| **Search Space Reduction Heuristics** | Prior work shows 94.7% reduction possible via conflict-specific heuristics | Medium - Requires heuristic development |

## Actionable Improvements for lz-git.conflict

### Priority 1: Core Integration (High Impact, Low Effort)

1. **Implement Parent Similarity Scoring**
   - Add LCS-based Gestalt similarity calculation
   - Score candidate resolutions against both parent versions
   - Use mean aggregation for combined fitness score
   - Display confidence indicator based on correlation strength

2. **Partial Order Constraint**
   - Ensure generated resolutions maintain relative line ordering from each parent
   - Reject candidates that violate partial order (only 1.4% of resolutions do)

3. **Edge Case Detection**
   - Flag conflicts with empty V1 or V2 (parent similarity less reliable)
   - Warn when chunk/resolution size ratio exceeds threshold
   - Suggest manual review for low-correlation scenarios

### Priority 2: Search Enhancement (Medium Impact, Medium Effort)

4. **Hill Climbing Integration**
   - Implement RRHC for complex conflicts
   - Neighborhood operations: add/remove/swap lines
   - Parameters: 5 neighbors/iteration, 10 stagnation limit, 15s timeout
   - Target: conflicts with >4 lines where simple heuristics fail

5. **Candidate Ranking**
   - Generate multiple candidates via search
   - Rank by mean parent similarity
   - Present top-N candidates to user or LLM for selection

6. **Hybrid LLM-Search Approach**
   - Use search-based candidates as "seed" resolutions for LLM refinement
   - LLM handles the 13% of cases requiring new/modified lines
   - Search narrows solution space, LLM provides semantic understanding

### Priority 3: Quality Metrics (Medium Impact, Low Effort)

7. **Resolution Quality Prediction**
   - Classify conflicts by expected correlation strength
   - Use Sim_r-p analysis to predict resolution difficulty
   - Route difficult conflicts to appropriate resolution strategy

8. **Validation Without Tests**
   - Parent similarity provides rapid feedback without compilation
   - Useful for CI/CD integration where test execution is costly
   - Can validate LLM-generated resolutions before presenting to user

### Priority 4: Advanced Features (Lower Priority)

9. **Team Pattern Learning**
   - Track correlation strengths per project/team
   - Identify recurring conflict patterns with high success rates
   - Build project-specific resolution strategies

10. **Multi-Language Extension**
    - Paper uses Java but approach is language-agnostic (text-based)
    - Apply same similarity metrics to any programming language
    - Character-level LCS works across all file types

## Integration Opportunities with LLM-Based Approaches

### Complementary Strengths

| Aspect | Search-Based (SBCR) | LLM-Based |
|--------|---------------------|-----------|
| Coverage | 87% (line recombination) | 100% (can generate new code) |
| Speed | ~2.5s median | Variable (API latency) |
| Interpretability | High (similarity scores) | Lower (black box) |
| Cost | CPU only | API costs |
| Determinism | Reproducible | Non-deterministic |

### Hybrid Architecture

```
Conflict Input
      |
      v
+---------------------+
| Edge Case Detector  |  <- Empty parent? Size disparity?
+---------------------+
      |
      +---> [Edge Case] --> LLM Direct Resolution
      |
      v
+---------------------+
| Search-Based SBCR   |  <- Generate candidates via RRHC
+---------------------+
      |
      v
+---------------------+
| Candidate Ranking   |  <- Mean parent similarity
+---------------------+
      |
      +---> [High Confidence (>90%)] --> Auto-resolve or suggest
      |
      +---> [Medium Confidence] --> LLM refinement
      |
      +---> [Low Confidence] --> Manual review with LLM assistance
```

### Specific Integration Points

1. **Pre-LLM Filtering**: Use parent similarity to filter obviously poor LLM suggestions
2. **LLM Prompt Seeding**: Provide search-generated candidates as examples in prompt
3. **Confidence Calibration**: Combine parent similarity with LLM confidence scores
4. **Fallback Strategy**: Search-based when LLM unavailable or times out
5. **Cost Optimization**: Use search for simple conflicts, reserve LLM for complex ones

## Metrics for Comparing Resolution Approaches

### Primary Metrics (from paper)

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| Gestalt Similarity | `2*LCS(C,R) / (|C|+|R|)` | 0-100% match to developer resolution |
| Parent Correlation | Spearman's rho | Strength of evaluation function |
| Exact Match Rate | % with 100% similarity | Fully automated resolutions |
| Execution Time | Seconds per conflict | Practical deployment feasibility |

### Recommended Benchmarking

1. **Resolution Similarity**: Compare generated vs developer resolution
2. **Compilation Success**: Does merged file compile?
3. **Test Pass Rate**: Do existing tests pass?
4. **Time-to-Resolution**: Wall clock including user interaction
5. **User Acceptance Rate**: For suggested resolutions

### Baseline Comparisons

- **Random Selection**: Select V1 or V2 entirely
- **Line-by-Line Greedy**: Pick each line from higher-similarity parent
- **SBCR (this paper)**: 86.5% median similarity
- **LLM-Only**: Compare with GPT-4/Claude direct resolution
- **Hybrid**: Combined approach

## Relevance Score

**Overall Relevance: 9/10**

### Scoring Breakdown

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Technical Applicability | 10/10 | Directly addresses conflict resolution evaluation |
| Implementation Feasibility | 9/10 | Algorithms are straightforward, well-documented |
| LLM Integration Potential | 9/10 | Natural complement to semantic approaches |
| Dataset Validity | 8/10 | Large-scale Java study, language-agnostic technique |
| Novelty for Plugin | 9/10 | First principled evaluation function for this domain |

### Why High Relevance

1. **Solves Core Problem**: Provides computationally cheap fitness function for resolution candidates
2. **Proven Results**: 86.5% similarity with 2.5s execution is production-viable
3. **Complements LLMs**: Handles 87% of cases that are pure recombination
4. **Clear Integration Path**: Simple metrics that enhance existing commands
5. **Edge Case Guidance**: Identifies when approach may fail, enabling fallback strategies

### Limitations to Consider

- Java-only validation (though technique is language-agnostic)
- Does not handle resolutions requiring new code (13% of cases)
- Correlation varies by conflict type (some plateaus in search landscape)
- No semantic validation (syntactic similarity only)

## Implementation Roadmap for lz-git.conflict

### Phase 1: Foundation (1-2 weeks)
- Implement Gestalt similarity function
- Add parent similarity calculation to conflict analysis
- Display similarity scores in `/status` output

### Phase 2: Candidate Generation (2-3 weeks)
- Build partial order candidate generator
- Implement mean parent similarity ranking
- Add candidate suggestions to `/resolve` command

### Phase 3: Search Integration (2-4 weeks)
- Implement RRHC algorithm for complex conflicts
- Add edge case detection
- Create hybrid LLM-search resolution strategy

### Phase 4: Evaluation & Tuning (ongoing)
- Benchmark against manual resolutions
- Track correlation by conflict type
- Optimize parameters per project

## References

- Campos Junior et al. 2024: Search space reduction heuristics (94.7% reduction)
- Ghiotto et al. 2020: Original conflict dataset and 87% line recombination finding
- Boll et al. 2024: Semi-automated merge conflict resolution study
- Dong et al. 2023: MergeGen LLM approach for comparison

---

*Analysis generated for lz-git.conflict plugin research*
