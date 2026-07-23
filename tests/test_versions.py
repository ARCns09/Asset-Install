from pathlib import Path
from asset_install.versions import get_approved_versions, get_versions_file_path

def test_get_versions_file_path():
    path = get_versions_file_path()
    assert path.name == "versions.txt"
    assert path.parent.name == "config"

def test_get_approved_versions():
    versions = get_approved_versions()
    assert len(versions) > 0
    assert "1.0" in versions
    assert "26.2" in versions
