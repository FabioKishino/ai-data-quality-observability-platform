"""Shared project settings for local execution."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    """Canonical local paths used by the platform."""

    root: Path
    data_root: Path
    warehouse_path: Path


def discover_project_root(start: Path | None = None) -> Path:
    """Find the repository root by walking upward until pyproject.toml is found."""

    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").exists():
            return candidate
    msg = f"Could not discover project root from {current}"
    raise RuntimeError(msg)


def get_project_paths(root: Path | None = None) -> ProjectPaths:
    """Return the local filesystem contract used across stages."""

    project_root = (root or discover_project_root()).resolve()
    data_root = project_root / "data"
    return ProjectPaths(
        root=project_root,
        data_root=data_root,
        warehouse_path=data_root / "warehouse" / "observability.duckdb",
    )
