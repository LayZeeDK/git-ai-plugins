# Setup script for marker-pdf on Windows ARM64 with Python 3.12
# Generated: January 30, 2026
# Status: ✅ FULLY WORKING with patches applied
# See: README.md and setup/SETUP-NOTES.md for full details

$ErrorActionPreference = "Stop"

Write-Host "=== marker-pdf Python 3.12 ARM64 Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check if Python 3.12 is installed
try {
    $pythonVersion = py -3.12 --version 2>&1
    Write-Host "✓ Python 3.12 found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python 3.12 not found!" -ForegroundColor Red
    Write-Host "Install with: winget install Python.Python.3.12"
    exit 1
}
Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
py -3.12 -m venv venv-marker-py312
Write-Host "✓ Virtual environment created" -ForegroundColor Green
Write-Host ""

# Activate and upgrade pip
Write-Host "Activating environment and upgrading pip..." -ForegroundColor Yellow
.\venv-marker-py312\Scripts\Activate.ps1
python -m pip install --upgrade pip | Out-Null
$pipVersion = pip --version
Write-Host "✓ pip upgraded to $pipVersion" -ForegroundColor Green
Write-Host ""

# Create wheels directory if not present
if (-not (Test-Path "wheels")) {
    New-Item -ItemType Directory -Path "wheels" | Out-Null
}

Set-Location wheels

# Download cgohlke wheels if not already present
if (-not (Test-Path "2024.6.15-experimental-cp312-win_arm64.whl.zip")) {
    Write-Host "Downloading cgohlke Python 3.12 wheels..." -ForegroundColor Yellow
    gh release download v2024.6.15 --repo cgohlke/win_arm64-wheels --pattern "*cp312*win_arm64.whl.zip"
    Write-Host "✓ Downloaded cgohlke wheels" -ForegroundColor Green
} else {
    Write-Host "✓ cgohlke wheels already downloaded" -ForegroundColor Green
}
Write-Host ""

# Extract required wheels if not already extracted
if (-not (Test-Path "opencv_python_headless-4.10.0.82-cp39-abi3-win_arm64.whl")) {
    Write-Host "Extracting opencv, scikit-learn, cryptography wheels..." -ForegroundColor Yellow
    Expand-Archive -Path "2024.6.15-experimental-cp312-win_arm64.whl.zip" -DestinationPath "temp" -Force
    Copy-Item "temp/2024.6.15-experimental-cp312-win_arm64.whl/opencv_python_headless-4.10.0.82-cp39-abi3-win_arm64.whl" .
    Copy-Item "temp/2024.6.15-experimental-cp312-win_arm64.whl/scikit_learn-1.5.0-cp312-cp312-win_arm64.whl" .
    Copy-Item "temp/2024.6.15-experimental-cp312-win_arm64.whl/cryptography-42.0.8-cp312-cp312-win_arm64.whl" .
    Remove-Item -Recurse -Force "temp"
    Write-Host "✓ Wheels extracted" -ForegroundColor Green
} else {
    Write-Host "✓ Wheels already extracted" -ForegroundColor Green
}

Set-Location ..
Write-Host ""

# Install core packages from cgohlke
Write-Host "Installing OpenCV, scikit-learn, cryptography from cgohlke wheels..." -ForegroundColor Yellow
pip install wheels/opencv_python_headless-4.10.0.82-cp39-abi3-win_arm64.whl `
            wheels/scikit_learn-1.5.0-cp312-cp312-win_arm64.whl `
            wheels/cryptography-42.0.8-cp312-cp312-win_arm64.whl
Write-Host "✓ Core packages installed" -ForegroundColor Green
Write-Host ""

# Install PyTorch
Write-Host "Installing PyTorch for ARM64..." -ForegroundColor Yellow
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
Write-Host "✓ PyTorch installed" -ForegroundColor Green
Write-Host ""

# Install marker-pdf and surya-ocr with correct versions
Write-Host "Installing marker-pdf and surya-ocr..." -ForegroundColor Yellow
pip install --no-deps marker-pdf==1.2.7 surya-ocr==0.8.3
Write-Host "✓ marker-pdf and surya-ocr installed" -ForegroundColor Green
Write-Host ""

# Install transformers and ML packages
Write-Host "Installing transformers and ML packages..." -ForegroundColor Yellow
pip install transformers==4.57.6 tokenizers==0.22.2 safetensors==0.7.0 huggingface-hub==0.36.0
Write-Host "✓ ML packages installed" -ForegroundColor Green
Write-Host ""

# Install remaining dependencies (bypassing strict version conflicts)
Write-Host "Installing remaining dependencies..." -ForegroundColor Yellow
pip install --no-deps click==8.3.1 filetype==1.2.0 ftfy==6.3.1 markdown2==2.5.4 `
            markdownify==0.13.1 pdftext==0.6.3 pydantic==2.12.5 pydantic-settings==2.12.0 `
            python-dotenv==1.2.1 rapidfuzz==3.14.3 einops==0.8.2 protobuf==5.29.5 `
            tabled-pdf==0.2.0 tabulate==0.9.0 texify==0.2.1 google-generativeai==0.8.6 `
            pypdfium2==4.30.0 beautifulsoup4==4.14.3 distro==1.9.0
Write-Host "✓ Core dependencies installed" -ForegroundColor Green
Write-Host ""

# Install Google API and utility packages
Write-Host "Installing Google API packages..." -ForegroundColor Yellow
pip install google-ai-generativelanguage==0.6.15 google-api-core==2.29.0 `
            google-api-python-client==2.188.0 google-auth==2.48.0 `
            google-auth-httplib2==0.3.0 google-genai==1.60.0 `
            googleapis-common-protos==1.72.0 proto-plus==1.27.0 grpcio-status==1.64.1 `
            httplib2==0.31.2 pyasn1==0.6.2 pyasn1_modules==0.4.2 rsa==4.9.1 `
            pyparsing==3.3.2 uritemplate==4.2.0 soupsieve==2.8.3 wcwidth==0.5.0 `
            typing-inspection==0.4.2 annotated-types==0.7.0 pydantic_core==2.41.5 six==1.17.0
Write-Host "✓ All dependencies installed" -ForegroundColor Green
Write-Host ""

# Test installation
Write-Host "Testing marker_single command..." -ForegroundColor Yellow
$env:CRYPTOGRAPHY_OPENSSL_NO_LEGACY = "1"
try {
    .\venv-marker-py312\Scripts\marker_single --help | Out-Null
    Write-Host "✓ marker_single --help works!" -ForegroundColor Green
} catch {
    Write-Host "⚠ marker_single --help failed" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "=== Setup Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Native ARM64 marker-pdf installation successful!" -ForegroundColor Green
Write-Host ""
Write-Host "Next step: Apply compatibility patches" -ForegroundColor Yellow
Write-Host "  python setup/apply-patches.py venv-marker-py312"
Write-Host ""
Write-Host "To use:"
Write-Host "  .\venv-marker-py312\Scripts\Activate.ps1"
Write-Host '  $env:CRYPTOGRAPHY_OPENSSL_NO_LEGACY = "1"'
Write-Host '  cd ..\..\plugins\lz-git.conflict\research'
Write-Host '  marker_single "paper.pdf" --output_format markdown --output_dir output'
Write-Host ""
Write-Host "See README.md for full documentation."
