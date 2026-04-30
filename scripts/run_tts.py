#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MLX-Audio TTS CLI Tool
Optimized for Apple Silicon (M1/M2/M3/M4)

Supports three synthesis modes:
- voice-clone: Clone voice from reference audio
- custom-voice: Use preset voices (Serena, Ryan, etc.)
- voice-design: Design voice from text description

Dependencies:
    pip install mlx-audio soundfile
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

from mlx_audio.tts.generate import generate_audio


# Model IDs - bf16 for best quality
DEFAULT_MODELS = {
    "voice-clone": "mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16",
    "custom-voice": "mlx-community/Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16",
    "voice-design": "mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16",
}

# Preset voices
PRESET_VOICES = ["Serena", "Ryan", "Aiden", "Vivian", "Uncle_Fu"]

# Supported languages
LANGUAGES = [
    "auto", "Chinese", "English", "Japanese", "Korean",
    "French", "German", "Italian", "Spanish", "Portuguese", "Russian"
]


def configure_transformers() -> None:
    try:
        from transformers.utils import logging as hf_logging
        hf_logging.set_verbosity_error()
    except Exception:
        pass


def get_output_components(output: str | None, out_dir: str, prefix: str):
    """Resolve output directory, prefix and format."""
    if output:
        output_path = Path(output).expanduser()
        if output_path.is_absolute():
            out_dir_path = output_path.parent
            out_dir_path.mkdir(parents=True, exist_ok=True)
        elif output_path.parent != Path("."):
            out_dir_path = output_path.parent
            out_dir_path.mkdir(parents=True, exist_ok=True)
        else:
            out_dir_path = Path(".")

        stem = output_path.stem
        ext = output_path.suffix.lstrip(".") or "wav"
        return str(out_dir_path), stem, ext, True

    out_dir_path = Path(out_dir).expanduser()
    out_dir_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(out_dir_path), f"{prefix}_{timestamp}", "wav", False


def voice_clone(args):
    """Voice clone mode"""
    configure_transformers()

    model = args.model or DEFAULT_MODELS["voice-clone"]
    out_dir, prefix, audio_format, _ = get_output_components(
        args.output, args.out_dir, "voice_clone"
    )

    language = args.language.lower() if args.language != "auto" else "auto"

    print(f"[*] Model: {model}")
    print(f"[*] Reference audio: {args.ref_audio}")
    print(f"[*] Reference text: {args.ref_text}")
    print(f"[*] Text: {args.text}")
    print(f"[*] Language: {language}")
    print(f"[*] Temperature: {args.temperature}")
    print(f"[*] Speed: {args.speed}")

    try:
        generate_audio(
            text=args.text,
            model=model,
            voice=None,
            ref_audio=args.ref_audio,
            ref_text=args.ref_text,
            speed=args.speed,
            lang_code=language,
            temperature=args.temperature,
            output_path=out_dir,
            file_prefix=prefix,
            audio_format=audio_format,
            join_audio=True,
            play=False,
            verbose=True,
        )
        print(f"[+] Audio saved to: {Path(out_dir) / f'{prefix}.{audio_format}'}")
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)


def custom_voice(args):
    """Preset voice mode"""
    configure_transformers()

    voice = args.voice.capitalize() if args.voice else "Serena"

    if voice not in PRESET_VOICES:
        print(f"[!] Warning: {voice} not in preset list, available: {', '.join(PRESET_VOICES)}")

    model = args.model or DEFAULT_MODELS["custom-voice"]
    out_dir, prefix, audio_format, _ = get_output_components(
        args.output, args.out_dir, "custom_voice"
    )

    language = args.language.lower() if args.language != "auto" else "auto"

    print(f"[*] Model: {model}")
    print(f"[*] Voice: {voice}")
    print(f"[*] Style: {args.instruct or 'None'}")
    print(f"[*] Text: {args.text}")
    print(f"[*] Language: {language}")
    print(f"[*] Temperature: {args.temperature}")
    print(f"[*] Speed: {args.speed}")

    try:
        generate_audio(
            text=args.text,
            model=model,
            voice=voice,
            instruct=args.instruct,
            speed=args.speed,
            lang_code=language,
            temperature=args.temperature,
            output_path=out_dir,
            file_prefix=prefix,
            audio_format=audio_format,
            join_audio=True,
            play=False,
            verbose=True,
        )
        print(f"[+] Audio saved to: {Path(out_dir) / f'{prefix}.{audio_format}'}")
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)


def voice_design(args):
    """Voice design mode"""
    configure_transformers()

    model = args.model or DEFAULT_MODELS["voice-design"]
    out_dir, prefix, audio_format, _ = get_output_components(
        args.output, args.out_dir, "voice_design"
    )

    language = args.language.lower() if args.language != "auto" else "auto"

    print(f"[*] Model: {model}")
    print(f"[*] Voice description: {args.instruct}")
    print(f"[*] Text: {args.text}")
    print(f"[*] Language: {language}")
    print(f"[*] Temperature: {args.temperature}")
    print(f"[*] Speed: {args.speed}")

    try:
        generate_audio(
            text=args.text,
            model=model,
            voice=None,
            instruct=args.instruct,
            speed=args.speed,
            lang_code=language,
            temperature=args.temperature,
            output_path=out_dir,
            file_prefix=prefix,
            audio_format=audio_format,
            join_audio=True,
            play=False,
            verbose=True,
        )
        print(f"[+] Audio saved to: {Path(out_dir) / f'{prefix}.{audio_format}'}")
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="MLX-Audio TTS CLI - Qwen3-TTS Speech Synthesis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Voice clone
  %(prog)s voice-clone --text "Hello world" --ref_audio ref.wav --ref_text "Reference text" --language English --output output.wav

  # Preset voice (Japanese)
  %(prog)s custom-voice --text "真実永遠に一つ！" --voice Ryan --language Japanese --temperature 0.7 --speed 1.0 --output output.wav

  # Voice design
  %(prog)s voice-design --text "Welcome" --instruct "young male detective voice" --language English --temperature 0.7 --output output.wav

Available voices: {voices}
Available languages: {languages}
        """.format(voices=", ".join(PRESET_VOICES), languages=", ".join(LANGUAGES))
    )

    subparsers = parser.add_subparsers(dest="mode", help="Synthesis mode")

    # Voice Clone subcommand
    clone_parser = subparsers.add_parser("voice-clone", help="Clone voice from reference audio")
    clone_parser.add_argument("--text", required=True, help="Text to synthesize")
    clone_parser.add_argument("--ref_audio", required=True, help="Reference audio file path")
    clone_parser.add_argument("--ref_text", required=True, help="Reference audio transcript")
    clone_parser.add_argument("--language", default="auto", choices=LANGUAGES, help="Language (default: auto)")
    clone_parser.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature (default: 0.7)")
    clone_parser.add_argument("--speed", type=float, default=1.0, help="Speech speed (default: 1.0)")
    clone_parser.add_argument("--model", help="Model ID (default: Qwen3-TTS-12Hz-0.6B-Base-bf16)")
    clone_parser.add_argument("--output", help="Output file path")
    clone_parser.add_argument("--out-dir", default="./outputs", help="Output directory")

    # Custom Voice subcommand
    voice_parser = subparsers.add_parser("custom-voice", help="Use preset voice")
    voice_parser.add_argument("--text", required=True, help="Text to synthesize")
    voice_parser.add_argument("--voice", default="Serena", help=f"Preset voice ({', '.join(PRESET_VOICES)})")
    voice_parser.add_argument("--instruct", help="Style instruction (optional)")
    voice_parser.add_argument("--language", default="auto", choices=LANGUAGES, help="Language (default: auto)")
    voice_parser.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature (default: 0.7)")
    voice_parser.add_argument("--speed", type=float, default=1.0, help="Speech speed (default: 1.0)")
    voice_parser.add_argument("--model", help="Model ID (default: Qwen3-TTS-12Hz-1.7B-CustomVoice-bf16)")
    voice_parser.add_argument("--output", help="Output file path")
    voice_parser.add_argument("--out-dir", default="./outputs", help="Output directory")

    # Voice Design subcommand
    design_parser = subparsers.add_parser("voice-design", help="Design voice from text description")
    design_parser.add_argument("--text", required=True, help="Text to synthesize")
    design_parser.add_argument("--instruct", required=True, help="Voice description (e.g., warm male voice)")
    design_parser.add_argument("--language", default="auto", choices=LANGUAGES, help="Language (default: auto)")
    design_parser.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature (default: 0.7)")
    design_parser.add_argument("--speed", type=float, default=1.0, help="Speech speed (default: 1.0)")
    design_parser.add_argument("--model", help="Model ID (default: Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16)")
    design_parser.add_argument("--output", help="Output file path")
    design_parser.add_argument("--out-dir", default="./outputs", help="Output directory")

    args = parser.parse_args()

    if args.mode is None:
        parser.print_help()
        sys.exit(1)

    if args.mode == "voice-clone":
        voice_clone(args)
    elif args.mode == "custom-voice":
        custom_voice(args)
    elif args.mode == "voice-design":
        voice_design(args)


if __name__ == "__main__":
    main()
