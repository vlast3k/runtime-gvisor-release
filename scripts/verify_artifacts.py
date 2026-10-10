#!/usr/bin/env python3

import hashlib
import json
from pathlib import Path
import sys

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPOSITORY_ROOT / "ARTIFACTS.json"
BLOBS_ROOT = REPOSITORY_ROOT / "blobs"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as artifact:
        for chunk in iter(lambda: artifact.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    failures = []

    for name, expected in manifest["artifacts"].items():
        path = BLOBS_ROOT / expected["blob"]
        if not path.is_file():
            failures.append(f"{name}: missing {path}")
            continue

        actual_size = path.stat().st_size
        if actual_size != expected["size"]:
            failures.append(
                f"{name}: size {actual_size}, expected {expected['size']}"
            )

        actual_hash = sha256(path)
        if actual_hash != expected["sha256"]:
            failures.append(
                f"{name}: sha256 {actual_hash}, expected {expected['sha256']}"
            )

    if failures:
        print("Artifact verification failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"Verified {len(manifest['artifacts'])} release artifacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
