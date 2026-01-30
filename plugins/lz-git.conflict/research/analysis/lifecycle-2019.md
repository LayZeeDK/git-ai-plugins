# Analysis: The Life-cycle of Merge Conflicts (2019)

**Paper**: The life-cycle of merge conflicts: processes, barriers, and strategies
**Authors**: Nelson, Brindescu, McKee, Sarma, Dig
**Year**: 2019
**Citation**: Empirical Software Engineering (2019) 24:2863–2906

---

## Key Findings

### Developer Process Model
The study introduces a **4-phase life-cycle model** for managing merge conflicts:

1. **Awareness Phase**: How developers detect conflicts (mostly reactive)
2. **Planning Phase**: Deciding when/how to resolve (including deferral decisions)
3. **Resolution Phase**: Implementing the fix
4. **Evaluation Phase**: Validating the resolution worked

### Critical Statistics
- **19% of merges** result in conflicts in open source projects
- **56.18%** of developers have deferred merge conflict resolution at least once
- **73.68%** use **reactive monitoring** (detect after conflict occurs) vs. 26.3% proactive
- **78.7%** of developers occasionally fail on first resolution attempt
- **42.15%** experience some degree of toolset mistrust

### Top Factors Affecting Difficulty
1. **Complexity of conflicting code** (mean: 3.52/5)
2. **Expertise in conflict area** (mean: 3.50/5)
3. **Complexity of files** (mean: 3.23/5)
4. **Number of conflicting lines** (mean: 3.14/5)

### Key Developer Needs (Unmet)
1. **Understanding conflicting code** (mean: 3.89/5)
2. **Expertise in conflict area** (mean: 3.72/5)
3. **Contextual information** about changes (mean: 3.62/5)
4. **Better tool presentation** of information (mean: 3.48/5)

---

## Techniques Applicable to Automation

| Technique | Description | Automation Potential | Implementation Notes |
|-----------|-------------|---------------------|---------------------|
| **Reactive vs Proactive Monitoring** | 73.68% use reactive strategies; proactive tools (Crystal, Palantír) exist but underutilized | High | Could implement lightweight conflict prediction based on branch divergence analysis |
| **Complexity-Based Prioritization** | Developers assess complexity before deciding to resolve or defer | Medium | Use cyclomatic complexity, AST depth, number of conflicting locations to estimate difficulty |
| **Visual Inspection Validation** | 74.16% rely on "code looks correct" as success criteria | Low | Hard to automate, but could provide checklist of semantic issues to review |
| **Test-Based Validation** | 75.28% use "all tests pass" as success criteria | High | Already standard practice; ensure tests run automatically post-resolution |
| **Compilation Validation** | 75.28% use "code compiles" as success criteria | High | Already standard; important to detect syntax errors |
| **Expert Recommendation** | Expertise (F2, N2) ranked as top-2 factor/need | Medium | Use git blame, commit history, code ownership to suggest reviewers (like TIPMerge) |
| **History Exploration** | Developers need commit context (who/why/when) | Medium | Provide easy access to related commits, PRs, and issue discussions |
| **Deferral Decision Support** | 56.18% defer based on complexity/ownership | Medium | Provide confidence score or difficulty estimate before resolution |

### Specific Heuristics to Implement

**For Conflict Assessment:**
- Track number of conflicting locations (D2 - 22.22% selection rate)
- Analyze code complexity at conflict sites (D1 - 25.00% selection rate)
- Check code ownership overlap (D3 - 17.36% selection rate)
- Consider size of conflicting changes (D4 - 13.89% selection rate)

**For Resolution Strategies:**
- **Examining the merge** (U1 - 32.91%): Show recent commits with comments
- **Analyzing code** (U2 - 24.05%): Provide AST diff, semantic change summary
- **Examining code** (U3 - 22.79%): Highlight surrounding context, related functions

**For Backup Strategies:**
- **Take offline** (B1 - 25.33%): Create temporary branch automatically
- **Collaborate** (B2 - 22.67%): Suggest expert developers
- **Try again** (B3 - 20.00%): Provide alternative merge strategies
- **Redo changes** (B4 - 18.67%): Last resort; warn user of this risk

---

## Actionable Improvements for lz-git.conflict

### High Priority (Implement First)

1. **Conflict Difficulty Estimator**
   - Calculate complexity score using: lines of code, cyclomatic complexity, number of locations
   - Display before resolution: "Low/Medium/High complexity conflict"
   - Help users decide whether to resolve now or defer

2. **Automatic Expert Recommendation**
   - Use `git blame` on conflicting lines
   - Identify developers with most commits in conflict areas
   - Suggest: "Consider asking @username (15 commits in this area)"

3. **Enhanced Context Display**
   - Show commit messages for conflicting changes
   - Display "ours" vs "theirs" with author and timestamp
   - Link to related PRs or issues if available

4. **Test-Based Validation**
   - After resolution, automatically run tests on affected files/modules
   - Report: "✓ 15 tests passed" or "✗ 3 tests failed"
   - Integrate with CI tools (GitHub Actions, Jenkins)

### Medium Priority

5. **Proactive Conflict Detection**
   - Warn before merge if conflicts likely (branch divergence analysis)
   - Suggest: "Changes in feature-branch conflict with main in file.ts"

6. **Resolution Confidence Score**
   - After resolution, analyze semantic correctness
   - Check for common mistakes: duplicate code, missing branches, syntax errors
   - Display confidence: "90% confidence - looks good" or "50% confidence - review carefully"

7. **Backup Branch Creation**
   - Automatically create backup before resolution: `lz-git.conflict/resolve/<branch>/backup-<timestamp>`
   - Allow easy rollback if resolution fails

8. **History Exploration Tool**
   - Command to show evolution of conflicting code: `lz-git conflict history`
   - Display related commits, refactorings, bug fixes
   - Help developers understand "why this code exists"

### Low Priority (Future Enhancements)

9. **Interactive Tutorial**
   - Guided walkthrough for first-time users
   - Explain conflict markers, resolution strategies
   - Based on finding that less experienced developers fail more often

10. **Collaboration Features**
    - Integrate with chat tools (Slack, Teams)
    - Notify suggested experts about conflicts
    - Allow real-time collaboration on resolution

---

## Warnings and Anti-Patterns to Avoid

### Critical Findings from Paper

1. **Deferral Can Cascade**
   - **Finding**: Deferring increases complexity (E2 - 19.57% reported increased complexity)
   - **Impact**: Can require "Stop the Presses" (E1 - 32.61%) - halt all development
   - **Warning**: Don't encourage deferral without clear ownership/timeline
   - **Plugin Action**: Warn users if conflict has been deferred >3 days

2. **The Nuclear Option**
   - **Finding**: 18.67% use "redo changes" backup strategy
   - **Impact**: Developers throw away work and manually reimplement
   - **Warning**: This indicates failure of tools to support complex conflicts
   - **Plugin Action**: Provide better tools before users resort to this

3. **Tool Mistrust**
   - **Finding**: 42.15% experience some toolset mistrust
   - **Impact**: Developers manually verify or avoid tools entirely
   - **Warning**: Opaque tool behavior reduces trust
   - **Plugin Action**: Always explain WHY a resolution is suggested, show confidence level

4. **Context Switching Overhead**
   - **Finding**: Developers use average 2.5 tools (up to 7) to resolve conflicts
   - **Impact**: Mental fatigue, reduced performance
   - **Warning**: Avoid requiring external tools or manual steps
   - **Plugin Action**: Integrate everything within IDE/terminal workflow

5. **Complexity > Size**
   - **Finding**: Complexity impacts difficulty MORE than size (0.930 vs 0.496 difference in tool effectiveness)
   - **Impact**: Tools focus on wrong dimension
   - **Warning**: Don't just count lines of conflict
   - **Plugin Action**: Prioritize semantic complexity analysis over LOC counts

6. **Visual Inspection Unreliable**
   - **Finding**: 74.16% use "code looks correct" but complexity is #1 difficulty factor
   - **Impact**: High cognitive load, potential for errors
   - **Warning**: Developers trust their eyes even for complex code
   - **Plugin Action**: Provide automated semantic checks, don't rely on human review alone

### Specific Anti-Patterns to Avoid in Plugin

| Anti-Pattern | Why It Fails | Better Approach |
|--------------|--------------|-----------------|
| **Automatic resolution without explanation** | Reduces trust, developers don't understand what changed | Always show diff, explain strategy used |
| **Binary success/failure feedback** | Doesn't help developers improve | Provide detailed feedback: "Resolved 3/4 conflicts, 1 needs manual review" |
| **Hiding conflict markers** | Removes important context | Show markers but enhance with metadata (author, date, context) |
| **One-size-fits-all strategy** | Different conflicts need different approaches | Offer multiple strategies (ours/theirs/manual/semantic) |
| **No backup mechanism** | Developers fear destructive changes | Always create backup branch, allow easy rollback |
| **Requiring external tools** | Context switching reduces effectiveness | Integrate within git workflow, avoid external dependencies |
| **Ignoring code ownership** | Forces wrong person to resolve | Suggest expert developers, provide contact information |
| **Text-only analysis** | Misses semantic conflicts | Use AST parsing, type checking, semantic analysis |

---

## Relevance Score for lz-git.conflict Plugin

**Overall Relevance: 9.5/10** - Extremely High

### Breakdown by Plugin Feature

| Plugin Feature | Relevance | Supporting Evidence from Paper |
|----------------|-----------|-------------------------------|
| **resolve command** | 10/10 | Core resolution phase (Section 6.2); 78.7% fail on first attempt, need better support |
| **ours/theirs commands** | 8/10 | Simple conflicts benefit from quick resolution (U1 32.91% examine merge first) |
| **abort command** | 9/10 | Backup strategies (B1 25.33% "take offline"); deferral common (56.18%) |
| **status command** | 10/10 | Awareness phase (Section 5); 29.41% don't monitor, need visibility |
| **conflict-resolver agent** | 9/10 | Complexity assessment (F1 3.52/5); expert recommendation (N2 3.72/5) |

### Why This Paper is Essential

1. **Only comprehensive study of developer processes**: 264 developers surveyed across awareness/planning/resolution/evaluation
2. **Quantifies real pain points**: Mistrust (42.15%), deferral (56.18%), failure rate (78.7%)
3. **Identifies tool gaps**: Developers want better usability (I1 3.43/5), filtering (I2 3.41/5), history exploration (I3 3.30/5)
4. **Provides actionable metrics**: Complexity > size for difficulty; expertise is top-2 factor
5. **Validates automated approaches**: 75.28% already use test-based validation; expert recommendation is desired

### Direct Applications to Plugin

- **Implement difficulty estimator** based on complexity (F1) + locations (D2) + ownership (D3)
- **Add expert recommendation** based on git blame (addresses N2 - expertise need)
- **Show commit context** for conflicting changes (addresses N3 - information need)
- **Provide multiple strategies** for backup (try again, collaborate, take offline)
- **Create automatic backups** to reduce fear of destructive changes
- **Integrate test running** post-resolution to validate (C1 75.28%)
- **Display confidence score** to address tool mistrust (42.15%)

---

## Implementation Roadmap

### Phase 1: Core Enhancements (Weeks 1-4)
- [ ] Complexity estimator (lines, locations, ownership)
- [ ] Expert recommendation via git blame
- [ ] Enhanced context display (commit messages, authors, dates)
- [ ] Automatic backup branch creation

### Phase 2: Validation & Trust (Weeks 5-8)
- [ ] Test-based validation integration
- [ ] Confidence score calculation
- [ ] Detailed feedback messages
- [ ] Resolution explanation (why this strategy was chosen)

### Phase 3: Proactive Features (Weeks 9-12)
- [ ] Proactive conflict detection (branch divergence)
- [ ] History exploration command
- [ ] Deferral tracking & warnings
- [ ] Alternative strategy suggestions

### Phase 4: Collaboration (Future)
- [ ] Expert notification system
- [ ] Interactive tutorial
- [ ] Integration with chat tools
- [ ] Real-time collaboration support

---

## Conclusion

This paper is **foundational** for the lz-git.conflict plugin. It provides:

1. **Clear understanding** of the 4-phase conflict life-cycle
2. **Quantified metrics** for difficulty factors and developer needs
3. **Validated strategies** that developers already use (and want improved)
4. **Specific warnings** about anti-patterns (deferral cascade, nuclear option, tool mistrust)
5. **Actionable improvements** with priority rankings

The key insight: **Developers struggle most with complexity and context, not just mechanics**. Automated tools should focus on:
- Making complexity visible (estimators, confidence scores)
- Providing context (commit history, expert recommendations, semantic analysis)
- Building trust (explanations, backups, detailed feedback)
- Reducing cognitive load (integrated workflow, smart defaults, guided resolution)

By implementing the high-priority improvements, the plugin can address the top unmet needs identified in this comprehensive empirical study.
