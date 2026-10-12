"""Create a local Git bundle outside tracked files after a validated checkpoint."""
from __future__ import annotations

import argparse
import pathlib
import subprocess
from datetime import datetime, timezone

from registry import ROOT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    output = pathlib.Path(args.output_dir) if args.output_dir else ROOT.parent / "Maliky-Repository-Intelligence-checkpoints"
    output.mkdir(parents=True, exist_ok=True)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bundle = output / f"maliky-ri-{stamp}-{head[:12]}.bundle"
    subprocess.run(["git", "bundle", "create", str(bundle), "--all"], cwd=ROOT, check=True)
    print(bundle)


if __name__ == "__main__":
    main()
