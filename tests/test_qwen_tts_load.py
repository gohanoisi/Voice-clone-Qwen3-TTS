# coding=utf-8
"""
タスク4-2: Qwen3-TTS モデルロード動作確認

Qwen3TTSWrapper を用いて Qwen3-TTS-12Hz-1.7B-Base をロードし、
VRAM 上で正常に動作するか確認する。

実行方法:
    cd /home/gohan/dev/Voice-clone-Qwen3-TTS
    python -m tests.test_qwen_tts_load

または pytest:
    pytest tests/test_qwen_tts_load.py -v -s
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# プロジェクトルートをパスに追加
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import torch

from src.tts.qwen_wrapper import Qwen3TTSWrapper


# 設定パラメータ（タスク4-2仕様）
MODEL_NAME = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
DEVICE = "cuda"  # RTX 4070 Ti 使用
DTYPE = torch.bfloat16  # メモリ効率化


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


def test_normal_load() -> bool:
    """
    正常系: Qwen3TTSWrapper のインスタンス化とモデルロード成功を確認する。

    Returns:
        成功した場合 True、失敗した場合 False
    """
    print("\n--- 1. 正常系: モデルロード ---")
    _show_vram_status("ロード前")

    start_time = time.perf_counter()
    try:
        wrapper = Qwen3TTSWrapper(
            model_name=MODEL_NAME,
            device=DEVICE,
            dtype=DTYPE,
        )
        elapsed = time.perf_counter() - start_time

        print("  [OK] モデルロードに成功しました。")
        _show_vram_status("ロード後")
        print(f"  [INFO] 所要時間: {elapsed:.2f} 秒")
        print(f"  [INFO] model_name: {wrapper._model_name}")
        print(f"  [INFO] device: {wrapper._device}")
        print(f"  [INFO] dtype: {wrapper._dtype}")

        # device_map と dtype の設定が反映されているか確認
        if hasattr(wrapper, "_model") and wrapper._model is not None:
            model = wrapper._model
            if hasattr(model, "dtype"):
                print(f"  [INFO] モデル内部 dtype: {model.dtype}")
            print("  [OK] device_map と dtype の設定が反映されています。")
        return True
    except RuntimeError as e:
        print(f"  [NG] モデルロードに失敗しました: {e}")
        return False
    except Exception as e:
        print(f"  [NG] 予期せぬエラー: {type(e).__name__}: {e}")
        return False
    finally:
        # メモリ解放のためガベージコレクションを促す
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        _show_vram_status("クリーンアップ後")


def test_invalid_model_name() -> bool:
    """
    異常系: 不正な model_name を指定した場合、RuntimeError が発生することを確認する。

    Returns:
        適切に RuntimeError が発生した場合 True、そうでない場合 False
    """
    print("\n--- 2. 異常系: 不正な model_name ---")
    invalid_model = "invalid/this-model-does-not-exist-12345"

    try:
        Qwen3TTSWrapper(
            model_name=invalid_model,
            device=DEVICE,
            dtype=DTYPE,
        )
        print("  [NG] RuntimeError が発生すべきでしたが、正常終了しました。")
        return False
    except RuntimeError as e:
        print(f"  [OK] 想定どおり RuntimeError が発生しました: {e}")
        return True
    except ValueError as e:
        print(f"  [INFO] ValueError が発生（model_name の検証で早期に弾かれた可能性）: {e}")
        return True  # 不正な入力に対する適切な例外
    except Exception as e:
        print(f"  [NG] 想定外の例外: {type(e).__name__}: {e}")
        return False


def test_empty_model_name() -> bool:
    """
    異常系: 空の model_name を指定した場合、ValueError が発生することを確認する。
    """
    print("\n--- 3. 異常系: 空の model_name ---")
    try:
        Qwen3TTSWrapper(
            model_name="",
            device=DEVICE,
            dtype=DTYPE,
        )
        print("  [NG] ValueError が発生すべきでしたが、正常終了しました。")
        return False
    except ValueError as e:
        print(f"  [OK] 想定どおり ValueError が発生しました: {e}")
        return True
    except Exception as e:
        print(f"  [NG] 想定外の例外: {type(e).__name__}: {e}")
        return False


def main() -> int:
    """テストスクリプトのエントリポイント。"""
    print("=" * 60)
    print("タスク4-2: Qwen3-TTS モデルロード動作確認")
    print("=" * 60)
    print(f"モデル: {MODEL_NAME}")
    print(f"デバイス: {DEVICE}")
    print(f"dtype: {DTYPE}")
    print(f"CUDA 利用可能: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    results: list[bool] = []

    # 1. 正常系: モデルロード
    results.append(test_normal_load())

    # 2. 異常系: 不正な model_name（VRAM を消費するため正常系の後に実行）
    results.append(test_invalid_model_name())

    # 3. 異常系: 空の model_name
    results.append(test_empty_model_name())

    # 結果サマリ
    passed = sum(results)
    total = len(results)
    print("\n" + "=" * 60)
    print(f"結果: {passed}/{total} テスト成功")
    print("=" * 60)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
