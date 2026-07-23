from asset_install.history import get_history, add_history_entry, clear_history

def test_history(monkeypatch, tmp_path):
    monkeypatch.setattr("asset_install.history.get_history_path", lambda: tmp_path / "history.json")
    
    assert get_history() == []
    
    add_history_entry("1.21.1", "2026-07-23T20:00:00", "/test/path")
    
    hist = get_history()
    assert len(hist) == 1
    assert hist[0]["version"] == "1.21.1"
    
    # Should prepend
    add_history_entry("26.1", "2026-07-23T21:00:00", "/test/path2")
    hist = get_history()
    assert len(hist) == 2
    assert hist[0]["version"] == "26.1"
    assert hist[1]["version"] == "1.21.1"
    
    clear_history()
    assert get_history() == []
