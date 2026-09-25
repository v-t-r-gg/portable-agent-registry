#!/usr/bin/env python3
"""Check index.json against self-nomad pack --check, install, and validate.

Requires ``self-nomad`` on PATH (the pinned wheel). Does not reimplement
archive validation.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.json"
LISTING = ROOT / "site" / "index.html"


class IndexError_(RuntimeError):
    """Raised when the catalog does not match self-nomad."""


def _run(args: list[str]) -> dict[str, object]:
    completed = subprocess.run(args, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        raise IndexError_(f"{' '.join(args)} failed: {detail}")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise IndexError_(f"not JSON from {' '.join(args)}: {completed.stdout!r}") from exc
    if payload.get("ok") is not True:
        raise IndexError_(f"command not ok: {payload!r}")
    result = payload.get("result")
    if not isinstance(result, dict):
        raise IndexError_(f"result is not an object: {payload!r}")
    return result


def _digest(value: str) -> str:
    text = value.strip()
    if text.startswith("sha256:"):
        text = text.split(":", 1)[1]
    return text


def check_package(entry: dict[str, object], work: Path) -> None:
    name = str(entry["name"])
    pack_rel = str(entry["pack"])
    archive = ROOT / pack_rel
    if not archive.is_file():
        raise IndexError_(f"{name}: missing {pack_rel}")
    checked = _run(
        ["self-nomad", "--json", "pack", "--check", str(archive), "--profile", "specialist"]
    )
    if checked.get("profile") != "specialist":
        raise IndexError_(f"{name}: profile {checked.get('profile')!r}")
    digest = str(checked.get("content_digest") or "")
    if _digest(str(entry.get("content_digest"))) != digest:
        raise IndexError_(f"{name}: index digest does not match pack --check")
    skills = checked.get("skills")
    if skills != entry.get("skills"):
        raise IndexError_(f"{name}: skills {skills!r} != index {entry.get('skills')!r}")
    summary = checked.get("summary")
    if not isinstance(summary, dict):
        raise IndexError_(f"{name}: check JSON missing summary")
    identity = summary.get("self")
    if not isinstance(identity, dict):
        raise IndexError_(f"{name}: sidecar missing self")
    if str(identity.get("id")) != str(entry.get("self_id")):
        raise IndexError_(f"{name}: self_id mismatch")
    if identity.get("name") != entry.get("name"):
        raise IndexError_(f"{name}: name mismatch")
    if (identity.get("description") or "") != (entry.get("description") or ""):
        raise IndexError_(f"{name}: description mismatch")
    if str(summary.get("packer_version")) != str(entry.get("packer_version")):
        raise IndexError_(f"{name}: packer_version mismatch")
    if entry.get("runtimes_tested") != ["hermes", "openclaw"]:
        raise IndexError_(f"{name}: runtimes_tested must be hermes and openclaw")
    destination = work / name
    _run(["self-nomad", "--json", "install", str(archive), "--to", str(destination), "--no-git"])
    validated = _run(
        ["self-nomad", "--json", "--repo", str(destination), "validate", "--strict"]
    )
    if validated.get("valid") is not True:
        raise IndexError_(f"{name}: validate --strict failed: {validated!r}")
    if (destination / "identity" / "user.md").exists():
        raise IndexError_(f"{name}: installed tree contains identity/user.md")
    daily = destination / "memory" / "daily"
    if daily.exists():
        raise IndexError_(f"{name}: installed tree contains memory/daily")
    persona = (destination / "identity" / "persona.md").read_bytes()
    instructions = (destination / "identity" / "instructions.md").read_bytes()
    for adapter, target_name, comparisons in (
        ("hermes", "hermes", (("SOUL.md", persona),)),
        (
            "openclaw",
            "openclaw",
            (("SOUL.md", persona), ("AGENTS.md", instructions)),
        ),
    ):
        target = work / f"{name}-{target_name}"
        preview = _run(
            [
                "self-nomad",
                "--json",
                "--repo",
                str(destination),
                "restore",
                "--adapter",
                adapter,
                "--to",
                str(target),
            ]
        )
        if preview.get("applied") is not False:
            raise IndexError_(f"{name}: {adapter} preview applied")
        plan = preview.get("plan")
        encoded = json.dumps(plan)
        if "adapted" not in encoded and "unsupported" not in encoded:
            raise IndexError_(f"{name}: {adapter} plan has no adapted or unmapped class")
        applied = _run(
            [
                "self-nomad",
                "--json",
                "--repo",
                str(destination),
                "restore",
                "--adapter",
                adapter,
                "--to",
                str(target),
                "--yes",
            ]
        )
        if applied.get("applied") is not True:
            raise IndexError_(f"{name}: {adapter} restore failed")
        for relative, expected in comparisons:
            actual = target.joinpath(*relative.split("/")).read_bytes()
            if actual != expected:
                raise IndexError_(f"{name}: {adapter} {relative} bytes differ from the pack")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=INDEX)
    args = parser.parse_args(argv)
    if shutil.which("self-nomad") is None:
        print("self-nomad is not on PATH", file=sys.stderr)
        return 1
    try:
        document = json.loads(args.index.read_text(encoding="utf-8"))
        if document.get("index_schema") != 0:
            raise IndexError_("index_schema must be 0")
        if document.get("self_nomad_min") != "1.1.0":
            raise IndexError_("self_nomad_min must be 1.1.0")
        packages = document.get("packages")
        if not isinstance(packages, list) or not 3 <= len(packages) <= 5:
            raise IndexError_("packages must list 3 to 5 entries")
        listing = LISTING.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory(prefix="par-index-") as temporary:
            work = Path(temporary)
            os.environ["HOME"] = str(work / "home")
            os.environ["USERPROFILE"] = str(work / "home")
            os.environ["XDG_STATE_HOME"] = str(work / "state")
            (work / "home").mkdir()
            (work / "state").mkdir()
            for entry in packages:
                if not isinstance(entry, dict):
                    raise IndexError_("package entry is not an object")
                if entry.get("profile") != "specialist":
                    raise IndexError_(f"{entry.get('name')}: profile must be specialist")
                name = str(entry.get("name") or "")
                if name not in listing:
                    raise IndexError_(f"listing page does not name {name}")
                check_package(entry, work)
                print(f"OK  {name}")
    except (IndexError_, OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1
    print("OK  index")
    return 0


if __name__ == "__main__":
    os.environ.setdefault("SELF_NOMAD_BANNER", "0")
    raise SystemExit(main())
