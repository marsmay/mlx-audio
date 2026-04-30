#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MLX-Audio Batch Dubbing Tool
Optimized for Apple Silicon (M1/M2/M3/M4)

批量语音合成工具，支持多段文本分别合成并合并。

输入格式 (JSON):
{
  "model": "custom-voice",  // 或 "voice-clone", "voice-design"
  "voice": "Serena",        // 预设音色 (custom-voice 模式)
  "instruct": "warm",        // 风格指令 (可选)
  "language": "auto",       // 语言 (默认: auto)
  "temperature": 0.7,        // 温度 (默认: 0.7)
  "segments": [
    {"id": 1, "text": "第一段文本", "speaker": "Serena"},
    {"id": 2, "text": "第二段文本", "speaker": "Ryan"}
  ]
}

输出:
- individual/: 各段独立音频
- combined.wav: 合并后音频 (带静音间隔)
- manifest.json: 处理清单

Dependencies:
    pip install mlx-audio soundfile numpy
"""

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

from mlx_audio.tts.generate import generate_audio


# 模型映射 - 使用量化模型
MODEL_MAP = {
    "base": "mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16",
    "custom-voice": "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16",
    "voice-design": "mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16",
}

# 默认静音间隔配置
DEFAULT_SILENCE_GAP = 0.3      # 同说话人之间的静音 (秒)
DEFAULT_CHARACTER_SWITCH_GAP = 0.5  # 换说话人时的静音 (秒)


def configure_transformers() -> None:
    try:
        from transformers.utils import logging as hf_logging
        hf_logging.set_verbosity_error()
    except Exception:
        pass


def load_batch_config(config_path):
    """加载批量配置文件"""
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def synthesize_segment(
    text: str,
    voice: str,
    language: str,
    instruct: str,
    model: str,
    output_path: str,
    temperature: float,
):
    output_file = Path(output_path)
    out_dir = str(output_file.parent)
    file_prefix = output_file.stem
    audio_format = output_file.suffix.lstrip(".") or "wav"

    try:
        generate_audio(
            text=text,
            model=model,
            voice=voice,
            instruct=instruct,
            lang_code=language,
            temperature=temperature,
            output_path=out_dir,
            file_prefix=file_prefix,
            audio_format=audio_format,
            join_audio=True,
            play=False,
            verbose=False,
        )
        return True
    except Exception as e:
        print(f"    [!] 合成失败: {e}")
        return False


def merge_audio_with_gaps(
    segment_files: list,
    output_path: str,
    silence_gap: float = DEFAULT_SILENCE_GAP,
    character_switch_gap: float = DEFAULT_CHARACTER_SWITCH_GAP,
    speakers: list = None,
    sample_rate: int = 24000,
):
    all_audio = []
    prev_speaker = None

    for i, (_, seg_file) in enumerate(segment_files):
        # 读取音频
        audio, sr = sf.read(seg_file)
        all_audio.append(audio)

        # 确定当前说话人
        speaker = speakers[i] if speakers and i < len(speakers) else None

        # 决定静音间隔
        if prev_speaker is not None and speaker != prev_speaker:
            gap = character_switch_gap
        else:
            gap = silence_gap

        # 添加静音 (除了最后一个片段)
        if i < len(segment_files) - 1:
            silence = np.zeros(int(sample_rate * gap), dtype=np.float32)
            all_audio.append(silence)

        prev_speaker = speaker

    # 合并所有音频
    combined = np.concatenate(all_audio)
    sf.write(output_path, combined, samplerate=sample_rate)


def main():
    parser = argparse.ArgumentParser(
        description="MLX-Audio Batch Dubbing - 批量语音合成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本用法
  %(prog)s --config dubbing.json --output ./output/

  # 自定义静音间隔
  %(prog)s --config dubbing.json --output ./output/ --silence-gap 0.5 --character-switch-gap 0.8

输入 JSON 格式:
  {
    "model": "custom-voice",
    "voice": "Serena",
    "instruct": "warm and friendly",
    "language": "Chinese",
    "temperature": 0.7,
    "segments": [
      {"id": 1, "text": "第一段", "speaker": "Serena"},
      {"id": 2, "text": "第二段", "speaker": "Ryan"}
    ]
  }
        """
    )
    parser.add_argument("--config", required=True, help="批量配置文件 (JSON)")
    parser.add_argument("--output", default="./batch_output", help="输出目录")
    parser.add_argument("--silence-gap", type=float, default=DEFAULT_SILENCE_GAP, help=f"同说话人静音间隔 (秒, 默认: {DEFAULT_SILENCE_GAP})")
    parser.add_argument("--character-switch-gap", type=float, default=DEFAULT_CHARACTER_SWITCH_GAP, help=f"换说话人静音间隔 (秒, 默认: {DEFAULT_CHARACTER_SWITCH_GAP})")
    parser.add_argument("--temperature", type=float, default=0.7, help="采样温度 (默认: 0.7)")

    args = parser.parse_args()

    # 应用 transformers 配置
    configure_transformers()

    # 创建输出目录
    output_dir = Path(args.output)
    individual_dir = output_dir / "individual"
    individual_dir.mkdir(parents=True, exist_ok=True)

    # 加载配置
    print(f"[*] 加载配置: {args.config}")
    config = load_batch_config(args.config)

    mode = config.get("model", "custom-voice")
    voice = config.get("voice", "Serena")
    instruct = config.get("instruct")
    language = config.get("language", "auto")
    temperature = config.get("temperature", args.temperature)
    segments = config.get("segments", [])

    if not segments:
        print("[!] 没有找到片段配置")
        sys.exit(1)

    # 获取模型 ID
    model_id = MODEL_MAP.get(mode)
    if not model_id:
        print(f"[!] 未知模式: {mode}")
        sys.exit(1)

    print(f"[*] 模式: {mode}")
    print(f"[*] 模型: {model_id}")
    print(f"[*] 音色: {voice}")
    print(f"[*] 语言: {language}")
    print(f"[*] 温度: {temperature}")
    print(f"[*] 静音间隔: {args.silence_gap}s (同说话人), {args.character_switch_gap}s (换说话人)")

    # 合成所有片段
    segment_files = []
    speakers = []

    for i, segment in enumerate(segments):
        seg_id = segment.get("id", i)
        text = segment.get("text", "")
        speaker = segment.get("speaker", voice)

        print(f"[*] 合成片段 {seg_id}: {text[:50]}...")

        segment_path = individual_dir / f"segment_{seg_id:04d}.wav"
        success = synthesize_segment(
            text=text,
            voice=speaker,
            language=language.lower() if language != "auto" else "auto",
            instruct=instruct,
            model=model_id,
            output_path=str(segment_path),
            temperature=temperature,
        )

        if success:
            segment_files.append((seg_id, str(segment_path)))
            speakers.append(speaker)
            print(f"    -> 保存: {segment_path}")
        else:
            print(f"    [!] 跳过片段 {seg_id}")

    # 合并音频 (按 ID 排序)
    if segment_files:
        segment_files.sort(key=lambda x: x[0])
        combined_path = output_dir / "combined.wav"

        print(f"[*] 合并 {len(segment_files)} 个片段...")
        merge_audio_with_gaps(
            segment_files=segment_files,
            output_path=str(combined_path),
            silence_gap=args.silence_gap,
            character_switch_gap=args.character_switch_gap,
            speakers=speakers,
        )
        print(f"\n[+] 合并音频已保存: {combined_path}")
    else:
        print("[!] 没有成功合成的片段")

    # 保存 manifest
    manifest = {
        "mode": mode,
        "voice": voice,
        "instruct": instruct,
        "language": language,
        "temperature": temperature,
        "segments_count": len(segments),
        "succeeded_count": len(segment_files),
        "individual_dir": str(individual_dir),
        "combined_file": str(combined_path) if segment_files else None,
        "silence_gap": args.silence_gap,
        "character_switch_gap": args.character_switch_gap,
    }

    manifest_path = output_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"[+] Manifest 已保存: {manifest_path}")
    print(f"\n[*] 完成! 输出目录: {output_dir}")


if __name__ == "__main__":
    main()
