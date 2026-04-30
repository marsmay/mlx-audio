# TTS 模型参考

## Qwen3-TTS 模型系列

基于 Qwen3 的文本转语音模型，支持语音合成、音色克隆和音色设计。

---

## 模型列表

### 1. Base 模型 (音色克隆)

| 模型 ID | 内存 | 量化 | 用途 |
|---------|------|------|------|
| `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16` | ~4GB | bf16 | 音色克隆 |

**API**: `model.generate(text, ref_audio, ref_text)`

**示例**:
```python
model = load_model("mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16")
results = list(model.generate(
    text="要合成的文本",
    ref_audio="speaker.wav",
    ref_text="这是参考音频说的内容"
))
```

---

### 2. CustomVoice 模型 (预设音色)

| 模型 ID | 内存 | 量化 | 用途 |
|---------|------|------|------|
| `mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16` | ~5GB | bf16 | 预设音色 |

**API**: `model.generate_custom_voice(text, voice, instruct?)`

**预设音色**:

| 音色 | 语言 | 性别 | 特点 |
|------|------|------|------|
| Serena | 中文 | 女 | 温柔，柔和 |
| Vivian | 中文 | 女 | 明亮，年轻 |
| Uncle_Fu | 中文 | 男 | 权威，成熟 |
| Ryan | 英文 | 男 | 活力，清晰 |
| Aiden | 英文 | 男 | 中性，专业 |

**示例**:
```python
model = load_model("mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-bf16")
results = list(model.generate_custom_voice(
    text="Hello world",
    voice="Serena",
    instruct="warm and friendly"  # 可选风格指令
))
```

**风格指令示例**:
- `warm and friendly` - 温暖友好
- `serious and professional` - 严肃专业
- `excited and energetic` - 兴奋活力
- `calm and relaxing` - 平静放松
- `sad and melancholic` - 悲伤忧郁

---

### 3. VoiceDesign 模型 (音色设计)

| 模型 ID | 内存 | 量化 | 用途 |
|---------|------|------|------|
| `mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16` | ~5GB | bf16 | 文本描述设计音色 |

**API**: `model.generate_voice_design(text, instruct)`

**示例**:
```python
model = load_model("mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16")
results = list(model.generate_voice_design(
    text="Welcome to our podcast",
    instruct="warm, mature male narrator with a slight British accent"
))
```

**音色描述语法**:
- 音色特征: `male`, `female`, `young`, `old`, `deep`, `high-pitched`
- 情感: `warm`, `cold`, `friendly`, `professional`, `energetic`
- 口音: `British`, `American`, `Australian`, `Chinese`, `Japanese`
- 说话风格: `casual`, `formal`, `storytelling`, `news anchor`

**音色描述示例**:
| 描述 | 效果 |
|------|------|
| `young female with a sweet voice` | 年轻女声甜美 |
| `mature male narrator with low pitch` | 成熟男声低沉 |
| `professional female news anchor` | 专业女新闻主播 |
| `friendly elderly man with warmth` | 温暖的老年男士 |
| `energetic teenage boy` | 活力少年男声 |
| `calm and soothing female voice` | 平静舒缓女声 |
| `British gentleman with distinguished accent` | 英伦绅士 |

---

## 技术参数

| 参数 | 值 |
|------|-----|
| 采样率 | 24000 Hz |
| 音频格式 | WAV (PCM) |
| Context Length | 128k tokens |
| MRoPE | 3D 位置编码 (时间, 高度, 宽度) |
| 注意力机制 | Grouped Query Attention (GQA) |
| 激活函数 | SwiGLU |

---

## 模型选择指南

| 场景 | 推荐模型 | 原因 |
|------|---------|------|
| 音色克隆 | Base bf16 | 需要参考音频才能工作 |
| 高质量合成 | CustomVoice 1.7B | 更好的情感表达 |
| 创意音色设计 | VoiceDesign 1.7B | 完全自定义音色 |

---

## 内存优化

| 策略 | 内存节省 | 质量影响 |
|------|---------|----------|
| bf16 量化 | - | 无 (原始精度) |
| 流式输出 | 减少峰值 | 无 |
