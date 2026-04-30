# MLX-Audio

Apple Silicon 本地语音合成 (TTS) 与转写 (STT) 工具集，基于 [MLX](https://github.com/ml-explore/mlx) 框架，使用 [Qwen3-TTS](https://huggingface.co/collections/mlx-community/qwen3-tts-67f7e0c5e06c3f5e8e2c5b3a) 和 [Whisper](https://huggingface.co/mlx-community/whisper-large-v3-turbo-asr-fp16) 模型。完全离线运行，无需网络连接。

## 功能

- **语音合成 (TTS)** — 三种模式：音色克隆、预设音色、文字描述设计音色
- **语音转写 (STT)** — 支持 99+ 语言，输出 SRT/VTT/TXT/JSON 字幕，词级时间戳
- **批量配音** — 多段文本分段合成、多说话人切换、自动合并输出

## 环境要求

| 项目 | 要求 |
|------|------|
| **硬件** | Apple Silicon Mac (M1 / M2 / M3 / M4) |
| **系统** | macOS 13+ (Ventura 及以上) |
| **Python** | 3.11+（macOS 自带 `/usr/bin/python3` 为 3.9，需 `brew install python@3.14` 安装新版） |
| **内存** | 8 GB 起步（推荐 16 GB+，详见[硬件参考](#硬件资源参考)） |
| **磁盘** | 首次运行自动下载模型，约 1-4 GB/模型 |
| **网络** | 仅首次下载模型需要，后续完全离线 |

> **重要：** Intel Mac 无法使用 MLX 框架。本工具仅支持 Apple Silicon (M 系列芯片)。

## 安装

```bash
# Python 依赖
pip install mlx-audio soundfile numpy

# 音频格式支持（可选，处理 mp3/m4a 等格式时需要）
brew install ffmpeg
```

## 快速开始

### TTS — 语音合成

```bash
# 预设音色（Serena / Ryan / Aiden / Vivian / Uncle_Fu）
python3 scripts/run_tts.py custom-voice \
  --text "Hello, welcome to MLX-Audio." \
  --voice Serena --language English --output output.wav

# 音色克隆（需要提供参考音频 + 参考文本）
python3 scripts/run_tts.py voice-clone \
  --text "这是克隆后的语音。" \
  --ref_audio speaker.wav --ref_text "这是参考音频说的内容" \
  --language Chinese --output clone.wav

# 音色设计（用文字描述想要的音色）
python3 scripts/run_tts.py voice-design \
  --text "Welcome to our podcast." \
  --instruct "warm, mature male narrator with a slight British accent" \
  --language English --output design.wav
```

### STT — 语音转写

```bash
# 基本转写
python3 scripts/run_stt.py transcribe --audio input.wav

# 导出 SRT 字幕
python3 scripts/run_stt.py transcribe --audio input.wav \
  --format srt --output ./subtitles/

# 词级时间戳 → JSON
python3 scripts/run_stt.py word-timestamps --audio input.wav --json timeline.json
```

### 批量配音

```bash
# 创建配置文件
cat > dubbing.json << 'EOF'
{
  "model": "custom-voice",
  "voice": "Serena",
  "language": "English",
  "segments": [
    {"id": 1, "text": "First segment.", "speaker": "Serena"},
    {"id": 2, "text": "Second segment.", "speaker": "Ryan"}
  ]
}
EOF

# 执行
python3 scripts/batch_dubbing.py --config dubbing.json --output ./output/
```

输出目录结构：
```
output/
├── individual/
│   ├── segment_0001.wav
│   └── segment_0002.wav
├── combined.wav          # 合并音频（含静音间隔）
└── manifest.json         # 处理清单
```

## 模型配置

脚本中默认使用 bf16（无损精度）模型。如果你的 Mac 内存有限，可以切换到量化版本以降低内存占用。

### 修改默认模型

在对应脚本中找到模型映射字典，替换模型 ID 即可：

```python
# scripts/run_tts.py — 修改 DEFAULT_MODELS
DEFAULT_MODELS = {
    "voice-clone": "mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit",      # bf16 → 4bit
    "custom-voice": "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-4bit",
    "voice-design": "mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-4bit",
}

# scripts/batch_dubbing.py — 修改 MODEL_MAP
MODEL_MAP = {
    "base": "mlx-community/Qwen3-TTS-12Hz-0.6B-Base-4bit",
    "custom-voice": "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-4bit",
    "voice-design": "mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-4bit",
}

# scripts/run_stt.py — 修改 MODEL_LARGE
MODEL_LARGE = "mlx-community/whisper-large-v3-turbo-asr-4bit"  # fp16 → 4bit
```

也可以通过命令行参数临时指定：

```bash
python3 scripts/run_tts.py custom-voice \
  --text "Hello" --voice Serena \
  --model "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-4bit" \
  --output output.wav

python3 scripts/run_stt.py transcribe \
  --audio input.wav \
  --model "mlx-community/whisper-large-v3-turbo-asr-4bit"
```

## 硬件资源参考

根据你的 Mac 内存选择合适的量化等级。建议模型 RAM + 系统开销 ≤ 可用内存的 70%。

### TTS — Qwen3-TTS

#### 0.6B 参数（音色克隆）

| 量化 | 模型 ID 后缀 | 磁盘 | 最低 RAM | 推荐芯片 |
|------|-------------|------|----------|---------|
| **bf16** | `0.6B-Base-bf16` | 1.8 GB | ~4 GB | M1+ |
| 8-bit | `0.6B-Base-8bit` | 1.3 GB | ~3 GB | M1 |
| 6-bit | `0.6B-Base-6bit` | 1.2 GB | ~2.5 GB | M1 |
| 4-bit | `0.6B-Base-4bit` | 1.0 GB | ~2 GB | M1 |

#### 1.7B 参数（预设音色 / 音色设计）

| 量化 | 模型 ID 后缀 | 磁盘 | 最低 RAM | 推荐芯片 |
|------|-------------|------|----------|---------|
| **bf16** | `1.7B-CustomVoice-bf16` | 3.9 GB | ~8 GB | M2 Pro+ |
| 8-bit | `1.7B-CustomVoice-8bit` | 2.4 GB | ~5 GB | M1 Pro+ |
| 6-bit | `1.7B-CustomVoice-6bit` | 2.0 GB | ~4 GB | M1+ |
| 4-bit | `1.7B-CustomVoice-4bit` | 1.7 GB | ~3.5 GB | M1 |

> **VoiceDesign** 和 **Base** 的 1.7B 变体资源需求与 CustomVoice 相同，替换模型 ID 中的 `CustomVoice` 为 `VoiceDesign` 或 `Base` 即可。

### STT — Whisper

| 量化 | 模型 ID 后缀 | 磁盘 | 最低 RAM | 推荐芯片 |
|------|-------------|------|----------|---------|
| **fp16** | `whisper-large-v3-turbo-asr-fp16` | 1.6 GB | ~3 GB | M1+ |
| 8-bit | `whisper-large-v3-turbo-asr-8bit` | 0.9 GB | ~2 GB | M1 |
| 4-bit | `whisper-large-v3-turbo-asr-4bit` | 0.5 GB | ~1 GB | M1 |

### 按芯片推荐配置

| 芯片 | 统一内存 | TTS 推荐 | STT 推荐 |
|------|---------|---------|---------|
| M1 (基础款 8 GB) | 8 GB | 0.6B-Base + 1.7B 4-bit | fp16 |
| M1 Pro / Max (16 GB+) | 16 GB | 全部 bf16 | fp16 |
| M2 (8 GB) | 8 GB | 1.7B 4-bit | fp16 |
| M2 Pro / Max (16 GB+) | 16 GB | 全部 bf16 | fp16 |
| M3 / M4 (8 GB) | 8 GB | 1.7B 4-bit | fp16 |
| M3 Pro / M4 Pro (18 GB+) | 18 GB+ | 全部 bf16 | fp16 |
| M3 Max / M4 Max (36 GB+) | 36 GB+ | 全部 bf16 | fp16 |

> **粗体**为脚本默认值。量化精度越高语音质量越好，4-bit 在大多数场景下仍可接受。

## 预设音色

| 音色 | 语言 | 性别 | 风格 |
|------|------|------|------|
| Serena | 中文 | 女 | 温柔柔和 |
| Vivian | 中文 | 女 | 明亮年轻 |
| Uncle_Fu | 中文 | 男 | 权威成熟 |
| Ryan | 英文 | 男 | 活力清晰 |
| Aiden | 英文 | 男 | 中性专业 |

可通过 `--instruct` 参数叠加风格指令：

```bash
python3 scripts/run_tts.py custom-voice \
  --text "Welcome everyone." --voice Ryan \
  --instruct "serious and professional" \
  --language English --output output.wav
```

## 支持语言

```
auto（自动检测） Chinese  English  Japanese  Korean
French  German  Italian  Spanish  Portuguese  Russian
```

## 命令行参数

### run_tts.py

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--text` | (必填) | 要合成的文本 |
| `--voice` | Serena | 预设音色名称 |
| `--language` | auto | 语言 |
| `--temperature` | 0.7 | 采样温度 |
| `--speed` | 1.0 | 语速倍率 |
| `--output` | 自动 | 输出文件路径 |
| `--model` | 默认 | 自定义模型 ID |
| `--ref_audio` | — | 参考音频（voice-clone 必填） |
| `--ref_text` | — | 参考文本（voice-clone 必填） |
| `--instruct` | — | 音色描述（voice-design 必填） |

### run_stt.py

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--audio` | (必填) | 输入音频文件 |
| `--format` | — | 输出格式：srt / vtt / txt / json |
| `--output` | ./ | 输出目录 |
| `--language` | 自动 | 语言代码（en, zh, ja...） |
| `--word_timestamps` | false | 启用词级时间戳 |
| `--translate` | false | 翻译为英文 |
| `--stream` | false | 流式转写 |
| `--save` | — | 保存纯文本到指定文件 |

### batch_dubbing.py

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--config` | (必填) | 批量配置文件 (JSON) |
| `--output` | ./batch_output | 输出目录 |
| `--silence-gap` | 0.3s | 同说话人片段间隔 |
| `--character-switch-gap` | 0.5s | 不同说话人片段间隔 |

## 项目结构

```
├── scripts/
│   ├── run_tts.py          # TTS CLI（voice-clone / custom-voice / voice-design）
│   ├── run_stt.py          # STT CLI（transcribe / word-timestamps）
│   └── batch_dubbing.py    # 批量配音
├── references/
│   ├── tts_models.md       # TTS 模型详细参考
│   ├── stt_models.md       # STT 模型详细参考
│   └── subtitle_formats.md # 字幕格式规范
├── tests/                  # 功能测试
│   ├── test_tts_functional.py
│   ├── test_stt_functional.py
│   └── test_batch_functional.py
├── CLAUDE.md               # Claude Code 项目指引
└── SKILL.md                # Claude Code Skill 定义
```

## 许可

本项目仅供学习和个人使用。模型权重遵循各自的原作者许可协议。
