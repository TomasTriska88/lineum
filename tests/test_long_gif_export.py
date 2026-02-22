import pytest
import numpy as np
import os
import sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

def test_gif_decimation_prevents_overflow(tmp_path):
    """
    Test that supplying >500 frames to lineum's internal GIF savers
    triggers the downsampling protection against the 16-bit ushort overflow.
    Instead of running the full 10,000 step physics engine, we extract the local
    `save_gif` function from lineum.py by executing its code.
    """
    import PIL.Image
    
    # Read lineum.py
    lineum_path = os.path.join(repo_root, "lineum.py")
    with open(lineum_path, 'r', encoding='utf-8') as f:
        code = f.read()
        
    start_idx = code.find("def save_gif(data_frames, filename")
    end_idx = code.find("def save_full_overlay_gif", start_idx)
    save_gif_code = code[start_idx:end_idx].rstrip()
    
    # Un-indent the nested block
    save_gif_lines = [line[4:] if line.startswith("    ") else line for line in save_gif_code.split('\n')]
    clean_save_gif = "\n".join(save_gif_lines)

    # 3. Create dummy globals space and mock notify_file_creation
    mock_globals = {
        "notify_file_creation": lambda path, success=True, error=None: print(f"Mock notify: {path}, {success}, {error}")
    }
    
    # Compile and bind the extracted save_gif function
    exec(clean_save_gif, mock_globals)
    save_gif = mock_globals["save_gif"]
    
    # 4. Generate 2500 dummy frames (amplitude-like)
    dummy_frames = [np.random.rand(4, 4) for _ in range(2500)]
    out_file = tmp_path / "test_overflow.gif"
    
    # 5. Call the extracted function
    save_gif(dummy_frames, str(out_file), cmap='viridis', vmin=0.0, vmax=1.0)
    
    # 6. Verify the file exists and has exactly 500 frames due to step=5 downsampling
    assert os.path.exists(out_file), "Failed to save the decimated GIF."
    
    with PIL.Image.open(out_file) as img:
        frames_in_gif = img.n_frames
        assert frames_in_gif == 500, f"Expected 500 decimated frames, got {frames_in_gif}"
