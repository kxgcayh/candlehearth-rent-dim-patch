# Build status

No implementation was approved by the investigation confidence gate. There is no build.py, release.toml, FOMOD or installable output. Do not package this investigation as a mod.

Inputs examined read-only: Candlehearth.esp and Candlehearth.bsa, Candlehearth 1.1.1 (Nexus 97542). Their hashes are in inputs.sha256. No third-party source or plugin is committed. Generated serialization is ignored under build/.

The successful read-only serialization used bash /Volumes/S512/Projects/ETC/skyrim-ai-toolkit/tools/spriggit-cli.sh serialize with --GameRelease SkyrimSE --PackageName Spriggit.Yaml --PackageVersion 0.41.0 -u. Set SPRIGGIT_WORK_ROOT inside build/ to keep the wrapper workspace local.
