from asset_install.manifest import Manifest

def test_manifest_creation_and_update(tmp_path):
    manifest = Manifest(tmp_path)
    
    # Should create an empty manifest
    assert manifest.data["versions"] == {}
    
    manifest.update_version("1.0", "complete", size=123, sha256="abc")
    
    # Reload from disk
    manifest2 = Manifest(tmp_path)
    assert manifest2.data["versions"]["1.0"]["status"] == "complete"
    assert manifest2.data["versions"]["1.0"]["size"] == 123
    assert manifest2.data["versions"]["1.0"]["sha256"] == "abc"
    
def test_manifest_atomic_save(tmp_path):
    manifest = Manifest(tmp_path)
    manifest.update_version("1.1", "downloading")
    
    assert (tmp_path / "manifest.json").exists()
