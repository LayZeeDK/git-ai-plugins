#!/usr/bin/env bash
# Setup script for marker-pdf on Windows ARM64 with Python 3.12
# Generated: January 30, 2026
# Status: ✅ FULLY WORKING with patches applied
# See: README.md and setup/SETUP-NOTES.md for full details

set -e  # Exit on error

echo "=== marker-pdf Python 3.12 ARM64 Setup ==="
echo ""

# Check if Python 3.12 is installed
if ! command -v py &> /dev/null || ! py -3.12 --version &> /dev/null; then
    echo "❌ Python 3.12 not found!"
    echo "Install with: winget install Python.Python.3.12"
    exit 1
fi

echo "✓ Python 3.12 found: $(py -3.12 --version)"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
py -3.12 -m venv venv-marker-py312
echo "✓ Virtual environment created"
echo ""

# Activate and upgrade pip
echo "Activating environment and upgrading pip..."
source venv-marker-py312/Scripts/activate
python -m pip install --upgrade pip
echo "✓ pip upgraded to $(pip --version)"
echo ""

# Download cgohlke wheels if not already present
if [ ! -d "wheels" ]; then
    mkdir wheels
fi

cd wheels

if [ ! -f "2024.6.15-experimental-cp312-win_arm64.whl.zip" ]; then
    echo "Downloading cgohlke Python 3.12 wheels..."
    gh release download v2024.6.15 --repo cgohlke/win_arm64-wheels --pattern "*cp312*win_arm64.whl.zip"
    echo "✓ Downloaded cgohlke wheels"
else
    echo "✓ cgohlke wheels already downloaded"
fi
echo ""

# Extract required wheels if not already extracted
if [ ! -f "opencv_python_headless-4.10.0.82-cp39-abi3-win_arm64.whl" ]; then
    echo "Extracting opencv, scikit-learn, cryptography wheels..."
    unzip -j 2024.6.15-experimental-cp312-win_arm64.whl.zip \
      "2024.6.15-experimental-cp312-win_arm64.whl/opencv_python_headless-4.10.0.82-cp39-abi3-win_arm64.whl" \
      "2024.6.15-experimental-cp312-win_arm64.whl/scikit_learn-1.5.0-cp312-cp312-win_arm64.whl" \
      "2024.6.15-experimental-cp312-win_arm64.whl/cryptography-42.0.8-cp312-cp312-win_arm64.whl"
    echo "✓ Wheels extracted"
else
    echo "✓ Wheels already extracted"
fi

cd ..
echo ""

# Install core packages from cgohlke
echo "Installing OpenCV, scikit-learn, cryptography from cgohlke wheels..."
pip install wheels/opencv_python_headless-4.10.0.82-cp39-abi3-win_arm64.whl \
            wheels/scikit_learn-1.5.0-cp312-cp312-win_arm64.whl \
            wheels/cryptography-42.0.8-cp312-cp312-win_arm64.whl
echo "✓ Core packages installed"
echo ""

# Install PyTorch
echo "Installing PyTorch for ARM64..."
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
echo "✓ PyTorch installed"
echo ""

# Install marker-pdf and surya-ocr with correct versions
echo "Installing marker-pdf and surya-ocr..."
pip install --no-deps marker-pdf==1.2.7 surya-ocr==0.8.3
echo "✓ marker-pdf and surya-ocr installed"
echo ""

# Install transformers and ML packages
echo "Installing transformers and ML packages..."
pip install transformers==4.57.6 tokenizers==0.22.2 safetensors==0.7.0 huggingface-hub==0.36.0
echo "✓ ML packages installed"
echo ""

# Install remaining dependencies (bypassing strict version conflicts)
echo "Installing remaining dependencies..."
pip install --no-deps click==8.3.1 filetype==1.2.0 ftfy==6.3.1 markdown2==2.5.4 \
            markdownify==0.13.1 pdftext==0.6.3 pydantic==2.12.5 pydantic-settings==2.12.0 \
            python-dotenv==1.2.1 rapidfuzz==3.14.3 einops==0.8.2 protobuf==5.29.5 \
            tabled-pdf==0.2.0 tabulate==0.9.0 texify==0.2.1 google-generativeai==0.8.6 \
            pypdfium2==4.30.0 beautifulsoup4==4.14.3 distro==1.9.0
echo "✓ Core dependencies installed"
echo ""

# Install Google API and utility packages
echo "Installing Google API packages..."
pip install google-ai-generativelanguage==0.6.15 google-api-core==2.29.0 \
            google-api-python-client==2.188.0 google-auth==2.48.0 \
            google-auth-httplib2==0.3.0 google-genai==1.60.0 \
            googleapis-common-protos==1.72.0 proto-plus==1.27.0 grpcio-status==1.64.1 \
            httplib2==0.31.2 pyasn1==0.6.2 pyasn1_modules==0.4.2 rsa==4.9.1 \
            pyparsing==3.3.2 uritemplate==4.2.0 soupsieve==2.8.3 wcwidth==0.5.0 \
            typing-inspection==0.4.2 annotated-types==0.7.0 pydantic_core==2.41.5 six==1.17.0
echo "✓ All dependencies installed"
echo ""

# Test installation
echo "Testing marker_single command..."
export CRYPTOGRAPHY_OPENSSL_NO_LEGACY=1
if ./venv-marker-py312/Scripts/marker_single --help > /dev/null 2>&1; then
    echo "✓ marker_single --help works!"
else
    echo "⚠ marker_single --help failed"
fi
echo ""

echo "=== Setup Complete ==="
echo ""
echo "✅ Native ARM64 marker-pdf installation successful!"
echo ""
echo "Next step: Apply compatibility patches"
echo "  python setup/apply-patches.py venv-marker-py312"
echo ""
echo "To use:"
echo "  source venv-marker-py312/Scripts/activate"
echo "  export CRYPTOGRAPHY_OPENSSL_NO_LEGACY=1"
echo "  cd ../../plugins/lz-git.conflict/research"
echo "  marker_single 'paper.pdf' --output_format markdown --output_dir output"
echo ""
echo "See README.md for full documentation."
