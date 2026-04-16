This directory contains CI  files.

Purpose:
- provide detector coverage checks in CI
- keep sample-only content out of runtime paths
- make cleanup simple if a pipeline no longer needs them

Layout:
- `patterns/` holds sample code patterns
- `deps/` holds a standalone dependency manifest
- `keys/` holds credential
- `manifests/` holds sample cluster manifests
