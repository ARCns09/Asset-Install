import json
import responses
from unittest.mock import Mock
from asset_install.versions import (
    is_valid_version,
    sort_versions,
    group_versions,
    fetch_versions_from_github,
    get_available_versions
)

def test_is_valid_version():
    assert is_valid_version("1.21")
    assert is_valid_version("1.21.11")
    assert is_valid_version("26.1")
    assert is_valid_version("26.1.2")
    
    # Exclusions
    assert not is_valid_version("master")
    assert not is_valid_version("main")
    assert not is_valid_version("1.21-rc1")
    assert not is_valid_version("26w14a")
    assert not is_valid_version("1.0.0.0")

def test_sort_versions():
    versions = ["1.1", "1.10", "1.2", "26.1", "1.1.1", "26.1.2", "26.2"]
    sorted_v = sort_versions(versions)
    assert sorted_v == ["1.1", "1.1.1", "1.2", "1.10", "26.1", "26.1.2", "26.2"]

def test_group_versions():
    versions = ["1.20", "1.20.1", "1.21", "1.21.11", "26.1", "26.1.2", "26.2"]
    groups = group_versions(versions)
    
    assert groups["1.20.x"] == ["1.20", "1.20.1"]
    assert groups["1.21.x"] == ["1.21", "1.21.11"]
    assert groups["26.1.x"] == ["26.1", "26.1.2"]
    assert groups["26.2.x"] == ["26.2"]

@responses.activate
def test_fetch_versions_from_github():
    url = "https://api.github.com/repos/InventivetalentDev/minecraft-assets/git/refs/heads"
    responses.add(
        responses.GET,
        url,
        json=[
            {"ref": "refs/heads/1.21"},
            {"ref": "refs/heads/1.21-rc1"},
            {"ref": "refs/heads/26.1"},
            {"ref": "refs/heads/master"}
        ],
        status=200
    )
    
    versions = fetch_versions_from_github()
    assert versions == ["1.21", "26.1"]

@responses.activate
def test_get_available_versions_fallback(monkeypatch, tmp_path):
    # Mock cache path to tmp_path
    monkeypatch.setattr("asset_install.versions.get_cached_versions_path", lambda: tmp_path / "versions.json")
    
    url = "https://api.github.com/repos/InventivetalentDev/minecraft-assets/git/refs/heads"
    responses.add(responses.GET, url, status=500)
    
    # 1. No cache exists -> fallback to bundled
    # We mock load_bundled_versions
    monkeypatch.setattr("asset_install.versions.load_bundled_versions", lambda: ["1.0", "1.1"])
    
    warning_mock = Mock()
    versions = get_available_versions(refresh=True, print_warning=warning_mock)
    assert versions == ["1.0", "1.1"]
    assert warning_mock.call_count == 1
    
    # 2. Cache exists -> fallback to cache
    cache_path = tmp_path / "versions.json"
    with open(cache_path, "w") as f:
        json.dump({"versions": ["1.2", "26.1"]}, f)
        
    warning_mock.reset_mock()
    versions2 = get_available_versions(refresh=True, print_warning=warning_mock)
    assert versions2 == ["1.2", "26.1"]
    assert warning_mock.call_count == 1
