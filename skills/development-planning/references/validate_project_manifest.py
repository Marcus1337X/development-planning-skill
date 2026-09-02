from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_HEADER_RE = re.compile(r"^\[(?P<mark>[^\]]*)\]\s*[：:]\s*(?P<name>.+?)\s*$")
MANIFEST_ENTRY_RE = re.compile(r"^\[(?P<mark>[^\]]*)\]\s*[：:]\s*(?P<path>.+?)\s*$")


def fail(reason: str, **details: object) -> int:
    print("INVALID")
    print(f"reason={reason}")
    for key, value in details.items():
        if value is not None:
            print(f"{key}={value}")
    return 1


def find_projects_file(start: Path) -> Path | None:
    current = start.resolve()
    for directory in (current, *current.parents):
        candidate = directory / ".development" / "projects.md"
        if candidate.is_file():
            return candidate
    return None


def find_active_project(projects_file: Path) -> tuple[str | None, str | None]:
    active: list[str] = []
    for raw_line in projects_file.read_text(encoding="utf-8-sig").splitlines():
        match = PROJECT_HEADER_RE.match(raw_line.strip())
        if not match:
            continue
        if "✅" in match.group("mark"):
            active.append(match.group("name").strip())

    if not active:
        return None, "no_active_project"
    if len(active) > 1:
        return None, "multiple_active_projects"
    return active[0], None


def safe_target(state_dir: Path, relative_text: str) -> Path | None:
    raw = Path(relative_text.strip().strip('"').strip("'"))
    if raw.is_absolute() or ".." in raw.parts:
        return None

    target = (state_dir / raw).resolve()
    try:
        target.relative_to(state_dir.resolve())
    except ValueError:
        return None
    return target


def main() -> int:
    cwd = Path.cwd().resolve()
    projects_file = find_projects_file(cwd)
    if projects_file is None:
        return fail("projects_file_not_found", cwd=cwd)

    try:
        project_name, error = find_active_project(projects_file)
    except (OSError, UnicodeError) as exc:
        return fail("projects_file_unreadable", projects_file=projects_file, error=exc)

    if error:
        return fail(error, projects_file=projects_file)
    assert project_name is not None

    state_dir = projects_file.parent / project_name
    manifest_file = state_dir / "manifest.md"

    if not state_dir.is_dir():
        return fail("project_state_dir_not_found", project=project_name, state_dir=state_dir)
    if not manifest_file.is_file():
        return fail(
            "manifest_file_not_found",
            project=project_name,
            manifest_file=manifest_file,
            can_rebuild="true",
        )

    confirmed: list[str] = []
    pending: list[str] = []
    missing: list[str] = []
    unconfirmed_existing: list[str] = []

    try:
        lines = manifest_file.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError) as exc:
        return fail("manifest_file_unreadable", manifest_file=manifest_file, error=exc)

    for raw_line in lines:
        match = MANIFEST_ENTRY_RE.match(raw_line.strip())
        if not match:
            continue

        relative_text = match.group("path").strip()
        target = safe_target(state_dir, relative_text)
        if target is None:
            return fail(
                "manifest_path_invalid",
                manifest_file=manifest_file,
                path=relative_text,
            )

        is_confirmed = "✅" in match.group("mark")
        if is_confirmed:
            confirmed.append(relative_text)
            if not target.is_file():
                missing.append(relative_text)
        else:
            pending.append(relative_text)
            if target.is_file():
                unconfirmed_existing.append(relative_text)

    if missing:
        print("INVALID")
        print("reason=confirmed_file_missing")
        print(f"project={project_name}")
        print(f"manifest_file={manifest_file}")
        for item in missing:
            print(f"missing={item}")
        print("can_rebuild=true")
        return 1

    print("VALID")
    print(f"project={project_name}")
    print(f"manifest_file={manifest_file}")
    print(f"confirmed_count={len(confirmed)}")
    print(f"pending_count={len(pending)}")
    for item in unconfirmed_existing:
        print(f"unconfirmed_existing={item}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
