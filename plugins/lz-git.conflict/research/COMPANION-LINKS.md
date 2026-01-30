# Companion Links

Code repositories and datasets associated with research papers.

## Paper Companions

| Repository | Related Paper | Contents |
|------------|---------------|----------|
| [gems-uff/merge-nature](https://github.com/gems-uff/merge-nature) | On the Nature of Merge Conflicts (2018) | Datasets from 2,731 Java projects, interactive visualization at merge-nature.netlify.app |
| [shikham-8/CS230-TIM-Improves-Merging](https://github.com/shikham-8/CS230-TIM-Improves-Merging) | Semantic Merge Conflict Detection (TIM Report) | TIM tool Python implementation (detect.py, api.py, parse.py), symbolic execution with CrossHair |
| [sealuzh/tools-changedistiller](https://bitbucket.org/sealuzh/tools-changedistiller) | ChangeDistiller (2007) and Retrospective (2025) | Original ChangeDistiller Java implementation for AST-based tree differencing |

## Standalone Tools

| Repository | Description | Contents |
|------------|-------------|----------|
| [johanvanl/SemDiff](https://github.com/johanvanl/SemDiff) | Java semantic differencing tool | Eclipse JDT-based implementation for language-aware code comparison. Often referenced in merge conflict research. |

Note: The SemDiff tool repository is **unrelated** to the SemDiff paper (2308.01463v1.pdf) which covers binary similarity detection.

## Local Clones

These repositories are cloned to `research/repos/` for analysis (git-ignored):

```
research/repos/
├── merge-nature/
├── CS230-TIM-Improves-Merging/
├── SemDiff/
└── tools-changedistiller/
```

## Analysis Files

| Repository | Analysis Document |
|------------|-------------------|
| merge-nature | [nature-2018.md](analysis/nature-2018.md) |
| CS230-TIM-Improves-Merging | [semantic-detection-2023.md](analysis/semantic-detection-2023.md) |
| tools-changedistiller | [changedistiller-2007.md](analysis/changedistiller-2007.md), [changedistiller-retrospective-2025.md](analysis/changedistiller-retrospective-2025.md) |
| SemDiff | [semdiff-tool.md](analysis/semdiff-tool.md) |
