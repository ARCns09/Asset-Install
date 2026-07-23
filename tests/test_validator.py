import zipfile
from asset_install.validator import is_valid_zip, calculate_sha256

def test_calculate_sha256(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("hello world")
    
    # echo -n "hello world" | sha256sum
    # b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9
    assert calculate_sha256(file_path) == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

def test_is_valid_zip(tmp_path):
    zip_path = tmp_path / "test.zip"
    
    # Create valid zip
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.writestr("test.txt", "data")
        
    assert is_valid_zip(zip_path)
    
    # Test invalid zip
    bad_zip_path = tmp_path / "bad.zip"
    bad_zip_path.write_text("not a zip file")
    assert not is_valid_zip(bad_zip_path)
    
    # Test non-existent file
    assert not is_valid_zip(tmp_path / "does-not-exist.zip")
