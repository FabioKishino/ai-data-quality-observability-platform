from pathlib import Path

from observability_platform import __version__
from observability_platform.settings import get_project_paths

ROOT = Path(__file__).resolve().parents[1]


def test_package_has_version() -> None:
    assert __version__ == "0.1.0"


def test_expected_project_directories_exist() -> None:
    expected_directories = [
        ".github/workflows",
        "dagster_project",
        "data/bronze",
        "data/silver",
        "data/gold",
        "data/warehouse",
        "dbt",
        "docs",
        "src/observability_platform",
        "tests",
    ]

    missing = [path for path in expected_directories if not (ROOT / path).is_dir()]

    assert missing == []


def test_project_paths_contract() -> None:
    paths = get_project_paths(ROOT)

    assert paths.root == ROOT
    assert paths.data_root == ROOT / "data"
    assert paths.warehouse_path == ROOT / "data" / "warehouse" / "observability.duckdb"
