# Batch convert all research PDFs to Markdown using native ARM64 marker-pdf
# Generated: January 29, 2026
# Requires: Python 3.12 venv with all patches applied

$ErrorActionPreference = "Stop"

# Set required environment variable
$env:CRYPTOGRAPHY_OPENSSL_NO_LEGACY = "1"

# Configuration
$VENV = "..\..\tools\marker-pdf\venv-marker-py312"
$OUTPUT_DIR = "papers-markdown"
$MARKER_CMD = "$VENV\Scripts\marker_single.exe"

Write-Host "=== marker-pdf Batch PDF Conversion ===" -ForegroundColor Cyan
Write-Host ""

# Create output directory
if (-not (Test-Path $OUTPUT_DIR)) {
    New-Item -ItemType Directory -Path $OUTPUT_DIR | Out-Null
    Write-Host "✓ Created output directory: $OUTPUT_DIR" -ForegroundColor Green
}

# Find all PDFs in research directory (excluding subdirectories)
$pdfs = Get-ChildItem -Path "." -Filter "*.pdf" -File
$total = $pdfs.Count

if ($total -eq 0) {
    Write-Host "❌ No PDF files found in current directory" -ForegroundColor Red
    exit 1
}

Write-Host "Found $total PDF files to convert" -ForegroundColor Yellow
Write-Host ""

# Process each PDF
$successful = 0
$failed = 0
$startTime = Get-Date

foreach ($pdf in $pdfs) {
    $num = $successful + $failed + 1
    $name = $pdf.Name

    Write-Host "[$num/$total] Converting: $name" -ForegroundColor Cyan

    try {
        # Run marker_single
        $output = & $MARKER_CMD $pdf.FullName --output_format markdown --output_dir $OUTPUT_DIR 2>&1

        if ($LASTEXITCODE -eq 0) {
            # Extract time from output
            $timeLine = $output | Select-String "Total time:" | Select-Object -Last 1
            if ($timeLine) {
                $time = $timeLine -replace ".*Total time: ", ""
                Write-Host "  ✅ Success in $time seconds" -ForegroundColor Green
            } else {
                Write-Host "  ✅ Success" -ForegroundColor Green
            }
            $successful++
        } else {
            Write-Host "  ❌ Failed (exit code: $LASTEXITCODE)" -ForegroundColor Red
            Write-Host "  Error: $($output | Select-String "Error|Exception" | Select-Object -Last 1)" -ForegroundColor Red
            $failed++
        }
    } catch {
        Write-Host "  ❌ Failed: $_" -ForegroundColor Red
        $failed++
    }

    Write-Host ""
}

# Summary
$endTime = Get-Date
$duration = ($endTime - $startTime).TotalSeconds

Write-Host "=== Conversion Complete ===" -ForegroundColor Cyan
Write-Host "Successful: $successful/$total" -ForegroundColor Green
Write-Host "Failed: $failed/$total" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Green" })
Write-Host "Total time: $([math]::Round($duration, 2)) seconds" -ForegroundColor Yellow
Write-Host ""
Write-Host "Output directory: $OUTPUT_DIR" -ForegroundColor Cyan
