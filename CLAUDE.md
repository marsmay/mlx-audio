# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MLX-Audio is an **agent skill** compatible with Claude Code, Codex, OpenClaw, Hermes, and other Skill-protocol agents. It provides local speech synthesis (TTS) and transcription (STT) on Apple Silicon (M1-M4) via the MLX framework. Fully offline after model download.

## Environment

- Python 3.14+ required (`~/Homebrew/bin/python3`). System python3 (3.9) will fail with `TypeError: unsupported operand type(s) for |`.
- Dependencies: `pip install mlx-audio soundfile numpy` + `brew install ffmpeg`
- MLX audio package version: 0.4.3+ (upgrade from PyPI if STT processor errors occur)

## Commands

All scripts are in `scripts/`. Use `python3` (Homebrew) not `python` (system).

### TTS (Qwen3-TTS)

```bash
python3 scripts/run_tts.py voice-clone \
  --text "Text" --ref_audio ref.wav --ref_text "Transcript" \
  --language English --output output.wav

python3 scripts/run_tts.py custom-voice \
  --text "Hello" --voice Serena --language English --output output.wav

python3 scripts/run_tts.py voice-design \
  --text "Welcome" --instruct "warm male narrator" --language English --output output.wav
```

### STT (Whisper)

```bash
python3 scripts/run_stt.py transcribe --audio input.wav
python3 scripts/run_stt.py transcribe --audio input.wav --format srt --output ./subtitles/
python3 scripts/run_stt.py word-timestamps --audio input.wav --json timeline.json
```

### Batch Dubbing

```bash
python3 scripts/batch_dubbing.py --config dubbing.json --output ./output/
```

### Tests

```bash
# Run all functional tests (requires MLX models, ~30s per test)
pytest tests/ -v

# Run a single test file
pytest tests/test_tts_functional.py -v

# Run without slow model-dependent tests
pytest tests/ -v -m "not slow"

# Skip only the batch test (takes longest, loads TTS model twice)
pytest tests/ -v -k "not batch"
```

Tests are subprocess-based — they invoke the actual CLI scripts with real MLX models, not mocked. All tests are marked `@pytest.mark.slow`.

## Architecture

Three independent CLI scripts wrapping the `mlx-audio` pip package. Each script is self-contained with its own model mapping and argparse setup — no shared modules.

| Script | Purpose | Entry Point |
|--------|---------|-------------|
| `scripts/run_tts.py` | TTS CLI with voice-clone/custom-voice/voice-design subcommands | `mlx_audio.tts.generate.generate_audio()` |
| `scripts/run_stt.py` | STT CLI with transcribe/word-timestamps subcommands | `mlx_audio.stt.load()` |
| `scripts/batch_dubbing.py` | Multi-segment TTS with audio merging and speaker switching | `mlx_audio.tts.generate.generate_audio()` + `soundfile` |

### Models

| Type | Model ID | Use Case |
|------|----------|----------|
| TTS Base | `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16` | Voice cloning (~4GB) |
| TTS CustomVoice | `mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16` | Preset voices (~5GB) |
| TTS VoiceDesign | `mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16` | Voice design from text (~5GB) |
| STT Whisper | `mlx-community/whisper-large-v3-turbo-asr-fp16` | Transcription (~3GB) |

Quantized variants (8-bit, 6-bit, 4-bit) are available on HuggingFace under `mlx-community/`. Replace `bf16`/`fp16` in the model ID suffix (e.g., `0.6B-Base-4bit`).

### Key Patterns

- **TTS mode dispatch**: `run_tts.py` has three handler functions (`voice_clone`, `custom_voice`, `voice_design`) that each call `generate_audio()` with different parameter subsets
- **STT output conversion**: `run_stt.py` converts `STTOutput` to dict via `stt_output_to_dict()` before passing to `get_writer()` — writers do not accept raw result objects
- **Language normalization**: `args.language.lower() if args.language != "auto" else "auto"` — applied in all scripts
- **Model mapping**: `DEFAULT_MODELS` in `run_tts.py` and `MODEL_MAP` in `batch_dubbing.py` use different key names for the same models (`"voice-clone"` vs `"base"`)
- **Streaming guard**: `run_stt.py` checks `args.stream` before calling `model.generate()` to avoid double GPU inference

## Reference Documents

- `references/tts_models.md` — Qwen3-TTS model details, preset voices, voice description syntax
- `references/stt_models.md` — Whisper parameters, language codes, streaming API
- `references/subtitle_formats.md` — SRT/VTT/TXT/JSON format specs and writer API
