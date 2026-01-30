# Using Pre-trained Language Models to Resolve Textual and Semantic Merge Conflicts (ISSTA 2022) Analysis

## Key Findings

- **k-shot learning with GPT-3 achieves 64.6% accuracy** on semantic merge conflict resolution in Microsoft Edge, outperforming heuristic-based (30.1%) and program synthesis (25.9%) approaches
- **Semantic merge conflicts** (code compiles after merge but is broken) are distinct from textual conflicts; they require understanding upstream changes to repair downstream code
- **Prompt engineering is critical**: One-shot with heuristic-based content selection (64.6%) significantly outperforms zero-shot (40.0%) and naive content selection (60.4%)
- **Model size matters**: GPT-3 (175B params) achieves 64.6% vs GPT-J (6B params) at 39.1% - larger models better capture complex transformation patterns
- **Multiple trials improve accuracy**: 10 independent model queries boost accuracy from 37.2% (single trial) to 64.6%
- **Data curation is essential**: Automatically extracting relevant upstream changes from compiler error messages enables the LLM to focus on the right context
- **LLMs handle complex patterns** that rigid DSL-based synthesis cannot: multi-file renames, cascading naming convention changes, and combined transformations

## Relevant Techniques for lz-git.conflict

| Technique | Description | Plugin Application | Implementation Complexity |
|-----------|-------------|-------------------|--------------------------|
| **k-shot prompting with conflict examples** | Provide 1-2 historical resolved conflicts as "shots" before the query conflict | Use in `/resolve` command to show Claude example resolutions before asking it to resolve current conflict | Low - structure prompts with Question/Answer format |
| **Distinct edit sequence heuristic** | Prioritize upstream changes with different string edit patterns (add/delete/replace) | When multiple hunks exist, select diverse examples to fit context window | Medium - requires diff analysis |
| **Compiler error keyword extraction** | Parse error messages to identify renamed/missing symbols, then search commit history | For semantic conflict detection post-merge - trace undefined symbols to upstream renames | High - requires language-specific error parsing |
| **JSON intermediate representation** | Structure conflict data as `{UpstreamChanges[], DownstreamConflict, DownstreamFix}` | Standardize conflict representation for consistent prompting | Low - define JSON schema for conflicts |
| **Multiple model trials with union** | Query model 10 times, accept if any trial produces correct resolution | Offer multiple resolution candidates, let user choose | Low - generate alternatives |
| **Prefix-based accuracy metric** | Resolution correct if ground truth is prefix of model output | Useful for evaluation - allow trailing tokens in suggestions | Low - simple string comparison |
| **Divergent fork conflict model** | Track upstream (Chromium) vs downstream (Edge) changes separately | Adapt for team branches - "main" as upstream, feature as downstream | Medium - branch relationship tracking |

## Actionable Improvements

### 1. Add Few-Shot Prompting to conflict-resolver Agent (High Impact)

**Current state**: The `conflict-resolver` agent uses semantic analysis but doesn't explicitly structure prompts with resolved examples.

**Improvement**: Inject 1-2 resolved conflict examples from the same repository (or from skill examples) before presenting the current conflict.

**Implementation**:
```markdown
# In conflict-resolver.md or resolve.md
## Resolution Context
Before resolving, I will:
1. Search git log for recent commits that resolved conflicts in similar files
2. Extract the before/after patterns from those resolutions
3. Use them as few-shot examples when analyzing current conflict
```

**Expected benefit**: Based on paper, this alone could improve resolution quality by ~25% (comparing zero-shot 40% to one-shot 64.6%).

---

### 2. Implement Semantic Conflict Detection Post-Merge (High Impact)

**Current state**: Plugin detects textual conflicts via git markers but not semantic conflicts (code compiles but is broken).

**Improvement**: After a clean merge, run lightweight checks for:
- Undefined references that existed before merge
- Renamed symbols in upstream that downstream still references
- Import/include mismatches

**Implementation**: Add to `PostToolUse` hook for `git merge`:
```javascript
// In detect-conflicts.js
if (mergeSucceeded && !hasConflictMarkers) {
  // Check for semantic conflicts
  const upstreamChanges = extractRecentUpstreamRenames();
  const downstreamReferences = findReferencesToOldNames();
  if (downstreamReferences.length > 0) {
    return { additionalContext: "Potential semantic conflicts detected..." };
  }
}
```

**Expected benefit**: Catches the "silently broken" merges that are 26x more likely to cause bugs (per paper's cited statistics).

---

### 3. Structured Conflict Representation (Medium Impact)

**Current state**: Conflicts shown as raw git diff markers.

**Improvement**: Parse conflicts into structured JSON for cleaner prompting:
```json
{
  "file": "src/browser.ts",
  "upstreamChanges": [
    {"before": "isIncognito()", "after": "getIncognito()"}
  ],
  "conflictRegion": {
    "ours": "browser.isIncognito()",
    "theirs": "browser.getIncognito()"
  }
}
```

**Implementation**: Add parsing utility in skills or hook scripts.

**Expected benefit**: Cleaner LLM input, easier to validate resolutions, supports the "distinct edit sequence" heuristic.

---

### 4. Multi-Candidate Resolution with Ranking (Medium Impact)

**Current state**: Agent proposes single resolution.

**Improvement**: Generate 3-5 candidate resolutions (via temperature variation or rephrasing), present ranked by confidence.

**Implementation**:
```markdown
# In resolve.md
## Resolution Candidates
I'll generate multiple resolution options:
1. [Most likely] Apply upstream rename pattern
2. [Alternative] Keep downstream version, add compatibility wrapper
3. [Alternative] Merge both changes with deduplication
```

**Expected benefit**: Paper shows 10 trials boost accuracy from 37% to 65%. Even 3-5 alternatives give user choice.

---

### 5. Track Resolution History for Learning (Low Impact, Enables Future)

**Current state**: No persistence of resolution decisions.

**Improvement**: Log resolved conflicts to `.claude/lz-git.conflict.history.json`:
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "file": "src/auth.ts",
  "pattern": "rename",
  "upstreamChange": "isLoggedIn -> getIsLoggedIn",
  "resolution": "applied-rename",
  "accepted": true
}
```

**Implementation**: Append to history file after each resolution.

**Expected benefit**: Enables few-shot example retrieval from same repository (most relevant examples), supports future "team patterns" feature.

---

### 6. Upstream Change Mining Command (Low Impact)

**Current state**: No tooling to analyze what changed upstream before resolving.

**Improvement**: Add `/lz-git.conflict:analyze-upstream` command that:
1. Identifies the merge base
2. Extracts relevant symbol renames/changes from upstream commits
3. Presents context before resolution

**Implementation**: Git commands + grep for changed function/class names.

**Expected benefit**: Matches paper's "data curation" phase - gives Claude (and user) the context needed to understand why conflict exists.

## Technical Insights for Prompt Engineering

### Effective Prompt Structure (from paper's Figure 6)
```
Question:
--<old upstream code>
++<new upstream code>

-<downstream conflict line>

Answer:
+<resolution>
```

The double `--`/`++` prefix indicates upstream changes, single `-`/`+` indicates downstream conflict/resolution. This clear visual syntax helps the model distinguish context from task.

### Content Selection Heuristics

When upstream changes are large (thousands of lines), use the paper's "distinct edit sequence" heuristic:
1. Compute string diff between each `before`/`after` pair
2. Categorize by operation type: addition (+), deletion (-), replacement (|)
3. Select one example of each unique edit pattern
4. Prioritize patterns most similar to the current conflict

### Token Budget Management

GPT-3's 2048 token limit (paper's constraint) is less relevant for Claude, but the principle applies:
- Include minimal but diverse upstream context
- One clear shot is better than multiple noisy examples
- The conflict itself should have room for full context

## Evaluation Metrics

| Metric | Description | Plugin Use |
|--------|-------------|------------|
| **Prefix accuracy** | Ground truth is prefix of output | Accept resolutions with trailing whitespace/comments |
| **Exact match** | Output equals ground truth exactly | Strictest validation |
| **Compile success** | Resolved code compiles | Validate with language server if available |
| **Test pass** | Resolved code passes tests | Run tests after resolution (future enhancement) |

## Limitations Noted in Paper

1. **Relies on compiler errors**: Semantic conflict detection requires parseable error messages
2. **No guarantees**: LLM suggestions need human verification
3. **Context-dependent**: Performance varies by conflict complexity
4. **Token limits**: Complex conflicts may exceed context window

## Relevance Score: High

This paper directly addresses the lz-git.conflict plugin's core use case with empirical validation on a real-world codebase (Microsoft Edge). The k-shot learning approach is immediately applicable to Claude-based resolution. Key findings about prompt structure, model size benefits, and the importance of upstream context mining provide actionable guidance for plugin enhancement.

**Priority integration points**:
1. Few-shot prompting (immediate, high impact)
2. Semantic conflict detection (medium-term, high value)
3. Structured conflict representation (supports both above)
