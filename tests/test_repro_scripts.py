import pathlib

def test_repro_script_saves_state():
    """
    Ověří, že skript repro_spec6_false_s41.py explicitně zapíná 
    ukládání checkpointů ve standardním (nikoliv --quick) režimu.
    """
    root = pathlib.Path(__file__).resolve().parent.parent
    script_path = root / "scripts" / "repro_spec6_false_s41.py"
    
    assert script_path.exists(), "Repro script nenalezen!"
    
    content = script_path.read_text(encoding="utf-8")
    
    # Check that LINEUM_SAVE_STATE is explicitly activated
    assert 'env["LINEUM_SAVE_STATE"] = "1"' in content, "Skript musí explicitně zapínat LINEUM_SAVE_STATE='1' pro export referencí!"
