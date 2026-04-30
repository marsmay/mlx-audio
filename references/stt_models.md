# STT 模型参考

## Whisper 模型系列

OpenAI Whisper 语音识别模型在 Apple MLX 上的实现。

---

## 模型列表

### Whisper Large V3 Turbo

| 模型 ID | 内存 | 参数量 | 用途 |
|---------|------|--------|------|
| `mlx-community/whisper-large-v3-turbo-asr-fp16` | ~3GB | 809M | 通用转写 |

**特点**:
- 支持 99+ 语言
- 高精度转写
- 词级时间戳支持
- 流式转写支持

**示例**:
```python
from mlx_audio.stt import load

model = load("mlx-community/whisper-large-v3-turbo-asr-fp16")
result = model.generate("audio.wav", language=None)  # 自动检测语言
print(result.text)
```

---

## 语言支持

### 完整支持语言 (99+)

| 语言 | 代码 | 语言 | 代码 |
|------|------|------|------|
| English | en | Chinese | zh |
| Japanese | ja | Korean | ko |
| French | fr | German | de |
| Spanish | es | Italian | it |
| Portuguese | pt | Russian | ru |
| Arabic | ar | Hindi | hi |
| ... | ... | ... | ... |

**语言代码示例**:
```python
# 指定语言
result = model.generate("audio.wav", language="zh")

# 自动检测 (默认)
result = model.generate("audio.wav", language=None)

# 翻译模式
result = model.generate("audio.wav", language="ja", task="translate")
```

---

## 生成参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `language` | str | None | 语言代码 (None=自动检测) |
| `task` | str | "transcribe" | 转写模式 ("transcribe" 或 "translate") |
| `return_timestamps` | bool | True | 返回时间戳 |
| `word_timestamps` | bool | False | 词级时间戳 |
| `temperature` | float | 0.0 | 采样温度 (0=贪婪, >0=采样) |
| `prompt` | str | None | 上下文提示 |
| `context` | str | None | 热词/元数据 |

---

## 时间戳格式

### 段级时间戳

```python
result = model.generate("audio.wav")

for segment in result.segments:
    start = segment["start"]  # 秒
    end = segment["end"]      # 秒
    text = segment["text"]
    print(f"[{start:.2f}s -> {end:.2f}s] {text}")
```

### 词级时间戳

```python
result = model.generate("audio.wav", word_timestamps=True)

for segment in result.segments:
    for word in segment.get("words", []):
        start = word["start"]
        end = word["end"]
        word_text = word["word"]
        prob = word["probability"]  # 置信度
        print(f"[{start:.2f}s -> {end:.2f}s] {word_text} (p={prob:.2f})")
```

---

## 流式转写

```python
model = load("mlx-community/whisper-large-v3-turbo-asr-fp16")

for result in model.generate_streaming(
    "audio.wav",
    chunk_duration=1.0,     # 音频块时长 (秒)
    frame_threshold=25,     # AlignAtt 阈值
    language="en",
):
    marker = "[FINAL]" if result.is_final else "[partial]"
    print(f"{marker} {result.text}", end="", flush=True)
```

---

## 模型选择指南

| 场景 | 推荐模型 | 原因 |
|------|---------|------|
| 通用转写 | Whisper Large v3 Turbo | 最高精度 |
