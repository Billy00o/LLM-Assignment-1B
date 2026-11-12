"""Download and verify Google's pinned Gemma 2B IT checkpoint."""
import argparse
import hashlib
import json
import platform
from importlib.metadata import version

from src.model import CACHE, CHECKPOINT, CHECKPOINT_FILES, MODEL_ID, MODEL_REVISION, ROOT, WEIGHT_SHARDS, check_checkpoint


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--download", action="store_true", help="Download the official checkpoint from Hugging Face")
    args = parser.parse_args()
    if args.download:
        from huggingface_hub import snapshot_download
        from huggingface_hub.errors import HfHubHTTPError, LocalTokenNotFoundError
        from requests.exceptions import RequestException

        try:
            check_checkpoint()
        except FileNotFoundError:
            try:
                snapshot_download(MODEL_ID, revision=MODEL_REVISION, cache_dir=CACHE, token=True,
                                  allow_patterns=[*CHECKPOINT_FILES, *WEIGHT_SHARDS], max_workers=2)
            except LocalTokenNotFoundError:
                parser.exit(1, "Run hf auth login after accepting the Gemma model terms.\n")
            except (HfHubHTTPError, RequestException, OSError, RuntimeError) as error:
                parser.exit(1, f"Checkpoint download failed ({type(error).__name__}). Confirm Hugging Face access and rerun to resume.\n")
    try:
        check_checkpoint()
    except FileNotFoundError as error:
        parser.exit(1, f"{error}\n")
    shards = {name: sha256_file(CHECKPOINT / name) for name in WEIGHT_SHARDS}
    verified = all(shards[name] == expected for name, (_, expected) in WEIGHT_SHARDS.items())
    report = {"model": MODEL_ID, "revision": MODEL_REVISION, "device": "cpu", "dtype": "bfloat16",
              "python": platform.python_version(), "huggingface_hub": version("huggingface-hub"),
              "shard_sha256": shards, "verified": verified}
    print(json.dumps(report, indent=2))
    (ROOT / "runtime" / "preflight.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if not verified:
        parser.exit(1, "Checkpoint SHA-256 mismatch. Remove the affected shard and run preflight.py --download again.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
