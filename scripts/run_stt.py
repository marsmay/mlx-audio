#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MLX-Audio STT CLI Tool

Supports Whisper speech transcription and subtitle generation:
- transcribe: Basic transcription with multiple subtitle formats (SRT/VTT/TXT/JSON)
- word-timestamps: Word-level timestamp alignment
"""

import argparse
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
os.environ.setdefault("HF_HUB_ENABLE_OFFLINE", "1")

sys.path.insert(0, str(Path(__file__).parent.parent))

from mlx_audio.stt import load
from mlx_audio.stt.models.whisper.writers import get_writer


MODEL_LARGE = "mlx-community/whisper-large-v3-turbo-asr-fp16"
SUPPORTED_FORMATS = ["srt", "vtt", "txt", "json"]
STREAM_CHUNK_DURATION = 1.0
STREAM_FRAME_THRESHOLD = 25


def stt_output_to_dict(result):
    return {
        "text": result.text,
        "segments": result.segments,
        "language": result.language,
    }


def transcribe(args):
    """Transcription mode"""
    model_id = args.model or MODEL_LARGE
    print(f"[*] Loading model: {model_id}")

    model = load(model_id)

    print(f"[*] Input audio: {args.audio}")
    print(f"[*] Word timestamps: {args.word_timestamps}")

    # Execute transcription
    result = model.generate(
        args.audio,
        language=args.language,
        word_timestamps=args.word_timestamps,
        task="transcribe" if not args.translate else "translate"
    )

    # Convert to dict for writers
    result_dict = stt_output_to_dict(result)

    # Streaming output
    if args.stream:
        print("[*] Streaming mode...")
        for chunk in model.generate_streaming(
            args.audio,
            language=args.language,
            chunk_duration=STREAM_CHUNK_DURATION,
            frame_threshold=STREAM_FRAME_THRESHOLD
        ):
            marker = "[FINAL]" if chunk.is_final else "[partial]"
            print(f"{marker} {chunk.text}", end="", flush=True)
        print()
        return

    # Export subtitles if format specified
    if args.format:
        format_lower = args.format.lower()
        if format_lower not in SUPPORTED_FORMATS:
            print(f"[!] Unsupported format: {format_lower}, available: {', '.join(SUPPORTED_FORMATS)}")
            sys.exit(1)

        print(f"[*] Export format: {format_lower.upper()}")

        # Ensure output directory exists
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        writer = get_writer(format_lower, str(output_dir))
        filename = args.filename or "output"
        writer(result_dict, filename)

        output_path = output_dir / f"{filename}.{format_lower}"
        print(f"[+] Saved to: {output_path}")
    else:
        # Print transcription result
        print("\n" + "=" * 50)
        print("Transcription Result:")
        print("=" * 50)
        print(result.text)

        # Print timestamps if available
        if hasattr(result, 'segments') and result.segments:
            print("\n" + "=" * 50)
            print("Timestamps:")
            print("=" * 50)
            for seg in result.segments:
                print(f"[{seg['start']:.2f}s -> {seg['end']:.2f}s] {seg['text']}")

    # Save to file
    if args.save:
        save_path = Path(args.save)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(result.text)
        print(f"[+] Text saved to: {save_path}")


def word_timestamps(args):
    """Word-level timestamp mode"""
    print(f"[*] Loading model: {MODEL_LARGE}")
    model = load(MODEL_LARGE)

    print(f"[*] Input audio: {args.audio}")
    print(f"[*] Language: {args.language or 'auto'}")

    result = model.generate(
        args.audio,
        language=args.language,
        word_timestamps=True,
    )

    print("\n" + "=" * 50)
    print("Word-level Timestamps:")
    print("=" * 50)

    for segment in result.segments:
        for word in segment.get("words", []):
            prob = word.get("probability", 0)
            print(f"[{word['start']:.3f}s -> {word['end']:.3f}s] {word['word']} (p={prob:.2f})")

    # Export to JSON
    if args.json:
        output = {
            "text": result.text,
            "segments": result.segments,
            "language": result.language,
        }
        json_path = Path(args.json)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"\n[+] JSON saved to: {json_path}")


def main():
    parser = argparse.ArgumentParser(
        description="MLX-Audio STT CLI - Whisper Speech Transcription",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic transcription
  %(prog)s transcribe --audio input.wav

  # Generate SRT subtitles
  %(prog)s transcribe --audio input.wav --format srt --output ./subtitles/

  # Generate VTT subtitles (Web)
  %(prog)s transcribe --audio input.wav --format vtt --output ./subtitles/

  # Word timestamps
  %(prog)s word-timestamps --audio input.wav --json timeline.json

  # Specify language
  %(prog)s transcribe --audio input.wav --language zh --format json --output ./

  # Translate mode
  %(prog)s transcribe --audio input.wav --translate --format srt --output ./

Supported formats: {formats}
        """.format(formats=", ".join(SUPPORTED_FORMATS))
    )

    subparsers = parser.add_subparsers(dest="mode", help="Transcription mode")

    # Transcribe subcommand
    trans_parser = subparsers.add_parser("transcribe", help="Speech transcription")
    trans_parser.add_argument("--audio", required=True, help="Input audio file path")
    trans_parser.add_argument("--format", help=f"Output format ({', '.join(SUPPORTED_FORMATS)})")
    trans_parser.add_argument("--output", default="./", help="Output directory (default: ./)")
    trans_parser.add_argument("--filename", help="Output filename (without extension)")
    trans_parser.add_argument("--language", help="Language code (e.g., en, zh, ja)")
    trans_parser.add_argument("--word_timestamps", action="store_true", help="Include word-level timestamps")
    trans_parser.add_argument("--translate", action="store_true", help="Translate to English")
    trans_parser.add_argument("--model", help="Model ID")
    trans_parser.add_argument("--stream", action="store_true", help="Streaming transcription")
    trans_parser.add_argument("--save", help="Save plain text to specified file")

    # Word Timestamps subcommand
    ts_parser = subparsers.add_parser("word-timestamps", help="Word-level timestamp alignment")
    ts_parser.add_argument("--audio", required=True, help="Input audio file path")
    ts_parser.add_argument("--text", help="Reference text (for alignment)")
    ts_parser.add_argument("--language", help="Language code")
    ts_parser.add_argument("--json", help="Export JSON to specified file")

    args = parser.parse_args()

    if args.mode is None:
        parser.print_help()
        sys.exit(1)

    if args.mode == "transcribe":
        transcribe(args)
    elif args.mode == "word-timestamps":
        word_timestamps(args)


if __name__ == "__main__":
    main()
