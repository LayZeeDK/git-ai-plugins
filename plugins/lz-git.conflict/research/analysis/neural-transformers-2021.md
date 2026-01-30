# Neural Transformers for Merge Conflict Resolution (2021)

**Paper**: Program Merge Conflict Resolution via Neural Transformers
**Authors**: Svyatkovskiy, Fakhoury, Ghorbani, Mytkowicz, Dinella, Bird, Jang, Sundaresan, Lahiri
**Venue**: ESEC/FSE 2022
**arXiv**: 2109.00084v4

## Key Findings

### 1. Token-Level Differencing is Superior to Line-Level

MergeBERT's core innovation is applying diff3 at **token granularity** rather than line granularity:

- **74%** of token-level resolutions are simply choosing `a` or `b`
- **23%** are concatenations (`a+b` or `b+a`)
- **0.4%** take the base `o`
- **1.8%** are variants with base tokens removed
- Only **9 primitive merge patterns** cover the vast majority of resolutions

This transforms the complex generative problem into a **classification task** over 9 patterns.

### 2. Performance Metrics

| Approach | Granularity | Precision | Accuracy |
|----------|-------------|-----------|----------|
| Language Model | Line | 3.6% | 3.1% |
| DeepMerge | Line | 55.0% | 35.1% |
| diff3 | Token | 82.4% | 36.1% |
| DeepMerge | Token | 64.5% | 42.7% |
| **MergeBERT** | **Token** | **69.1%** | **68.2%** |

MergeBERT achieves **2-3x improvement** over prior neural approaches and structured merge tools.

### 3. User Study Insights (Critical for LLM Integration)

From 122 real-world conflicts evaluated by 25 developers:

- **54%** of MergeBERT suggestions were acceptable (even when not exact matches)
- **45%** were semantically equivalent despite syntactic differences
- **16%** of conflicts required **external context** (project rules, linter settings, language updates)
- **29%** were genuinely incorrect without needing external context

**Key Insight**: Strict string matching underestimates actual utility. Semantic equivalence checking is essential.

### 4. Multi-Language Generalization

MergeBERT works across JavaScript, TypeScript, Java, and C# with consistent 63-69% precision:

- Monolingual vs multilingual models show **negligible performance difference**
- Only requires: tokenizer + parser + training data per language
- **97%+ syntactic correctness** across all languages

### 5. Edit-Type Embeddings Matter

Ablation study shows edit-aware encoding improves accuracy from 63% to 68%:
- Edit types: `=` (equal), `+` (insert), `-` (delete), `<->` (replace), `null` (pad)
- Captures the transformation semantics between versions

## Techniques

| Technique | Description | Implementation Complexity | LLM Adaptation |
|-----------|-------------|---------------------------|----------------|
| **Token-level diff3** | Apply diff3 at token granularity instead of lines | Medium | Direct - preprocess conflicts before LLM |
| **Resolution as Classification** | 9 primitive patterns cover 98%+ of resolutions | Low | Few-shot prompt with pattern examples |
| **Multi-input Encoder** | Encode (a\|o, o\|a, b\|o, o\|b) separately then aggregate | High | N/A - use LLM's native context window |
| **Edit Sequence Embedding** | Encode edit operations (=, +, -, <->) as type embeddings | Medium | Include edit annotations in prompt |
| **BPE Tokenization** | Byte-pair encoding for code identifiers | Low | Use LLM's native tokenizer |
| **Syntax Validation** | Filter suggestions through tree-sitter parser | Low | Add syntax check post-generation |
| **Beam Search Decoding** | For multiple token-level conflicts per line-level conflict | Medium | Generate multiple completions |
| **Context Window** | Include prefix/suffix around conflict (512 BPE tokens) | Low | Standard context inclusion |
| **Pairwise Alignment** | Align a/b with base o to compute edit sequences | Medium | Annotate conflicts with alignment info |

## Actionable Improvements for lz-git.conflict

### Priority 1: Token-Level Preprocessing (High Impact, Low Effort)

**Current Gap**: Plugin likely operates at line level like standard Git.

**Implementation**:
```javascript
// Before sending to LLM, convert line-level conflict to token-level
function tokenizeConflict(conflict) {
  const aTokens = tokenize(conflict.ours);
  const bTokens = tokenize(conflict.theirs);
  const oTokens = tokenize(conflict.base);

  // Apply diff3 at token level
  const tokenConflict = diff3(aTokens, oTokens, bTokens);

  // Non-conflicting tokens become context
  return {
    prefix: tokenConflict.mergedPrefix,
    conflict: tokenConflict.remaining,
    suffix: tokenConflict.mergedSuffix
  };
}
```

**Benefit**: Localizes conflicts, often resolving portions automatically.

### Priority 2: Classification-Based Prompting (High Impact, Medium Effort)

**Strategy**: Frame resolution as choosing among 9 primitive patterns rather than open generation.

**Prompt Template**:
```
Given this token-level conflict:
<<<<<<< OURS
{a_tokens}
||||||| BASE
{o_tokens}
=======
{b_tokens}
>>>>>>> THEIRS

Choose the resolution pattern:
1. a (take ours)
2. b (take theirs)
3. o (keep base)
4. a+b (ours then theirs)
5. b+a (theirs then ours)
6. a-o (ours minus base overlap)
7. b-o (theirs minus base overlap)
8. (a+b)-o (combined minus base)
9. (b+a)-o (combined reverse minus base)

Analyze the semantic intent of each change and select the pattern number.
```

**Benefit**: Constrains LLM output to valid patterns, improving reliability.

### Priority 3: Semantic Equivalence Checking (Medium Impact, Medium Effort)

**Insight from User Study**: 45% of acceptable resolutions were semantically equivalent but syntactically different.

**Implementation**:
```javascript
async function validateResolution(original, suggested, language) {
  // 1. Parse both to AST
  const originalAST = parse(original, language);
  const suggestedAST = parse(suggested, language);

  // 2. Normalize (remove comments, standardize formatting)
  const normalizedOriginal = normalize(originalAST);
  const normalizedSuggested = normalize(suggestedAST);

  // 3. Check structural equivalence
  if (astEqual(normalizedOriginal, normalizedSuggested)) {
    return { equivalent: true, type: 'structural' };
  }

  // 4. Check for reordering of independent statements
  if (canReorder(normalizedOriginal, normalizedSuggested)) {
    return { equivalent: true, type: 'reorderable' };
  }

  return { equivalent: false };
}
```

### Priority 4: Edit Sequence Annotation (Medium Impact, Low Effort)

**Technique**: Annotate conflicts with edit operations to help LLM understand transformations.

**Enhanced Conflict Format**:
```
BASE:    x = max(y, 10)
OURS:    x = max(y, 11)      [EDIT: 10->11]
THEIRS:  x = max(y, 12, z)   [EDIT: 10->12, INSERT: z]

The edits are:
- OURS changes argument from 10 to 11
- THEIRS changes argument from 10 to 12 AND adds parameter z

Resolution should incorporate both changes: x = max(y, 12, z)
(Taking THEIRS which subsumes OURS's numeric change and adds z)
```

### Priority 5: Syntax Validation Gate (Low Impact, Low Effort)

**Implementation**: Already mentioned in paper - use tree-sitter to validate suggestions.

```javascript
const Parser = require('tree-sitter');

function isValidSyntax(code, language) {
  const parser = new Parser();
  parser.setLanguage(getLanguage(language));
  const tree = parser.parse(code);
  return tree.rootNode.hasError === false;
}

// Filter LLM suggestions
const validSuggestions = suggestions.filter(s => isValidSyntax(s, language));
```

### Priority 6: External Context Detection (Future Enhancement)

**User Study Finding**: 16% of conflicts require external context.

**Detection Heuristics**:
- Linter rule references (eslint, prettier configs)
- Project-wide patterns (naming conventions)
- Language version features (C# 8.0 `using` syntax)
- Dependency changes outside conflict region

**Implementation**: Add a confidence score and flag conflicts likely needing human review:

```javascript
function assessContextRequirement(conflict, projectContext) {
  const signals = [];

  // Check for linter-related patterns
  if (conflict.involves('formatting', 'whitespace', 'semicolons')) {
    signals.push({ type: 'linter', confidence: 0.7 });
  }

  // Check for language feature patterns
  if (conflict.involves('var/let/const', 'using', 'async/await')) {
    signals.push({ type: 'language-update', confidence: 0.6 });
  }

  // Check for cross-file dependencies
  if (conflict.referencesModifiedFiles(projectContext)) {
    signals.push({ type: 'cross-file', confidence: 0.8 });
  }

  return signals.length > 0
    ? { needsReview: true, signals }
    : { needsReview: false };
}
```

## Evaluation Metrics for Resolution Quality

### Metrics from Paper

| Metric | Description | Use Case |
|--------|-------------|----------|
| **Precision@k** | Correct in top-k when suggestion provided | Measure suggestion quality |
| **Accuracy@k** | Correct in top-k across all conflicts | Measure overall coverage |
| **Syntactic Correctness** | Parses without errors | Baseline quality gate |
| **Semantic Equivalence** | AST-normalized match | Capture acceptable alternatives |
| **Coverage Rate** | % of conflicts with any suggestion | Measure applicability |

### Recommended Metrics for lz-git.conflict

1. **Resolution Acceptance Rate**: User accepts/rejects in workflow
2. **Edit Distance**: Levenshtein distance from accepted resolution (measures "how close")
3. **Pattern Match Rate**: How often LLM selects one of 9 primitive patterns
4. **Conflict Localization**: Reduction in conflict size after token-level preprocessing
5. **Time to Resolution**: Comparative time with/without tool assistance

## Integration Opportunities with LLM-Based Approaches

### 1. Few-Shot Learning with Primitive Patterns

The 9 primitive patterns are ideal for few-shot prompting:

```
Example 1 (Pattern: b - take theirs):
Conflict: config.timeout = [10|5|15]
Resolution: config.timeout = 15
Reason: Theirs (15) is a deliberate update over base (5)

Example 2 (Pattern: a+b - ours then theirs):
Conflict: imports = [import A|import A|import A, B]
Resolution: import A, B
Reason: Both branches added imports, combine them

[... 7 more examples covering each pattern ...]

Now resolve:
{actual_conflict}
```

### 2. Chain-of-Thought for Complex Conflicts

For the 5% of conflicts with multiple token-level conflicts per line:

```
Step 1: Identify all token-level conflicts in this line-level conflict
Step 2: For each token conflict, determine the semantic intent
Step 3: Check for dependencies between token conflicts
Step 4: Resolve each independently or jointly as needed
Step 5: Combine resolutions and validate syntax
```

### 3. Retrieval-Augmented Generation (RAG)

Use project history for context:
- Retrieve similar past conflicts and their resolutions
- Include team's resolution patterns as examples
- Reference project style guides and conventions

### 4. Multi-Turn Clarification

For the 16% requiring external context:
```
LLM: "This conflict involves a change to the `using` statement syntax.
      Is this project using C# 8.0+ with the new using declaration syntax?
      [Yes - use new syntax] [No - keep traditional] [Unsure - show both]"
```

## Relevance Score

**Overall Relevance: 9/10**

| Aspect | Score | Rationale |
|--------|-------|-----------|
| Model Architecture | 6/10 | Specific to fine-tuned BERT; LLMs don't need this architecture |
| Training Data Approach | 8/10 | Mining merge commits is directly applicable for few-shot examples |
| Token-Level Differencing | 10/10 | Directly applicable preprocessing step |
| Classification Framing | 10/10 | Perfect for LLM prompting - constrained output space |
| Evaluation Methodology | 9/10 | Metrics and user study methodology directly applicable |
| Semantic Equivalence Insight | 10/10 | Critical for acceptance criteria |
| External Context Detection | 8/10 | Important for knowing when to defer to human |

### Key Takeaways for lz-git.conflict

1. **Token-level preprocessing should be the first enhancement** - it's low effort and high impact
2. **Frame resolution as classification** over 9 patterns rather than open-ended generation
3. **Don't aim for exact match** - semantic equivalence is the real goal
4. **Flag conflicts needing external context** rather than guessing incorrectly
5. **Syntax validation is a cheap quality gate** - always parse before accepting
6. **User study methodology** is valuable for evaluating the plugin with real developers

### Limitations for LLM Adaptation

1. Paper's model requires fine-tuning; LLMs work via prompting (different paradigm)
2. 512 token limit in paper is much smaller than modern LLM context windows
3. Multi-input encoder architecture doesn't translate to prompt-based approaches
4. BPE vocabulary was code-specific; general LLMs have broader tokenization

Despite these differences, the **conceptual insights** (token-level diffing, classification framing, semantic equivalence) are highly transferable to LLM-based conflict resolution.
