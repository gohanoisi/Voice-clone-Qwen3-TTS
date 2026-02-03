# coding=utf-8
"""
タスク5-4: 自分の音声サンプルでボイスクローン実行テスト

data/voice_samples/my_voice.mp3 と data/corpus.txt を使用し、
VoiceCloneManager で音声生成 → outputs/voice_clone_test.wav に保存。
生成時間・VRAM・音声長・RTF を記録し、エラーハンドリングを確認する。

実行方法:
    cd /home/gohan/dev/Voice-clone-Qwen3-TTS
    python -m tests.test_voice_clone

または pytest:
    pytest tests/test_voice_clone.py -v -s
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# プロジェクトルートをパスに追加
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np
import soundfile as sf
import torch

from src.tts.voice_clone import VoiceCloneManager


# タスク5-4 仕様
REF_AUDIO_PATH = _PROJECT_ROOT / "data" / "voice_samples" / "my_voice.mp3"
CORPUS_PATH = _PROJECT_ROOT / "data" / "corpus.txt"
OUTPUT_PATH = _PROJECT_ROOT / "outputs" / "voice_clone_test.wav"
TEST_TEXT = "今日はいい天気ですね。ボイスクローンのテストです。"


def _format_vram_mb(amount: int) -> str:
    """VRAM 使用量を MB 単位でフォーマットする。"""
    return f"{amount / 1024 / 1024:.2f} MB"


def _show_vram_status(label: str) -> None:
    """現在の VRAM 使用量を表示する。"""
    if not torch.cuda.is_available():
        print(f"  [{label}] CUDA 利用不可のため VRAM 情報は表示しません。")
        return
    allocated = torch.cuda.memory_allocated()
    reserved = torch.cuda.memory_reserved()
    print(f"  [{label}] 使用中: {_format_vram_mb(allocated)} | 予約: {_format_vram_mb(reserved)}")


def _load_corpus(path: Path) -> str:
    """コーパステキストを読み込む。"""
    if not path.exists():
        raise FileNotFoundError(f"コーパスファイルが見つかりません: {path}")
    return path.read_text(encoding="utf-8").strip()


def run_voice_clone_test() -> dict | None:
    """
    VoiceCloneManager で音声生成し、ファイルに保存する。
    成功時は結果サマリ（生成時間・VRAM・音声長・RTF）を返す。失敗時は None。
    """
    print("\n--- タスク5-4: 自分の音声でボイスクローン ---")
    _show_vram_status("開始時")

    if not REF_AUDIO_PATH.exists():
        print(f"  [NG] 参照音声が見つかりません: {REF_AUDIO_PATH}")
        print("  data/voice_samples/my_voice.mp3 を配置してから再実行してください。")
        return None

    ref_text = _load_corpus(CORPUS_PATH)
    print(f"  [INFO] 参照音声: {REF_AUDIO_PATH}")
    print(f"  [INFO] コーパス長: {len(ref_text)} 文字")

    # 1. VoiceCloneManager のインスタンス化（モデルロード含む）
    print("\n[1] VoiceCloneManager のインスタンス化（モデルロード）")
    load_start = time.perf_counter()
    try:
        manager = VoiceCloneManager(
            ref_audio_path=str(REF_AUDIO_PATH),
            ref_text=ref_text,
            language="ja",
        )
        load_elapsed = time.perf_counter() - load_start
        print(f"  [OK] インスタンス化完了（{load_elapsed:.2f} 秒）")
    except FileNotFoundError as e:
        print(f"  [NG] 参照音声が見つかりません: {e}")
        return None
    except ValueError as e:
        print(f"  [NG] パラメータエラー: {e}")
        return None
    except RuntimeError as e:
        print(f"  [NG] モデルロード失敗: {e}")
        return None

    _show_vram_status("モデルロード後")

    # 2. 音声生成
    print("\n[2] 音声生成（synthesize）")
    gen_start = time.perf_counter()
    try:
        wav_array, sample_rate = manager.synthesize(TEST_TEXT, language="ja")
        gen_elapsed = time.perf_counter() - gen_start
        print("  [OK] 音声生成完了")
    except ValueError as e:
        print(f"  [NG] パラメータエラー: {e}")
        return None
    except RuntimeError as e:
        print(f"  [NG] 音声生成失敗: {e}")
        return None

    _show_vram_status("生成後")

    duration_sec = len(wav_array) / sample_rate
    rtf = gen_elapsed / duration_sec if duration_sec > 0 else 0.0
    print(f"  [INFO] 生成時間: {gen_elapsed:.2f} 秒")
    print(f"  [INFO] 音声の長さ: {duration_sec:.2f} 秒")
    print(f"  [INFO] サンプル数: {len(wav_array)}, サンプリングレート: {sample_rate} Hz")
    print(f"  [INFO] リアルタイム係数 (RTF): {rtf:.2f}x")

    # 3. WAV 保存
    print("\n[3] 音声ファイルの保存")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        sf.write(str(OUTPUT_PATH), wav_array, sample_rate)
        print(f"  [OK] 保存完了: {OUTPUT_PATH}")
    except OSError as e:
        print(f"  [NG] ファイル保存失敗: {e}")
        return None

    vram_allocated = int(torch.cuda.memory_allocated()) if torch.cuda.is_available() else 0
    result = {
        "load_time_sec": load_elapsed,
        "gen_time_sec": gen_elapsed,
        "duration_sec": duration_sec,
        "rtf": rtf,
        "vram_mb": vram_allocated / 1024 / 1024,
        "sample_rate": sample_rate,
        "error": None,
    }
    print("\n" + "=" * 60)
    print("タスク5-4 完了: ボイスクローン音声生成に成功しました")
    print("=" * 60)
    return result


def test_error_handling() -> bool:
    """エラーハンドリング（ref_audio_path 不正・ref_text 空）を確認する。"""
    print("\n--- エラーハンドリング確認 ---")

    # ref_audio_path が存在しない
    try:
        VoiceCloneManager(
            ref_audio_path="/nonexistent/my_voice.mp3",
            ref_text="some text",
            language="ja",
        )
        print("  [NG] FileNotFoundError が期待されましたが、例外が発生しませんでした。")
        return False
    except FileNotFoundError as e:
        print(f"  [OK] FileNotFoundError（参照音声なし）: {e}")
    except Exception as e:
        print(f"  [NG] 想定外の例外: {type(e).__name__}: {e}")
        return False

    # ref_text が空（インスタンス化前にバリデーションされるが、参照音声がないので
    # 先に FileNotFoundError になる。参照音声がある場合の ref_text 空をテストするには
    # 一時的に ref_audio_path を存在するパスにする必要がある）
    try:
        VoiceCloneManager(
            ref_audio_path=str(REF_AUDIO_PATH),
            ref_text="",
            language="ja",
        )
        print("  [NG] ValueError（ref_text 空）が期待されましたが、例外が発生しませんでした。")
        return False
    except ValueError as e:
        print(f"  [OK] ValueError（ref_text 空）: {e}")
    except Exception as e:
        print(f"  [NG] 想定外の例外: {type(e).__name__}: {e}")
        return False

    print("  エラーハンドリング確認完了")
    return True


def main() -> int:
    """テストスクリプトのエントリポイント。"""
    print("=" * 60)
    print("タスク5-4: 自分の音声でボイスクローン実行テスト")
    print("=" * 60)
    print(f"参照音声: {REF_AUDIO_PATH}")
    print(f"コーパス: {CORPUS_PATH}")
    print(f"生成テキスト: {TEST_TEXT}")
    print(f"出力先: {OUTPUT_PATH}")

    # エラーハンドリング確認（参照音声が存在する場合のみメイン実行の前に実施）
    ok_errors = test_error_handling()

    result = run_voice_clone_test()
    if result is None:
        return 1

    # 実行結果サマリを標準出力に表示（development-log 記録用）
    print("\n--- 実行結果サマリ（development-log 用） ---")
    print(f"  生成時間: {result['gen_time_sec']:.2f} 秒")
    print(f"  VRAM 使用量: {result['vram_mb']:.2f} MB")
    print(f"  音声の長さ: {result['duration_sec']:.2f} 秒")
    print(f"  RTF: {result['rtf']:.2f}x")
    print(f"  エラー: {result['error']}")

    return 0 if ok_errors else 1


if __name__ == "__main__":
    sys.exit(main())
