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
