import pytest
import responses
from unittest.mock import Mock
from asset_install.downloader import get_zip_url, download_version, NonRetryableError

def test_get_zip_url():
    url = get_zip_url("1.21.11")
    assert url == "https://github.com/InventivetalentDev/minecraft-assets/archive/refs/heads/1.21.11.zip"

@responses.activate
def test_download_version_success(tmp_path):
    version = "test-version"
    url = get_zip_url(version)
    responses.add(responses.GET, url, body=b"fake-zip-data", status=200)
    
    progress_mock = Mock()
    final_path = download_version(version, tmp_path, progress_mock)
    
    assert final_path.exists()
    assert final_path.read_bytes() == b"fake-zip-data"
    assert progress_mock.add_task.called
    assert progress_mock.update.called

@responses.activate
def test_download_version_404(tmp_path):
    version = "missing-version"
    url = get_zip_url(version)
    responses.add(responses.GET, url, status=404)
    
    progress_mock = Mock()
    with pytest.raises(NonRetryableError, match="404"):
        download_version(version, tmp_path, progress_mock)

@responses.activate
def test_download_version_retry(tmp_path):
    version = "retry-version"
    url = get_zip_url(version)
    
    # Fail 2 times with 500, then succeed
    responses.add(responses.GET, url, status=500)
    responses.add(responses.GET, url, status=500)
    responses.add(responses.GET, url, body=b"success", status=200)
    
    progress_mock = Mock()
    
    # We monkeypatch time.sleep to avoid waiting during tests
    import time
    original_sleep = time.sleep
    time.sleep = lambda x: None
    
    try:
        final_path = download_version(version, tmp_path, progress_mock)
        assert final_path.read_bytes() == b"success"
    finally:
        time.sleep = original_sleep

@responses.activate
def test_download_version_resume(tmp_path):
    version = "resume-version"
    url = get_zip_url(version)
    
    part_path = tmp_path / f"{version}.zip.part"
    part_path.write_bytes(b"hello")
    
    # 206 Partial Content
    responses.add(
        responses.GET, 
        url, 
        body=b"-world", 
        status=206, 
        match=[responses.matchers.header_matcher({"Range": "bytes=5-"})]
    )
    
    progress_mock = Mock()
    final_path = download_version(version, tmp_path, progress_mock)
    
    assert final_path.exists()
    assert final_path.read_bytes() == b"hello-world"

@responses.activate
def test_download_version_resume_fallback(tmp_path):
    version = "resume-fallback"
    url = get_zip_url(version)
    
    part_path = tmp_path / f"{version}.zip.part"
    part_path.write_bytes(b"hello")
    
    # 200 OK (server ignored Range)
    responses.add(
        responses.GET, 
        url, 
        body=b"full-file", 
        status=200
    )
    
    progress_mock = Mock()
    final_path = download_version(version, tmp_path, progress_mock)
    
    assert final_path.exists()
    assert final_path.read_bytes() == b"full-file"
