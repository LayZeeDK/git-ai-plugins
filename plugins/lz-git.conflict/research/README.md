# Research Papers on Merge Conflicts

This directory contains academic papers and research on merge conflicts, merge conflict resolution, and related topics.

## Filename Format

PDFs are named using the following format:

```
Title (Year) by Last Names [original-filename].pdf
```

Where:
- **Title**: Full title of the paper
- **Year**: Year of publication (in parentheses)
- **Last Names**: Comma-separated list of author last names (to keep paths under Windows 260 char limit)
- **original-filename**: Original filename without extension (in square brackets)

### Example

```
Detecting semantic conflicts with unit tests (2024) by Da Silva, Borba, Maciel, Mahmood, Berger, Moisakis, Gomes, Leite [1-s2.0-S0164121224001158-main].pdf
```

## PDF Information Extraction Script

A Node.js script is available to extract title, authors, and year information from PDFs.

### Prerequisites

```bash
npm install --no-save pdf-parse
```

### Script: `extract-pdf-info.js`

```javascript
const fs = require('fs');
const { PDFParse } = require('pdf-parse');

const filename = process.argv[2];
if (!filename) {
  console.error('Usage: node extract-pdf-info.js <filename>');
  process.exit(1);
}

(async () => {
  try {
    const dataBuffer = fs.readFileSync(filename);
    const parser = new PDFParse({ data: dataBuffer });

    // Get text from first 2 pages only
    const result = await parser.getText({ pageLimit: 2 });

    // Extract first 2500 characters which should contain title, authors, and year
    const text = result.text.substring(0, 2500);
    console.log(text);
  } catch (error) {
    console.error('Error parsing PDF:', error.message);
    process.exit(1);
  }
})();
```

### Usage

```bash
# Extract title, authors, and year from a PDF
node extract-pdf-info.js "filename.pdf"

# The script will print the first ~2500 characters from the first 2 pages
# This typically includes the title, authors, abstract, and publication info
```

### Tips

1. **Large PDFs**: For very large PDFs (>100MB), the script may take longer to process
2. **Year Extraction**: Look for copyright notices, publication dates, or conference dates in the output
3. **ArXiv Papers**: ArXiv identifiers like `2105.07569` encode the year and month (e.g., `2105` = May 2021)
4. **Conference Papers**: Look for conference dates like "ASE '14" (2014) or "ISSTA 22" (2022)

### Common Year Patterns

- IEEE/ACM papers: Copyright line usually contains year (`© 2024 IEEE`)
- Journal papers: Volume and year in header (`Vol. 51, 2025`)
- ArXiv: Date in identifier (`2308.01463` = August 2023, format YYMM)
- Conference papers: Conference year in proceedings info (`ASE '14`, `ISSTA 22`)

## Research Topics Covered

This collection includes papers on:

- **Semantic Conflict Detection**: Detecting conflicts beyond textual/syntactic analysis
- **Automated Conflict Resolution**: Using ML/LLMs to automatically resolve merge conflicts
- **Merge Conflict Studies**: Empirical studies on the nature and lifecycle of merge conflicts
- **Source Code Differencing**: Tree-based and structural approaches to code comparison
- **Test-Based Conflict Detection**: Using automated test generation to detect semantic conflicts
- **Search-Based Resolution**: Optimization approaches to finding conflict resolutions

## Total Papers: 15

Papers span from 2007 to 2025, covering the evolution of merge conflict research over nearly two decades.
