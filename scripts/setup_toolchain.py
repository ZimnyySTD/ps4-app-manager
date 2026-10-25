#!/usr/bin/env python3
import os
import sys
import subprocess
import tarfile
import glob

OO_ROOT = "/tmp/oo_root"

def setup():
    if os.path.exists(f"{OO_ROOT}/usr/lib/llvm-10/bin/lld") and os.path.exists(f"{OO_ROOT}/usr/lib/OpenOrbisSDK"):
        print("Toolchain already properly present at", OO_ROOT)
    else:
        print("Extracting OpenOrbis toolchain from Docker image...")
        os.makedirs("/tmp/openorbis_tar", exist_ok=True)
        os.makedirs(OO_ROOT, exist_ok=True)

        p = subprocess.Popen(['docker', 'image', 'save', 'openorbisofficial/toolchain:latest'], stdout=subprocess.PIPE)
        with tarfile.open(fileobj=p.stdout, mode='r|*') as tf:
            tf.extractall(path='/tmp/openorbis_tar')

        for blob in glob.glob('/tmp/openorbis_tar/blobs/sha256/*'):
            try:
                with tarfile.open(blob, 'r') as tar:
                    names = tar.getnames()
                    if any('OpenOrbisSDK' in n or 'llvm-10' in n or 'libssl' in n or 'libcrypto' in n for n in names):
                        print(f"Extracting layer {os.path.basename(blob)}...")
                        tar.extractall(OO_ROOT)
            except Exception:
                pass

    # Patch make_fself.py for Python 3
    fself_path = f"{OO_ROOT}/usr/lib/OpenOrbisSDK/scripts/make_fself.py"
    if os.path.exists(fself_path):
        with open(fself_path, 'r', encoding='latin1') as f:
            code = f.read()

        code = code.replace("xrange(", "range(")
        code = code.replace("MAGIC = 'SCE\\0'", "MAGIC = b'SCE\\0'")
        code = code.replace("MAGIC = '\\x7FELF'", "MAGIC = b'\\x7FELF'")
        code = code.replace("MAGIC = '\\x4F\\x15\\x3D\\x1D'", "MAGIC = b'\\x4F\\x15\\x3D\\x1D'")
        code = code.replace("expected_magic = '\\x7FELF'", "expected_magic = b'\\x7FELF'")
        code = code.replace("self.magic = SignedElfFile.MAGIC", "self.magic = b'\\x4F\\x15\\x3D\\x1D'")
        code = code.replace("self.npdrm_control_block.content_id = '\\0' * SELF_NPDRM_CONTROL_BLOCK_CONTENT_ID_SIZE", "self.npdrm_control_block.content_id = b'\\0' * SELF_NPDRM_CONTROL_BLOCK_CONTENT_ID_SIZE")
        code = code.replace("self.npdrm_control_block.random_pad = '\\0' * SELF_NPDRM_CONTROL_BLOCK_RANDOM_PAD_SIZE", "self.npdrm_control_block.random_pad = b'\\0' * SELF_NPDRM_CONTROL_BLOCK_RANDOM_PAD_SIZE")
        code = code.replace("self.signature = '\\0' * SELF_SIGNATURE_SIZE", "self.signature = b'\\0' * SIGNATURE_SIZE")
        code = code.replace("self.signature = '\\0' * SIGNATURE_SIZE", "self.signature = b'\\0' * SIGNATURE_SIZE")
        code = code.replace("f.write(self.signature)", "f.write(self.signature if isinstance(self.signature, bytes) else self.signature.encode('latin1'))")
        code = code.replace("f.write(entry.data)", "f.write(entry.data if isinstance(entry.data, bytes) else entry.data.encode('latin1'))")
        code = code.replace("f.write(self.version_data)", "f.write(self.version_data if isinstance(self.version_data, bytes) else self.version_data.encode('latin1'))")

        with open(fself_path, 'w', encoding='utf-8') as f:
            f.write(code)

    os.makedirs('/tmp/ssl1.1', exist_ok=True)
    subprocess.run(f"cp -f {OO_ROOT}/usr/lib/x86_64-linux-gnu/libssl.so* /tmp/ssl1.1/ 2>/dev/null", shell=True)
    subprocess.run(f"cp -f {OO_ROOT}/usr/lib/x86_64-linux-gnu/libcrypto.so* /tmp/ssl1.1/ 2>/dev/null", shell=True)

    print("Toolchain setup complete.")

if __name__ == "__main__":
    setup()
