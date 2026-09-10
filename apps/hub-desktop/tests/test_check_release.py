import importlib.util
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _load():
    spec = importlib.util.spec_from_file_location(
        "check_release", ROOT / "scripts" / "check_release.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _wheel(dist: Path, name: str, version: str, files: dict[str, str]) -> None:
    path = dist / f"{name}-{version}-py3-none-any.whl"
    with zipfile.ZipFile(path, "w") as zf:
        for inner, content in files.items():
            zf.writestr(inner, content)


def _good(dist: Path, version: str = "0.2.0") -> None:
    def meta(reqs: list[str]) -> str:
        return "\n".join(["Metadata-Version: 2.1", f"Version: {version}", *reqs])
    _wheel(
        dist,
        "pcl_core",
        version,
        {"pcl_core-0.2.0.dist-info/METADATA": meta([])},
    )
    _wheel(
        dist,
        "pcl_pca",
        version,
        {"pcl_pca-0.2.0.dist-info/METADATA": meta([f"Requires-Dist: pcl-core=={version}"])},
    )
    _wheel(
        dist,
        "pcl_sdk",
        version,
        {"pcl_sdk-0.2.0.dist-info/METADATA": meta([f"Requires-Dist: pcl-core=={version}"])},
    )
    _wheel(
        dist,
        "pcl_server",
        version,
        {
            "pcl_server/static/index.html": "<html></html>",
            "pcl_server/static/assets/app.js": "console.log(1)",
            "pcl_server-0.2.0.dist-info/METADATA": meta(
                [
                    f"Requires-Dist: pcl-core=={version}",
                    f"Requires-Dist: pcl-pca=={version}",
                    f"Requires-Dist: pcl-sdk=={version}",
                ]
            ),
        },
    )
    _wheel(
        dist,
        "personal_context_hub",
        version,
        {
            "personal_context_hub-0.2.0.dist-info/METADATA": meta(
                [f"Requires-Dist: pcl-server=={version}"]
            ),
            "personal_context_hub-0.2.0.dist-info/entry_points.txt": (
                "[console_scripts]\npersonal-context-hub = hub_desktop.cli:main\npch = hub_desktop.cli:main\n"
            ),
        },
    )


def test_check_release_passes_synthetic(tmp_path: Path):
    check = _load()
    _good(tmp_path)
    assert check.check(tmp_path) == []


def test_check_release_missing_index(tmp_path: Path):
    check = _load()
    _good(tmp_path)
    # overwrite server wheel without index
    _wheel(
        tmp_path,
        "pcl_server",
        "0.2.0",
        {
            "pcl_server/static/assets/app.js": "x",
            "pcl_server-0.2.0.dist-info/METADATA": "Requires-Dist: pcl-core==0.2.0\nRequires-Dist: pcl-pca==0.2.0\nRequires-Dist: pcl-sdk==0.2.0\n",
        },
    )
    errors = check.check(tmp_path)
    assert any("index.html" in e for e in errors)


def test_check_release_version_mismatch(tmp_path: Path):
    check = _load()
    _good(tmp_path)
    _wheel(tmp_path, "pcl_core", "0.9.0", {"pcl_core-0.9.0.dist-info/METADATA": "Version: 0.9.0\n"})
    errors = check.check(tmp_path)
    assert errors


def test_check_release_missing_entry_point(tmp_path: Path):
    check = _load()
    _good(tmp_path)
    _wheel(
        tmp_path,
        "personal_context_hub",
        "0.2.0",
        {
            "personal_context_hub-0.2.0.dist-info/METADATA": "Requires-Dist: pcl-server==0.2.0\n",
            "personal_context_hub-0.2.0.dist-info/entry_points.txt": "[console_scripts]\nhub-desktop=hub_desktop.main:main\n",
        },
    )
    errors = check.check(tmp_path)
    assert any("pch" in e or "entry" in e for e in errors)


def test_check_release_unpinned_sibling(tmp_path: Path):
    check = _load()
    _good(tmp_path)
    _wheel(
        tmp_path,
        "pcl_server",
        "0.2.0",
        {
            "pcl_server/static/index.html": "<html></html>",
            "pcl_server/static/assets/app.js": "x",
            "pcl_server-0.2.0.dist-info/METADATA": "Requires-Dist: pcl-core\nRequires-Dist: pcl-pca==0.2.0\nRequires-Dist: pcl-sdk==0.2.0\n",
        },
    )
    errors = check.check(tmp_path)
    assert any("pcl-core" in e for e in errors)
