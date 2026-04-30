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


@pytest.fixture(scope="module")
def test_audio(tmp_path_factory):
    """Generate a short English audio file via TTS for STT testing."""
    out_dir = tmp_path_factory.mktemp("stt_input")
    output = out_dir / "test_audio.wav"
    r = run_script(
        "run_tts.py", "custom-voice",
        "--text", "The quick brown fox jumps over the lazy dog.",
        "--voice", "Serena",
        "--language", "English",
        "--output", str(output),
    )
    assert r.returncode == 0, f"TTS failed: {r.stderr}\n{r.stdout}"

    # Find actual output (run_tts may use different filename)
    for wav in out_dir.rglob("*.wav"):
        return wav
    pytest.skip("TTS did not produce audio file")


@pytest.mark.slow
def test_transcribe_prints_text(test_audio):
    r = run_script(
        "run_stt.py", "transcribe",
        "--audio", str(test_audio),
    )

    assert r.returncode == 0, f"stderr: {r.stderr}\nstdout: {r.stdout}"
    assert "fox" in r.stdout.lower() or "dog" in r.stdout.lower() or "lazy" in r.stdout.lower(), \
        f"Transcription output doesn't contain expected words:\n{r.stdout}"


@pytest.mark.slow
def test_transcribe_exports_srt(test_audio, tmp_path):
    r = run_script(
        "run_stt.py", "transcribe",
        "--audio", str(test_audio),
        "--format", "srt",
        "--output", str(tmp_path),
    )

    assert r.returncode == 0, f"stderr: {r.stderr}\nstdout: {r.stdout}"
    srt_files = list(tmp_path.glob("*.srt"))
    assert len(srt_files) == 1, f"Expected 1 srt file, found {srt_files}"
    content = srt_files[0].read_text()
    assert "-->" in content, "SRT file should contain timestamp markers"
