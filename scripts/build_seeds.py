#!/usr/bin/env python3
"""Build specialist seed packs with the self-nomad CLI and refresh index.json.

Uses init, propose, validate, approve, apply, pack, and pack --check.
Does not copy a live personal repository.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT / "packages"

SEEDS = (
    {
        "name": "demo-echo",
        "version": "1.0.0",
        "description": "Repeats the operator's last sentence. Proves the pack pipe.",
        "files": {
            "identity/persona.md": "# Persona\n\nEcho answers with the words it was given.\n",
            "identity/instructions.md": "# Instructions\n\nRepeat the operator's last sentence and stop.\n",
            "identity/identity.md": "# Identity\n\nName: Echo\n",
            "tools/notes.md": "# Tool notes\n\nNo external tools.\n",
            "skills/echo/SKILL.md": "---\nname: echo\ndescription: Repeat text.\n---\n\n# Echo\n\nReturn the input unchanged.\n",
            "skills/echo/LICENSE": "MIT. This skill is sample content for the pack pipe.\n",
        },
    },
    {
        "name": "research-summarizer",
        "version": "1.0.0",
        "description": "Turns source notes into a short brief without personal memory.",
        "files": {
            "identity/persona.md": "# Persona\n\nSummarizer writes a short brief and cites the note it used.\n",
            "identity/instructions.md": "# Instructions\n\nSummarize only the text the operator supplies. Do not invent sources.\n",
            "identity/identity.md": "# Identity\n\nName: Summarizer\n",
            "tools/notes.md": "# Tool notes\n\nRead the supplied note. Do not browse.\n",
            "skills/summarize/SKILL.md": "---\nname: summarize\ndescription: Write a five-line brief.\n---\n\n# Summarize\n\nFive lines, then stop.\n",
            "skills/summarize/LICENSE": "MIT. Sample specialist skill.\n",
        },
    },
    {
        "name": "code-reviewer",
        "version": "1.0.0",
        "description": "Reviews a diff for correctness and missing tests.",
        "files": {
            "identity/persona.md": "# Persona\n\nReviewer is direct and names the line that failed.\n",
            "identity/instructions.md": "# Instructions\n\nReview the diff. Prefer a failing test over a style note.\n",
            "identity/identity.md": "# Identity\n\nName: Reviewer\n",
            "tools/notes.md": "# Tool notes\n\nRead the diff. Do not apply it.\n",
            "skills/review-diff/SKILL.md": "---\nname: review-diff\ndescription: Comment on a unified diff.\n---\n\n# Review diff\n\nList defects, then missing tests.\n",
            "skills/review-diff/LICENSE": "MIT. Sample specialist skill.\n",
        },
    },
)


def _run(args: list[str], env: dict[str, str]) -> dict[str, object]:
    completed = subprocess.run(args, check=False, capture_output=True, text=True, env=env)
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        raise SystemExit(f"{' '.join(args[:6])} failed:\n{detail}")
    if args[1:2] == ["--version"] or "--json" not in args:
        return {"stdout": completed.stdout.strip()}
    payload = json.loads(completed.stdout)
    if payload.get("ok") is not True:
        raise SystemExit(f"not ok: {payload}")
    result = payload.get("result")
    if not isinstance(result, dict):
        raise SystemExit(f"bad result: {payload}")
    return result


def _propose(cli: str, repo: Path, work: Path, env: dict[str, str], files: dict[str, str]) -> None:
    operations: list[str] = []
    for relative, content in files.items():
        source = work / "payload" / relative
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(content, encoding="utf-8")
        kind = "replace" if (repo / relative).exists() else "add"
        operations.append(
            f"  - kind: {kind}\n    path: {relative}\n    content_source: {source.as_posix()}\n"
        )
    change = work / "change.yaml"
    change.write_text("operations:\n" + "".join(operations), encoding="utf-8")
    proposed = _run(
        [cli, "--json", "--repo", str(repo), "propose", "--reason", "Seed specialist files", "--change", str(change)],
        env,
    )
    proposal = proposed.get("proposal")
    if not isinstance(proposal, dict) or "id" not in proposal:
        raise SystemExit(f"propose missing id: {proposed}")
    proposal_id = str(proposal["id"])
    _run([cli, "--json", "--repo", str(repo), "validate", proposal_id], env)
    _run([cli, "--json", "--repo", str(repo), "approve", proposal_id, "--identifier", "seed"], env)
    applied = _run([cli, "--json", "--repo", str(repo), "apply", proposal_id], env)
    if applied.get("status") != "applied":
        raise SystemExit(f"apply status: {applied}")


def main() -> int:
    cli = shutil.which("self-nomad")
    if cli is None:
        print("self-nomad is not on PATH", file=sys.stderr)
        return 1
    version = subprocess.run([cli, "--version"], check=True, capture_output=True, text=True).stdout.strip()
    if version != "1.1.0":
        print(f"refusing to pack seeds with self-nomad {version}; need 1.1.0", file=sys.stderr)
        return 1
    packages: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="par-seeds-") as temporary:
        work = Path(temporary)
        env = os.environ.copy()
        env["SELF_NOMAD_BANNER"] = "0"
        env["GIT_TERMINAL_PROMPT"] = "0"
        for seed in SEEDS:
            repo = work / str(seed["name"])
            _run(
                [
                    cli,
                    "--json",
                    "init",
                    str(repo),
                    "--name",
                    str(seed["name"]),
                    "--description",
                    str(seed["description"]),
                ],
                env,
            )
            _propose(cli, repo, work / f"{seed['name']}-src", env, seed["files"])  # type: ignore[arg-type]
            archive = work / f"{seed['name']}.snpack"
            packed = _run(
                [cli, "--json", "--repo", str(repo), "pack", "--out", str(archive), "--profile", "specialist"],
                env,
            )
            checked = _run(
                [cli, "--json", "pack", "--check", str(archive), "--profile", "specialist"],
                env,
            )
            if checked.get("content_digest") != packed.get("content_digest"):
                raise SystemExit("pack and check digests differ")
            if checked.get("profile") != "specialist":
                raise SystemExit("seed is not specialist")
            summary = checked.get("summary")
            if not isinstance(summary, dict) or not isinstance(summary.get("self"), dict):
                raise SystemExit(f"missing sidecar self: {checked}")
            identity = summary["self"]
            relative = f"packages/{seed['name']}/{seed['version']}/{seed['name']}.snpack"
            destination = ROOT / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(archive, destination)
            skills = checked.get("skills")
            packages.append(
                {
                    "name": seed["name"],
                    "self_id": identity["id"],
                    "description": identity.get("description") or seed["description"],
                    "profile": "specialist",
                    "pack": relative,
                    "content_digest": f"sha256:{checked['content_digest']}",
                    "skills": skills,
                    "runtimes_tested": ["hermes", "openclaw"],
                    "packer_version": version,
                }
            )
            print(f"packed {relative}")
    document = {"index_schema": 0, "self_nomad_min": "1.1.0", "packages": packages}
    (ROOT / "index.json").write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    names = "\n".join(f"    <li><a href=\"../{item['pack']}\">{item['name']}</a> — {item['description']}</li>" for item in packages)
    listing = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Portable Agent Registry</title>
</head>
<body>
  <h1>Portable Agent Registry 0.1.0</h1>
  <p>Read-only catalog of specialist <code>self-nomad-pack-v1</code> snapshots.
  No accounts, upload, or reputation scores.</p>
  <ul>
{names}
  </ul>
  <p>Install with <code>self-nomad install ARCHIVE --to NEW_REPO</code>,
  then <code>self-nomad restore</code> into Hermes or OpenClaw.</p>
</body>
</html>
"""
    site = ROOT / "site"
    site.mkdir(exist_ok=True)
    (site / "index.html").write_text(listing, encoding="utf-8")
    print("wrote index.json and site/index.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
