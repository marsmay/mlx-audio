import json
import subprocess
from pathlib import Path

import pytest
import soundfile as sf

SCRIPTS = Path(__file__).parent.parent / "scripts"
PYTHON = "python3"


def run_script(*args, timeout=600):
    result = subprocess.run(
        [PYTHON, str(SCRIPTS / args[0]), *args[1:]],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result


@pytest.mark.slow
def test_batch_dubbing_two_segments(tmp_path):
    config = {
        "model": "custom-voice",
        "voice": "Serena",
        "language": "English",
        "temperature": 0.7,
        "segments": [
            {"id": 1, "text": "First segment.", "speaker": "Serena"},
            {"id": 2, "text": "Second segment.", "speaker": "Ryan"},
        ],
    }
    config_path = tmp_path / "dubbing.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    output_dir = tmp_path / "output"

    r = run_script(
        "batch_dubbing.py",
        "--config", str(config_path),
        "--output", str(output_dir),
    )

    assert r.returncode == 0, f"stderr: {r.stderr}\nstdout: {r.stdout}"

    # Verify individual segments
    individual_dir = output_dir / "individual"
    assert individual_dir.exists()
    segments = sorted(individual_dir.glob("segment_*.wav"))
    assert len(segments) == 2, f"Expected 2 segments, found {segments}"

    for seg in segments:
        data, sr = sf.read(str(seg))
        assert sr > 0
        assert len(data) > 0

    # Verify combined audio
    combined = output_dir / "combined.wav"
    assert combined.exists()
    data, sr = sf.read(str(combined))
    assert len(data) > 0

    # Verify manifest
    manifest_path = output_dir / "manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text())
    assert manifest["succeeded_count"] == 2
    assert manifest["combined_file"] is not None
