import sys
from pathlib import Path
from asset_install.paths import resolve_path, is_path_writable, ensure_directory, get_app_data_dir

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

def test_get_app_data_dir_linux(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    
    app_dir = get_app_data_dir()
    assert str(app_dir).startswith(str(tmp_path / ".local" / "share"))
    assert app_dir.name == "asset-install"

def test_get_app_data_dir_windows(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "win32")
    win_path = str(tmp_path / "AppData" / "Local")
    monkeypatch.setenv("LOCALAPPDATA", win_path)
    
    app_dir = get_app_data_dir()
    assert str(app_dir).startswith(win_path)
    assert app_dir.name == "asset-install"

def test_get_app_data_dir_mac(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    
    app_dir = get_app_data_dir()
    assert str(app_dir).startswith(str(tmp_path / "Library" / "Application Support"))
    assert app_dir.name == "asset-install"
