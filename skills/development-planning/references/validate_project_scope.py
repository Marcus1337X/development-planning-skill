from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_HEADER_RE = re.compile(r"^\[(?P<mark>[^\]]*)\]\s*[：:]\s*(?P<name>.+?)\s*$")
PROJECT_PATH_RE = re.compile(r"^项目目录\s*[：:]\s*(?P<path>.+?)\s*$")


@dataclass
class Project:
    name: str
    active: bool
    path_text: str | None = None


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


def parse_projects(path: Path) -> list[Project]:
    projects: list[Project] = []
    current: Project | None = None

    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        header = PROJECT_HEADER_RE.match(line)
        if header:
            mark = header.group("mark").strip()
            current = Project(
                name=header.group("name").strip(),
                active="✅" in mark,
            )
            projects.append(current)
            continue

        if current is not None:
            path_match = PROJECT_PATH_RE.match(line)
            if path_match:
                current.path_text = path_match.group("path").strip().strip('"').strip("'")

    return projects


def normalize_path(path_text: str) -> Path:
    expanded = os.path.expandvars(os.path.expanduser(path_text))
    return Path(expanded).resolve()


def is_within(child: Path, root: Path) -> bool:
    child_text = os.path.normcase(str(child.resolve()))
    root_text = os.path.normcase(str(root.resolve()))
    try:
        return os.path.commonpath([child_text, root_text]) == root_text
    except ValueError:
        return False


def main() -> int:
    cwd = Path.cwd().resolve()
    projects_file = find_projects_file(cwd)

    if projects_file is None:
        return fail("projects_file_not_found", cwd=cwd)

    try:
        projects = parse_projects(projects_file)
    except (OSError, UnicodeError) as exc:
        return fail("projects_file_unreadable", projects_file=projects_file, error=exc)

    active_projects = [project for project in projects if project.active]

    if not active_projects:
        return fail("no_active_project", projects_file=projects_file)

    if len(active_projects) > 1:
        return fail(
            "multiple_active_projects",
            projects_file=projects_file,
            projects=", ".join(project.name for project in active_projects),
        )

    project = active_projects[0]

    if not project.path_text:
        return fail(
            "project_path_missing",
            project=project.name,
            projects_file=projects_file,
        )

    try:
        project_root = normalize_path(project.path_text)
    except (OSError, RuntimeError, ValueError) as exc:
        return fail(
            "project_path_invalid",
            project=project.name,
            path=project.path_text,
            error=exc,
        )

    if not project_root.is_dir():
        return fail(
            "project_path_not_found",
            project=project.name,
            project_root=project_root,
        )

    if not is_within(cwd, project_root):
        return fail(
            "cwd_outside_project",
            project=project.name,
            project_root=project_root,
            cwd=cwd,
        )

    development_root = projects_file.parent
    state_dir = development_root / project.name

    print("VALID")
    print(f"project={project.name}")
    print(f"project_root={project_root}")
    print(f"cwd={cwd}")
    print(f"projects_file={projects_file}")
    print(f"state_dir={state_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
