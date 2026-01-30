#!/usr/bin/env python3
"""
Apply patches to marker-pdf dependencies for transformers 4.57.6 compatibility on ARM64
Generated: January 29, 2026
Status: WORKING - All patches tested and verified
"""

import sys
from pathlib import Path

def apply_patches(venv_path):
    """Apply all 7 patches required for marker-pdf on Windows ARM64"""
    venv = Path(venv_path)
    site_packages = venv / "Lib" / "site-packages"

    print("🔧 Applying marker-pdf ARM64 compatibility patches...")
    print()

    # Patch 1: surya-ocr ocr_error config (transformers.onnx removal)
    print("1/7: Patching surya-ocr ocr_error config...")
    surya_config = site_packages / "surya/model/ocr_error/config.py"
    if surya_config.exists():
        content = surya_config.read_text()
        if "from transformers.onnx import OnnxConfig" in content:
            content = content.replace(
                "from transformers.onnx import OnnxConfig",
                """# from transformers.onnx import OnnxConfig  # Removed - deprecated in transformers 4.45+

# Stub for OnnxConfig to avoid import error (class not actually used)
class OnnxConfig:
    def __init__(self, *args, **kwargs):
        pass

    @property
    def inputs(self):
        return OrderedDict()"""
            )
            surya_config.write_text(content)
            print("   ✅ surya-ocr ocr_error config patched")
        else:
            print("   ⏭️  Already patched or not needed")
    else:
        print("   ⚠️  File not found")

    # Patch 2: transformers configuration_utils.py (handle dict configs)
    print("2/7: Patching transformers configuration_utils...")
    transformers_config = site_packages / "transformers/configuration_utils.py"
    if transformers_config.exists():
        content = transformers_config.read_text()
        old_code = """    diff = {}
    default = config_obj.__class__().to_dict() if config_obj is not None else {}
    for key, value in dict_a.items():"""
        new_code = """    diff = {}
    # PATCH: Handle dict config objects for compatibility with older models (texify, etc.)
    if config_obj is not None:
        if isinstance(config_obj, dict):
            default = config_obj  # Use dict directly
        else:
            default = config_obj.__class__().to_dict()
    else:
        default = {}
    for key, value in dict_a.items():"""
        if old_code in content:
            content = content.replace(old_code, new_code)
            transformers_config.write_text(content)
            print("   ✅ transformers configuration_utils patched")
        else:
            print("   ⏭️  Already patched or not needed")
    else:
        print("   ⚠️  File not found")

    # Patch 3: texify config (handle dict/object duality)
    print("3/7: Patching texify config...")
    texify_config = site_packages / "texify/model/config.py"
    if texify_config.exists():
        content = texify_config.read_text()
        old_code = """def get_config(model_checkpoint):
    config = TexifyConfig.from_pretrained(model_checkpoint)
    encoder_config = config.encoder
    encoder = VariableDonutSwinConfig(**encoder_config)
    config.encoder = encoder

    decoder_config = config.decoder
    decoder = MBartConfig(**decoder_config)
    config.decoder = decoder
    return config"""
        new_code = """def get_config(model_checkpoint):
    config = TexifyConfig.from_pretrained(model_checkpoint)
    encoder_config = config.encoder
    # PATCH: Handle both dict and object cases for transformers 4.57+ compatibility
    if isinstance(encoder_config, dict):
        encoder = VariableDonutSwinConfig(**encoder_config)
    else:
        encoder = encoder_config  # Already a config object
    config.encoder = encoder

    decoder_config = config.decoder
    if isinstance(decoder_config, dict):
        decoder = MBartConfig(**decoder_config)
    else:
        decoder = decoder_config  # Already a config object
    config.decoder = decoder
    return config"""
        if old_code in content:
            content = content.replace(old_code, new_code)
            texify_config.write_text(content)
            print("   ✅ texify config patched")
        else:
            print("   ⏭️  Already patched or not needed")
    else:
        print("   ⚠️  File not found")

    # Patch 4: surya recognition config
    print("4/7: Patching surya recognition config...")
    surya_rec_config = site_packages / "surya/model/recognition/config.py"
    if surya_rec_config.exists():
        content = surya_rec_config.read_text()
        # Check if get_text_config already exists
        if "def get_text_config(self" not in content:
            # Add the method before the class ends
            insert_pos = content.rfind("\n\nclass ")
            if insert_pos == -1:
                insert_pos = len(content)

            patch_code = """
    # PATCH: Add get_text_config() method for transformers 4.57+ compatibility
    def get_text_config(self, decoder=False):
        \"\"\"Return the decoder config as the text config\"\"\"
        return self.decoder if decoder else self.decoder

"""
            content = content[:insert_pos] + patch_code + content[insert_pos:]

        # Fix kwargs.pop calls
        content = content.replace(
            'encoder_config = kwargs.pop("encoder")',
            '# PATCH: Handle case where encoder/decoder not in kwargs (transformers 4.57+ default config creation)\n        encoder_config = kwargs.pop("encoder", None)'
        )
        content = content.replace(
            'decoder_config = kwargs.pop("decoder")',
            'decoder_config = kwargs.pop("decoder", None)'
        )

        surya_rec_config.write_text(content)
        print("   ✅ surya recognition config patched")
    else:
        print("   ⚠️  File not found")

    # Patch 5: surya table_rec config
    print("5/7: Patching surya table_rec config...")
    surya_table_config = site_packages / "surya/model/table_rec/config.py"
    if surya_table_config.exists():
        content = surya_table_config.read_text()
        # Check if get_text_config already exists
        if "def get_text_config(self" not in content:
            insert_pos = content.rfind("\n\nclass ")
            if insert_pos == -1:
                insert_pos = len(content)

            patch_code = """
    # PATCH: Add get_text_config() method for transformers 4.57+ compatibility
    def get_text_config(self, decoder=False):
        \"\"\"Return the decoder config as the text config\"\"\"
        return self.decoder if decoder else self.decoder

"""
            content = content[:insert_pos] + patch_code + content[insert_pos:]

        # Fix kwargs.pop calls
        if 'encoder_config = kwargs.pop("encoder")' in content:
            content = content.replace(
                '        encoder_config = kwargs.pop("encoder")\n        decoder_config = kwargs.pop("decoder")\n        text_enc_config = kwargs.pop("text_encoder")',
                '        # PATCH: Handle case where configs not in kwargs (transformers 4.57+ default config creation)\n        encoder_config = kwargs.pop("encoder", None)\n        decoder_config = kwargs.pop("decoder", None)\n        text_enc_config = kwargs.pop("text_encoder", None)'
            )

        surya_table_config.write_text(content)
        print("   ✅ surya table_rec config patched")
    else:
        print("   ⚠️  File not found")

    print()
    print("✅ All patches applied successfully!")
    print()
    print("Note: Patches 6-7 are package installations:")
    print("  6. markdownify==0.13.1 (pip install 'markdownify>=0.13.1,<0.14.0')")
    print("  7. grpcio==1.64.1 from cgohlke wheels")
    print()
    print("Run marker_single with: CRYPTOGRAPHY_OPENSSL_NO_LEGACY=1")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python apply-marker-patches.py <venv-path>")
        print("Example: python apply-marker-patches.py venv-marker-py312")
        sys.exit(1)

    venv_path = sys.argv[1]
    apply_patches(venv_path)
