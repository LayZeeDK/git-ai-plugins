# Attributions

This plugin's design incorporates insights from academic research and industry resources
on Git merge conflict resolution.

## Academic Research

### Zhang et al. (ISSTA 2022)
**Using Pre-trained Language Models to Resolve Textual and Semantic Merge Conflicts**

- DOI: [10.1145/3533767.3534396](https://doi.org/10.1145/3533767.3534396)
- Authors: Jialu Zhang, Todd Mytkowicz, Mike Kaufman, Ruzica Piskac, Shuvendu K. Lahiri
- Contribution: Classification of textual vs semantic conflicts, LLM-based resolution approaches,
  real-world conflict patterns from Microsoft Edge

### Ghiotto et al. (IEEE TSE 2018)
**On the Nature of Merge Conflicts: a Study of 2,731 Open Source Java Projects Hosted by GitHub**

- DOI: [10.1109/TSE.2018.2871083](https://doi.org/10.1109/TSE.2018.2871083)
- Authors: Gleiph Ghiotto, Leonardo Murta, Marcio Barros, Andre van der Hoek
- Contribution: Large-scale empirical study of conflict patterns, resolution strategies (V1, V2, CC, CB, NC, NN),
  statistical analysis of 175,805 conflicting chunks

## Online Resources

### Martin Fowler - Semantic Conflict
- URL: [martinfowler.com/bliki/SemanticConflict.html](https://martinfowler.com/bliki/SemanticConflict.html)
- Contribution: Clear definition and examples of semantic conflicts

### Git Documentation
- [merge-strategies](https://git-scm.com/docs/merge-strategies) - Git merge algorithm documentation
- [merge-config](https://git-scm.com/docs/merge-config) - Conflict style configuration options

## Inspiration

The conflict type taxonomy and resolution strategies in this plugin draw from the research above,
adapted for practical use in AI-assisted conflict resolution workflows.
