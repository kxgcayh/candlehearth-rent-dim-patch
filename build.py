#!/usr/bin/env python3
"""Audit pinned inputs; --write cross-builds and stages loose files inside this repo."""
from pathlib import Path
import argparse
import hashlib
import os
import shutil
import subprocess
from verify_binary import verify

HERE = Path(__file__).resolve().parent


def check_inputs():
    for line in (HERE / "inputs.sha256").read_text().splitlines():
        expected, name = line.split(None, 1)
        path = HERE / "inputs" / name.strip()
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise SystemExit(f"Input absent or hash mismatch: {path}; see BUILDING.md")
    print("PASS: pinned Candlehearth 1.1.1 inputs")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--toolchain", default=os.environ.get("CMAKE_TOOLCHAIN_FILE"))
    parser.add_argument("--commonlib-prefix", default=os.environ.get("COMMONLIB_PREFIX"))
    parser.add_argument("--deps-prefix", default=os.environ.get("DEPS_PREFIX"))
    args = parser.parse_args()
    check_inputs()
    if not args.write:
        print("DRY RUN: would build CandlehearthRentDim.dll for AE 1.7.104; no game files touched")
        return
    if not all((args.toolchain, args.commonlib_prefix, args.deps_prefix)):
        parser.error("--write requires --toolchain, --commonlib-prefix and --deps-prefix (or documented env vars)")
    subprocess.run(["cmake", "-S", str(HERE), "-B", str(HERE / "build/native"), "-G", "Ninja",
                    "-DCMAKE_BUILD_TYPE=Release", f"-DCMAKE_TOOLCHAIN_FILE={args.toolchain}",
                    f"-DCMAKE_PREFIX_PATH={args.commonlib_prefix};{args.deps_prefix}"], check=True)
    subprocess.run(["cmake", "--build", str(HERE / "build/native"), "-j1"], check=True)
    dll = HERE / "build/native/CandlehearthRentDim.dll"
    verify(dll)
    stage = HERE / "dist/Candlehearth Rent Dim Patch"
    target = stage / "SKSE/Plugins"
    target.mkdir(parents=True, exist_ok=True)
    shutil.copy2(dll, target / dll.name)
    for name in ("LICENSE", "COPYING", "THIRD-PARTY-NOTICES.txt", "README.md"):
        shutil.copy2(HERE / name, stage / name)
    print(f"Staged loose files: {stage}. No archive, install or upload performed.")


if __name__ == "__main__":
    main()
