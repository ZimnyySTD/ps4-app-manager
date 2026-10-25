#!/usr/bin/env python3
import sys
import os
import struct

def validate_pkg(filepath):
    print(f"Validating PS4 PKG: {filepath}")

    if not os.path.exists(filepath):
        print(f"ERROR: PKG file does not exist: {filepath}")
        return False

    file_size = os.path.getsize(filepath)
    print(f"File size: {file_size} bytes")

    if file_size == 0:
        print("ERROR: PKG file is empty!")
        return False

    if file_size < 1024:
        print("ERROR: PKG file is smaller than minimum header size (1024 bytes).")
        return False

    with open(filepath, "rb") as f:
        magic = f.read(4)
        if magic != b"\x7fCNT":
            print(f"ERROR: Invalid PKG magic header. Expected b'\\x7fCNT', got {magic}")
            return False

        f.seek(0x010)
        entry_count, flags = struct.unpack(">II", f.read(8))

        f.seek(0x040)
        content_id = f.read(36).decode("utf-8", errors="ignore").rstrip("\x00")

    print("PKG Validation Passed successfully!")
    print(f"  - Magic: \\x7fCNT")
    print(f"  - Content ID: {content_id}")
    print(f"  - Entries: {entry_count}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate_pkg.py <path_to_pkg>")
        sys.exit(1)

    pkg_path = sys.argv[1]
    if not validate_pkg(pkg_path):
        sys.exit(1)
    sys.exit(0)
