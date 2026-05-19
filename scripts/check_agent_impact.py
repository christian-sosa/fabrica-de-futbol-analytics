from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path.cwd()
CONTEXT_PATH = ROOT / "AGENT_CONTEXT.json"


def git_lines(args: list[str]) -> list[str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def changed_files() -> list[str]:
    if "--files" in sys.argv:
        index = sys.argv.index("--files")
        return sys.argv[index + 1 :]

    return sorted(
        set(
            git_lines(["diff", "--name-only", "HEAD", "--"])
            + git_lines(["diff", "--name-only", "--cached", "--"])
            + git_lines(["ls-files", "--others", "--exclude-standard"])
        )
    )


def main() -> int:
    if not CONTEXT_PATH.exists():
        print("AGENT_CONTEXT.json not found.", file=sys.stderr)
        return 1

    context = json.loads(CONTEXT_PATH.read_text(encoding="utf-8"))
    files = changed_files()
    matches: list[tuple[dict[str, object], list[str]]] = []

    for rule in context.get("impact_rules", []):
        patterns = [re.compile(pattern) for pattern in rule.get("regex", [])]
        matched_files = [file for file in files if any(pattern.search(file) for pattern in patterns)]
        if matched_files:
            matches.append((rule, matched_files))

    print(f"Agent impact check: {len(files)} changed file(s) inspected.")

    if not matches:
        print("No cross-repo impact rules matched.")
        return 0

    print("\nCross-repo review required:")
    for rule, matched_files in matches:
        print(f"\n- {rule['id']}: {rule['description']}")
        print(f"  Matched files: {', '.join(matched_files)}")
        if rule.get("review_repository"):
            print(f"  Review repo: {rule['review_repository']}")
        review_files = rule.get("review_files", [])
        if review_files:
            print(f"  Review files: {', '.join(review_files)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
