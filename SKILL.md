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
  - "subtitle generation"
  - "batch dubbing"
---

# MLX-Audio: Local TTS & STT

**Agent Skill** — Compatible with [Claude Code](https://claude.ai/code), [Codex](https://openai.com/codex), [OpenClaw](https://github.com/openclaw/openclaw), [Hermes](https://github.com/NousResearch/Hermes), and other Skill-protocol-compatible AI agents.

Apple MLX-based local speech synthesis and transcription, supporting Qwen3-TTS and Whisper models.

## Requirements

- Apple Silicon Mac (M1/M2/M3/M4)
- Python 3.11+
  - macOS 自带的 `/usr/bin/python3` 是 3.9，不满足要求
  - 安装方式：`brew install python@3.14`（装完后 `python3 --version` 应 ≥ 3.11）
- Dependencies:
  ```bash
  pip install mlx-audio soundfile numpy
  brew install ffmpeg
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
    join_audio=True,
    play=False,
)
```

#### 2. Preset Voice

```python
from mlx_audio.tts.generate import generate_audio

generate_audio(
    text="Hello from Sesame.",
    model="mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16",
    voice="Serena",
    instruct="warm and friendly",
    lang_code="en",
    temperature=0.7,
    speed=1.0,
    output_path="./",
    file_prefix="output",
    join_audio=True,
    play=False,
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
    join_audio=True,
    play=False,
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
python3 scripts/run_tts.py voice-clone \
  --text "The truth is always one" \
  --ref_audio reference.wav \
  --ref_text "Reference transcript" \
  --language English \
  --output output.wav

# Preset Voice
python3 scripts/run_tts.py custom-voice \
  --text "The truth is always one" \
  --voice Ryan \
  --language English \
  --temperature 0.7 \
  --speed 1.0 \
  --instruct "sharp and confident" \
  --output output.wav

# Voice Design
python3 scripts/run_tts.py voice-design \
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

# Convert to dict for writers
result_dict = {
    "text": result.text,
    "segments": result.segments,
    "language": result.language,
}

# Export SRT subtitles
writer = get_writer("srt", output_dir="./output/")
writer(result_dict, "subtitle")

# Export VTT (Web compatible)
writer = get_writer("vtt", output_dir="./output/")
writer(result_dict, "subtitle")

# Export plain text
writer = get_writer("txt", output_dir="./output/")
writer(result_dict, "transcript")

# Export JSON (full metadata)
writer = get_writer("json", output_dir="./output/")
writer(result_dict, "metadata")
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
# Basic transcription (save to file)
python3 scripts/run_stt.py transcribe \
  --audio input.wav \
  --save transcript.txt

# Generate SRT subtitles
python3 scripts/run_stt.py transcribe \
  --audio input.wav \
  --format srt \
  --output subtitles/

# Generate VTT subtitles
python3 scripts/run_stt.py transcribe \
  --audio input.wav \
  --format vtt \
  --output subtitles/

# Specify language
python3 scripts/run_stt.py transcribe \
  --audio input.wav \
  --language zh \
  --format json \
  --output metadata/

# Word timestamps
python3 scripts/run_stt.py word-timestamps \
  --audio input.wav \
  --json timeline.json
```

---

## Batch Dubbing

Multi-segment TTS with speaker switching and automatic merging.

### Input Config (JSON)

```json
{
  "model": "custom-voice",
  "voice": "Serena",
  "instruct": "warm and friendly",
  "language": "auto",
  "temperature": 0.7,
  "segments": [
    {"id": 1, "text": "First segment.", "speaker": "Serena"},
    {"id": 2, "text": "Second segment.", "speaker": "Ryan"}
  ]
}
```

### CLI

```bash
python3 scripts/batch_dubbing.py --config dubbing.json --output ./output/

# Custom silence gaps
python3 scripts/batch_dubbing.py --config dubbing.json --output ./output/ \
  --silence-gap 0.5 --character-switch-gap 0.8
```

### Output

```
output/
├── individual/
│   ├── segment_0001.wav
│   └── segment_0002.wav
├── combined.wav          # Merged audio with silence gaps
└── manifest.json         # Processing summary
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
| `TypeError: unsupported operand type(s) for |` | 终端 `python3 --version` 低于 3.11 — 运行 `brew install python@3.14` 安装新版 |
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
