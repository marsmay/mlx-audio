import subprocess
from pathlib import Path

import pytest
import soundfile as sf

SCRIPTS = Path(__file__).parent.parent / "scripts"
PYTHON = "python3"


def run_script(*args, timeout=300):
    result = subprocess.run(
        [PYTHON, str(SCRIPTS / args[0]), *args[1:]],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result


@pytest.mark.slow
def test_custom_voice_generates_wav(tmp_path):
    output = tmp_path / "custom_voice.wav"
    r = run_script(
        "run_tts.py", "custom-voice",
        "--text", "Hello, this is a functional test.",
        "--voice", "Serena",
        "--language", "English",
        "--output", str(output),
    )

    assert r.returncode == 0, f"stderr: {r.stderr}\nstdout: {r.stdout}"
    # run_tts.py writes to output_dir/file_prefix.format, find the actual file
    actual = _find_audio(output, tmp_path)
    assert actual is not None, f"No wav found in {tmp_path}\nstdout: {r.stdout}"

    data, sr = sf.read(str(actual))
    assert sr > 0
    assert len(data) > 0


@pytest.mark.slow
def test_voice_design_generates_wav(tmp_path):
    output = tmp_path / "designed.wav"
    r = run_script(
        "run_tts.py", "voice-design",
        "--text", "Welcome to the show.",
        "--instruct", "warm female narrator",
        "--language", "English",
        "--output", str(output),
    )

    assert r.returncode == 0, f"stderr: {r.stderr}\nstdout: {r.stdout}"
    actual = _find_audio(output, tmp_path)
    assert actual is not None, f"No wav found in {tmp_path}\nstdout: {r.stdout}"

    data, sr = sf.read(str(actual))
    assert sr > 0
    assert len(data) > 0


def _find_audio(expected_path: Path, search_dir: Path):
    """Find the actual output file - run_tts.py may write to a different name."""
    if expected_path.exists():
        return expected_path
    for wav in search_dir.rglob("*.wav"):
        return wav
    return None
