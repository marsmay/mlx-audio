---
name: mlx-audio
description: >
  Apple Silicon local audio processing skill using MLX framework. Features: (1) Qwen3-TTS speech synthesis - voice cloning from reference audio, preset voices (Serena/Ryan), voice design from text description. (2) Whisper speech transcription - timeline subtitles (SRT/VTT/TXT/JSON), word-level timestamps, streaming. (3) Offline operation, no network required, 99+ languages supported.
triggers:
  - "text to speech"
  - "speech synthesis"
  - "voice clone"
  - "voice design"
  - "custom voice"
  - "qwen3 tts"
  - "speech to text"
  - "speech transcription"
  - "transcribe audio"
  - "subtitle"
  - "SRT subtitle"
  - "VTT subtitle"
  - "offline voice synthesis"
  - "speech to text"
  - "subtitle generation"
---

# MLX-Audio: Local TTS & STT

Apple MLX-based local speech synthesis and transcription, supporting Qwen3-TTS and Whisper models.

## Requirements

- Apple Silicon Mac (M1/M2/M3/M4)
- Python 3.9+ (macOS system python3 is 3.9 or 3.10+)
- Dependencies:
  ```bash
  pip install mlx-audio soundfile sounddevice
  brew install ffmpeg
  ```

**⚠️ Python 3.9 Compatibility**: If you get `TypeError: unsupported operand type(s) for |:`, your macOS python3 version is too old. Use Homebrew python3 3.14+ instead:
  ```bash
  brew install python@3.14
  # Then reinstall mlx-audio with the new python:
  pip install mlx-audio --force-reinstall
  ```

## TTS: Qwen3-TTS Speech Synthesis

### Available Models (Quantized for Quality)

| Model | Use Case | Memory | Model ID |
|-------|----------|--------|---------|
| Base | Voice Clone | ~4GB | `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16` |
| CustomVoice | Preset Voices | ~5GB | `mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16` |
| VoiceDesign | Voice Design | ~5GB | `mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16` |

### Preset Voices (CustomVoice)

| Voice | Language | Characteristics |
|-------|----------|-----------------|
| Vivian | Chinese | Female, bright, young |
| Serena | Chinese | Female, gentle, soft |
| Uncle_Fu | Chinese | Male, authoritative |
| Ryan | English | Male, energetic |
| Aiden | English | Male, clear, neutral |

### Voice Selection Guide

| Scenario | Recommended Voice | Reason |
|----------|-------------------|--------|
| Story narration | Vivian / Serena | Warm and engaging |
| News broadcast | Uncle_Fu | Authoritative and clear |
| Children's content | Vivian | Bright and friendly |
| Energetic promo | Ryan | Dynamic and lively |
| Documentary | Aiden | Professional and neutral |
| Detective/ mystery | Ryan + instruct | Sharp, confident |

### Performance Metrics

| Model | RTF | Peak Memory |
|-------|-----|-------------|
| CustomVoice 1.7B | ~3.4x | ~5.2GB |
| VoiceDesign 1.7B | ~4.5x | ~5.2GB |
| Base 0.6B | ~3.2x | ~3.5GB |

*RTF = Real-Time Factor (3.4x means 1 second of audio processes in 0.29s)

### Usage

#### 1. Voice Clone

```python
from mlx_audio.tts.generate import generate_audio

generate_audio(
    text="Text to synthesize",
    model="mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16",
    ref_audio="reference.wav",
    ref_text="Reference transcript",
    lang_code="zh",
    temperature=0.7,
    output_path="./",
    file_prefix="output",
)
```

#### 2. Preset Voice

```python
from mlx_audio.tts.generate import generate_audio

generate_audio(
    text="Hello from Sesame.",
    model="mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16",
    voice="Serena",
    instruct="warm and friendly",
    lang_code="en",
    temperature=0.7,
    speed=1.0,
    output_path="./",
    file_prefix="output",
)
```

#### 3. Voice Design

```python
generate_audio(
    text="Welcome to our podcast.",
    model="mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16",
    instruct="warm, mature male narrator with low pitch and slight gravel",
    lang_code="en",
    temperature=0.7,
    speed=1.0,
    output_path="./",
    file_prefix="output",
)
```

#### 4. Streaming Output

```python
for chunk in model.generate(text="Long text...", stream=True):
    if chunk.audio is not None:
        # Process audio chunk
        pass
```

### TTS CLI

```bash
# Voice Clone
python scripts/run_tts.py voice-clone \
  --text "The truth is always one" \
  --ref_audio reference.wav \
  --ref_text "Reference transcript" \
  --language English \
  --output output.wav

# Preset Voice
python scripts/run_tts.py custom-voice \
  --text "The truth is always one" \
  --voice Ryan \
  --language English \
  --temperature 0.7 \
  --speed 1.0 \
  --instruct "sharp and confident" \
  --output output.wav

# Voice Design
python scripts/run_tts.py voice-design \
  --text "Welcome to our podcast" \
  --instruct "professional female news anchor" \
  --language English \
  --temperature 0.7 \
  --output output.wav
```

---

## STT: Whisper Speech Transcription

### Available Models

| Model | Use Case | Memory | Speed | Quality |
|-------|----------|--------|-------|---------|
| whisper-large-v3-turbo-asr-fp16 | General transcription | ~3GB | Medium | High |


### Usage

#### 1. Basic Transcription

```python
from mlx_audio.stt import load

model = load("mlx-community/whisper-large-v3-turbo-asr-fp16")
result = model.generate("audio.wav")

print(result.text)
```

#### 2. Transcription with Timestamps

```python
result = model.generate("audio.wav", word_timestamps=True)

for segment in result.segments:
    print(f"[{segment['start']:.2f}s -> {segment['end']:.2f}s] {segment['text']}")
```

#### 3. Word-level Timestamps

```python
result = model.generate("audio.wav", word_timestamps=True)

for segment in result.segments:
    for word in segment.get("words", []):
        print(f"[{word['start']:.2f}s -> {word['end']:.2f}s] {word['word']} (p={word['probability']:.3f})")
```

#### 4. Export Subtitles

```python
from mlx_audio.stt.models.whisper.writers import get_writer

model = load("mlx-community/whisper-large-v3-turbo-asr-fp16")
result = model.generate("audio.wav", word_timestamps=True)

# Export SRT subtitles
writer = get_writer("srt", output_dir="./output/")
writer(result, "subtitle")

# Export VTT (Web compatible)
writer = get_writer("vtt", output_dir="./output/")
writer(result, "subtitle")

# Export plain text
writer = get_writer("txt", output_dir="./output/")
writer(result, "transcript")

# Export JSON (full metadata)
writer = get_writer("json", output_dir="./output/")
writer(result, "metadata")
```

#### 5. Language Specification

```python
# Specify Chinese transcription
result = model.generate("audio.wav", language="zh")

# Translate to English
result = model.generate("audio.wav", language="ja", task="translate")
```

#### 6. Streaming Transcription

```python
for text in model.generate_streaming(
    "audio.wav",
    chunk_duration=1.0,
    frame_threshold=25,
    language="en",
):
    marker = "[FINAL]" if text.is_final else "[partial]"
    print(f"{marker} {text.text}", end="", flush=True)
```

### STT CLI

```bash
# Basic transcription
python scripts/run_stt.py transcribe \
  --audio input.wav \
  --output transcript.txt

# Generate SRT subtitles
python scripts/run_stt.py transcribe \
  --audio input.wav \
  --format srt \
  --output subtitles/

# Generate VTT subtitles
python scripts/run_stt.py transcribe \
  --audio input.wav \
  --format vtt \
  --output subtitles/

# Specify language
python scripts/run_stt.py transcribe \
  --audio input.wav \
  --language zh \
  --format json \
  --output metadata/

# Word timestamps
python scripts/run_stt.py word-timestamps \
  --audio input.wav \
  --json timeline.json
```

---

## Subtitle Formats

| Format | Extension | Features |
|--------|----------|----------|
| SRT | .srt | SubRip format, universal |
| VTT | .vtt | WebVTT format, web compatible |
| TXT | .txt | Plain text, no timestamps |
| JSON | .json | Full metadata with word timestamps |

---

## Troubleshooting

| Issue | Solution |
|-------|---------|
| TTS slow | Use bf16 models, ensure enough memory |
| STT inaccurate | Use larger model, provide language hint |
| Subtitle timestamps off | Use `--word-timestamps` for word-level alignment |
| Audio format not supported | Convert: `ffmpeg -i input.mp3 -ar 16000 -ac 1 output.wav` |
| Out of memory | Close other apps, use smaller models |
| `TypeError: unsupported operand type(s) for |` | Python version too old — use `~/Homebrew/bin/python3` (3.14) instead of system python3 (3.9) |
| `ModuleNotFoundError: No module named 'soundfile'/'sounddevice'` | Extra deps not bundled — install: `pip install soundfile sounddevice` |

---

## Reference Documents

- [TTS Model Details](./references/tts_models.md)
- [STT Model Details](./references/stt_models.md)
- [Subtitle Format Guide](./references/subtitle_formats.md)

---

## Credits

This skill is powered by **[Blaizzy/mlx-audio](https://github.com/Blaizzy/mlx-audio)**, an Apple MLX-based speech synthesis and transcription library.

### Key Features
- **Qwen3-TTS**: State-of-the-art text-to-speech with voice cloning, preset voices, and voice design
- **Whisper**: OpenAI's speech recognition for accurate transcription in 99+ languages
- **Apple Silicon Optimized**: Efficient inference on M1/M2/M3/M4 chips via MLX framework

### Official Resources
- GitHub: https://github.com/Blaizzy/mlx-audio
- Documentation: https://github.com/Blaizzy/mlx-audio#readme

### Supported Models
- TTS: Qwen3-TTS (Base, CustomVoice, VoiceDesign)
- STT: Whisper (large-v3-turbo)
