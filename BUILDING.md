# Building

Python 3, CMake 3.21+, Ninja, clang-cl/lld-link, Windows SDK/CRT sysroot and a prebuilt CommonLibSSE-NG package with its dependency prefix are required. The build writes only inside this repository. No third-party mod content is tracked.

## Inputs

Put Candlehearth.esp and Candlehearth.bsa from [Candlehearth 1.1.1](https://www.nexusmods.com/skyrimspecialedition/mods/97542?tab=files) into inputs/. Installed archive name: Candlehearth - An Inn Overhaul-97542-1-1-1-1692799446.7z. Nexus file ID was not verified, so it is not guessed here. inputs.sha256 pins the exact inspected files; build.py refuses an absent or changed input. Native compilation does not embed these files.

Read-only source serialization was performed through the toolkit's spriggit-cli.sh wrapper with --GameRelease SkyrimSE --PackageName Spriggit.Yaml --PackageVersion 0.41.0 -u. The local CLI's development version is not its translation package version. There is no output ESP to deserialize or validate with xeditlib.

## Toolchain

The build used CommonLibSSE-NG commit 8eaddedd1542290701ccb0e9e88b2af8b3cea597 from the shared workspace tools/CommonLibSSE-NG/build-install package, plus the pre-existing Windows x64 dependencies. The local package and source layout must match; an arbitrary older library is unsupported. No recursive clone, submodule update or package installation is performed by build.py.

```sh
python3 build.py
python3 build.py --write \
  --toolchain /Volumes/S512/Windows/Build-Tools/winsdk/toolchain/clang-cl-msvc.cmake \
  --commonlib-prefix /Volumes/S512/Projects/ETC/skyrim-workspace/tools/CommonLibSSE-NG/build-install \
  --deps-prefix /Volumes/S512/Windows/Build-Tools/vcpkg/installed/x64-windows-cross
```

The paths are this machine's verified prefixes; pass your equivalent prefixes elsewhere. Environment alternatives: CMAKE_TOOLCHAIN_FILE, COMMONLIB_PREFIX, DEPS_PREFIX. The build is capped at one job. Original source remains in src/; output is build/native/CandlehearthRentDim.dll. The binary-verified loose install tree is dist/Candlehearth Rent Dim Patch/.

verify_binary.py independently reads the PE exports and SKSE metadata without loading the DLL. Cross-check with LLVM:

```sh
python3 verify_binary.py build/native/CandlehearthRentDim.dll
llvm-readobj --file-headers --coff-exports build/native/CandlehearthRentDim.dll
```

release.toml is prepared for the shared tools/mod-release/release.py workflow. Do not run packaging until the user chooses Nexus, GitHub or both; do not publish without explicit instruction. The source repository is private at https://github.com/kxgcayh/candlehearth-rent-dim-patch. No public release exists. There is no FOMOD because the candidate has a single installable DLL.

The build verifies architecture and metadata, not engine behavior. See README.md for the required in-game tests and NOTES.md for assumptions and limitations.

## Live harness

`python3 test/live_rent.py <innkeeper-ref> night|week|month <price>` is an opt-in MUTATING live test. It calls the shipped ClearRoom to reset that inn's rental, activates the NPC, selects a rent topic, checks gold and immediate heard state, then probes a repeat selection. It requires a loaded disposable test session, enough gold, DevBench and its gfx tool. It never issues a save command. It appends evidence to test/live-results.json. It can time out if input is consumed by the greeting; do not treat no charge as a patch failure. The JSON pass field on the first two recorded cases covers purchase/dimming and unchanged gold after the next input, not confirmed refusal playback (repeatLines was empty).
