import os
from pathlib import Path
from asset_install.paths import resolve_path, is_path_writable, ensure_directory

def test_resolve_path():
    path = resolve_path("~/test_dir")
    assert str(path) == str(Path.home() / "test_dir")

def test_is_path_writable(tmp_path):
    assert is_path_writable(tmp_path)
    
    # Create an un-writable directory (read-only)
    read_only_dir = tmp_path / "readonly"
    read_only_dir.mkdir(mode=0o444)
    assert not is_path_writable(read_only_dir)
    
    # Restore permissions to allow cleanup
    read_only_dir.chmod(0o777)

def test_ensure_directory(tmp_path):
    new_dir = tmp_path / "a" / "b" / "c"
    ensure_directory(new_dir)
    assert new_dir.exists()
    assert new_dir.is_dir()
