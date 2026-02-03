# coding=utf-8
"""
音声合成CLIツール。

話者一覧の表示、指定話者でのテキスト音声合成、出力ファイル保存を行う。
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import soundfile as sf

from src.profile import VoiceProfileManager
from src.tts import VoiceCloneManager


def _default_output_path() -> str:
    """デフォルト出力ファイルパス: outputs/synthesis_YYYYMMDD_HHMMSS.wav"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"outputs/synthesis_{timestamp}.wav"


def main() -> None:
    """
    CLIツールのメイン処理。

    argparseで以下の引数を処理：
    - --list-speakers: 話者一覧を表示して終了
    - --speaker: 話者名（必須、list-speakers時は不要）
    - --text: 合成するテキスト（必須、list-speakers時は不要）
    - --output: 出力ファイルパス（デフォルト: outputs/synthesis_<timestamp>.wav）
    - --language: 言語（デフォルト: ja、選択肢: ja/en）
    - --metadata: メタデータファイルパス（デフォルト: data/metadata.csv）
    """
    parser = argparse.ArgumentParser(
        description="音声合成CLIツール（話者一覧表示・テキスト音声合成）"
    )
    parser.add_argument(
        "--list-speakers",
        action="store_true",
        help="利用可能な話者一覧を表示して終了",
    )
    parser.add_argument("--speaker", type=str, help="話者名")
    parser.add_argument("--text", type=str, help="合成するテキスト")
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="出力WAVファイルパス（デフォルト: outputs/synthesis_YYYYMMDD_HHMMSS.wav）",
    )
    parser.add_argument(
        "--language",
        type=str,
        default="ja",
        choices=["ja", "en"],
        help="合成時の言語（デフォルト: ja）",
    )
    parser.add_argument(
        "--metadata",
        type=str,
        default="data/metadata.csv",
        help="メタデータCSVのパス（デフォルト: data/metadata.csv）",
    )
    args = parser.parse_args()

    # 話者一覧表示モード
    if args.list_speakers:
        try:
            profile_manager = VoiceProfileManager(args.metadata)
        except FileNotFoundError as e:
            print(f"エラー: {e}", file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(f"エラー: {e}", file=sys.stderr)
            sys.exit(1)
        speakers = profile_manager.list_speakers()
        print("利用可能な話者:")
        for name in speakers:
            print(f"  - {name}")
        return

    # 音声合成モード: 必須引数チェック
    if not args.speaker or not args.speaker.strip():
        print("エラー: 音声合成には --speaker を指定してください。", file=sys.stderr)
        print("  例: python -m src.tools.test_synthesis --speaker gohan --text \"こんにちは\"", file=sys.stderr)
        sys.exit(1)
    if not args.text or not args.text.strip():
        print("エラー: 音声合成には --text を指定してください。", file=sys.stderr)
        sys.exit(1)

    # メタデータ・プロファイル取得
    try:
        profile_manager = VoiceProfileManager(args.metadata)
    except FileNotFoundError as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        profile = profile_manager.get_profile(args.speaker.strip())
    except ValueError as e:
        print(f"エラー: 話者 '{args.speaker}' が見つかりません。", file=sys.stderr)
        print(f"利用可能な話者: {', '.join(profile_manager.list_speakers())}", file=sys.stderr)
        sys.exit(1)

    # 参照音声の絶対パス（メタデータの親の親 = プロジェクトルート基準）
    metadata_path = Path(args.metadata).resolve()
    root = metadata_path.parent.parent
    ref_audio_path = str(root / profile["audio_path"])

    # VoiceCloneManager で音声合成
    try:
        voice_manager = VoiceCloneManager(
            ref_audio_path=ref_audio_path,
            ref_text=profile["corpus_text"],
            language=profile["language"],
        )
    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        wav_array, sample_rate = voice_manager.synthesize(
            args.text.strip(),
            language=args.language,
        )
    except ValueError as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"エラー: 音声生成に失敗しました: {e}", file=sys.stderr)
        sys.exit(1)

    # 出力ファイル保存
    output_path = Path(args.output or _default_output_path())
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(output_path), wav_array, sample_rate)
    print(f"音声を保存しました: {output_path}")


if __name__ == "__main__":
    main()
