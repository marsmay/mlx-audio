# 字幕格式说明

## 概述

mlx-audio 支持多种字幕和转写格式，通过 `writers.py` 模块导出。

---

## 格式对比

| 格式 | 扩展名 | 时间戳 | 用途 |
|------|--------|--------|------|
| SRT | .srt | 毫秒 | 通用字幕 (视频) |
| VTT | .vtt | 毫秒 | Web 视频 |
| TXT | .txt | 无 | 纯文本阅读 |
| JSON | .json | 词级 | 程序处理/数据分析 |

---

## SRT 格式 (SubRip)

### 特点
- 最通用的字幕格式
- 几乎所有视频播放器支持
- 包含精确时间戳

### 格式示例

```srt
1
00:00:01,000 --> 00:00:04,500
欢迎收听我们的播客

2
00:00:05,000 --> 00:00:08,200
今天我们邀请到一位特别的嘉宾

3
00:00:09,000 --> 00:00:12,300
让我们欢迎...
```

### 时间戳格式
```
HH:MM:SS,mmm --> HH:MM:SS,mmm
```
- 使用逗号 `,` 分隔秒和毫秒
- 小时:分钟:秒

### 使用方法

```python
from mlx_audio.stt.models.whisper.writers import get_writer

writer = get_writer("srt", output_dir="./")
writer(result, "subtitle")
# 生成: ./subtitle.srt
```

---

## VTT 格式 (WebVTT)

### 特点
- Web 标准字幕格式
- HTML5 video 标签原生支持
- 支持 CSS 样式

### 格式示例

```vtt
WEBVTT

00:00:01.000 --> 00:00:04.500
欢迎收听我们的播客

00:00:05.000 --> 00:00:08.200
今天我们邀请到一位特别的嘉宾

NOTE
这是一个注释
```

### 时间戳格式
```
HH:MM:SS.mmm --> HH:MM:SS.mmm
```
- 使用点号 `.` 分隔秒和毫秒
- 小时:分钟:秒

### 使用方法

```python
writer = get_writer("vtt", output_dir="./")
writer(result, "subtitle")
# 生成: ./subtitle.vtt
```

---

## TXT 格式 (纯文本)

### 特点
- 无时间信息
- 适合阅读和搜索
- 文件最小

### 格式示例

```
欢迎收听我们的播客
今天我们邀请到一位特别的嘉宾
让我们欢迎...
```

### 使用方法

```python
writer = get_writer("txt", output_dir="./")
writer(result, "transcript")
# 生成: ./transcript.txt
```

---

## JSON 格式 (完整元数据)

### 特点
- 包含所有可用信息
- 词级时间戳
- 程序友好

### 格式示例

```json
{
  "text": "欢迎收听我们的播客。今天我们邀请到一位特别的嘉宾。",
  "segments": [
    {
      "start": 1.0,
      "end": 4.5,
      "text": "欢迎收听我们的播客",
      "words": [
        {
          "word": "欢迎",
          "start": 1.0,
          "end": 1.5,
          "probability": 0.95
        },
        {
          "word": "收听",
          "start": 1.5,
          "end": 2.0,
          "probability": 0.92
        }
      ]
    }
  ],
  "language": "zh",
  "generation_tokens": 50,
  "total_time": 2.5
}
```

### 使用方法

```python
writer = get_writer("json", output_dir="./")
writer(result, "metadata")
# 生成: ./metadata.json
```

---

## 时间戳格式化函数

```python
from mlx_audio.stt.models.whisper.writers import format_timestamp

# SRT 格式 (逗号)
timestamp = format_timestamp(83.456, False)
# 返回: "00:01:23,456"

# VTT 格式 (点号)
timestamp = format_timestamp(83.456, True)
# 返回: "00:01:23.456"

# 始终显示小时
timestamp = format_timestamp(5.5, False, always_include_hours=True)
# 返回: "00:00:05,500"
```

---

## 自定义 Writer

### Writer 类列表

```python
from mlx_audio.stt.models.whisper.writers import (
    WriteSRT,
    WriteVTT,
    WriteTXT,
    WriteJSON,
    get_writer
)

# 方式 1: 使用 get_writer
writer = get_writer("srt", output_dir="./")

# 方式 2: 直接实例化
writer = WriteSRT(output_dir="./")
writer = WriteVTT(output_dir="./")
writer = WriteTXT(output_dir="./")
writer = WriteJSON(output_dir="./")
```

### 实现自定义 Writer

```python
from mlx_audio.stt.models.whisper.writers import Writer

class WriteCustom(Writer):
    def write_result(self, result, output_filename):
        with open(f"{output_filename}.txt", "w", encoding="utf-8") as f:
            for segment in result.segments:
                f.write(f"[{segment['start']}] {segment['text']}\n")
```

---

## 工具函数

### 获取 Writer

```python
from mlx_audio.stt.models.whisper.writers import get_writer

writer = get_writer(format="srt", output_dir="./output/")
```

### 格式化时间戳

```python
from mlx_audio.stt.models.whisper.writers import format_timestamp

# SRT 格式
ts = format_timestamp(seconds=3723.456, vtt=False)
# "01:02:03,456"

# VTT 格式
ts = format_timestamp(seconds=3723.456, vtt=True)
# "01:02:03.456"
```

---

## CLI 导出示例

```bash
# 导出 SRT
mlx_audio.stt.generate \
  --model mlx-community/whisper-large-v3-turbo \
  --audio audio.wav \
  --format srt \
  --output-path subtitles/

# 导出 VTT
mlx_audio.stt.generate \
  --model mlx-community/whisper-large-v3-turbo \
  --audio audio.wav \
  --format vtt \
  --output-path subtitles/

# 导出 JSON (含词级时间戳)
mlx_audio.stt.generate \
  --model mlx-community/whisper-large-v3-turbo \
  --audio audio.wav \
  --format json \
  --output-path metadata/ \
  --gen-kwargs '{"word_timestamps": true}'
```
