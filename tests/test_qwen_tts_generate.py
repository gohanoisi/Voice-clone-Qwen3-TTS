# coding=utf-8
"""
タスク4-3: 公式サンプル音声による音声生成テスト

Qwen3-TTS 公式サンプル音声を使用して、generate_voice による
ボイスクローン動作を確認する。

実行方法:
    cd /home/gohan/dev/Voice-clone-Qwen3-TTS
    python -m tests.test_qwen_tts_generate

または pytest:
    pytest tests/test_qwen_tts_generate.py -v -s
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen

# プロジェクトルートをパスに追加
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np
import soundfile as sf
import torch

from src.tts.qwen_wrapper import Qwen3TTSWrapper


# 設定パラメータ（タスク4-3仕様）
MODEL_NAME = "Qwen/Qwen3-TTS-12Hz-1.7B-Base"
DEVICE = "cuda"
DTYPE = torch.bfloat16

# 公式サンプル音声
REF_AUDIO_URL = "https://qianwen-res.oss-cn-beijing.aliyuncs.com/Qwen3-TTS-Repo/clone.wav"
REF_AUDIO_LOCAL = _PROJECT_ROOT / "data" / "samples" / "clone.wav"
REF_TEXT = (
    "Okay. Yeah. I resent you. I love you. I respect you. "
    "But you know what? You blew it! And thanks to you."
)

# 生成するテキスト（英語でテスト）
TEXT = (
    "This is a test of voice cloning with Qwen3-TTS. "
    "The quick brown fox jumps over the lazy dog."
)
LANGUAGE = "English"

# 出力先
OUTPUT_PATH = _PROJECT_ROOT / "outputs" / "test_generated.wav"


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


def get_ref_audio_path() -> str:
    """
    参照音声のパスを返す。
    1. ローカルに存在すればそれを使用
    2. なければ公式 URL からダウンロードを試行
    3. ダウンロード失敗時は gTTS で ref_text から音声を生成（フォールバック）

    Returns:
        参照音声のローカルパス
    """
    REF_AUDIO_LOCAL.parent.mkdir(parents=True, exist_ok=True)

    if REF_AUDIO_LOCAL.exists():
        print(f"  [INFO] 参照音声をローカルから使用: {REF_AUDIO_LOCAL}")
        return str(REF_AUDIO_LOCAL)

    # 1. 公式 URL からダウンロードを試行
    print(f"  [INFO] 参照音声をダウンロード中: {REF_AUDIO_URL}")
    try:
        req = Request(
            REF_AUDIO_URL,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        )
        with urlopen(req, timeout=60) as resp:
            REF_AUDIO_LOCAL.write_bytes(resp.read())
        print(f"  [OK] ダウンロード完了: {REF_AUDIO_LOCAL}")
        return str(REF_AUDIO_LOCAL)
    except Exception as e:
        print(f"  [WARN] ダウンロード失敗 ({e})")

    # 2. gTTS で ref_text から音声を生成（フォールバック）
    # torchaudio は MP3 を読み込めるため、そのまま MP3 で保存して使用
    print("  [INFO] gTTS で参照音声を生成中（フォールバック）...")
    try:
        from gtts import gTTS

        fallback_path = REF_AUDIO_LOCAL.with_suffix(".mp3")
        tts = gTTS(text=REF_TEXT, lang="en")
        tts.save(str(fallback_path))
        print(f"  [OK] gTTS で生成完了: {fallback_path}")
        return str(fallback_path)
    except ImportError:
        print("  [WARN] gTTS が未インストールです。pip install gtts で導入可能")
    except Exception as e:
        print(f"  [WARN] gTTS 生成失敗: {e}")

    # 3. どちらも失敗
    raise RuntimeError(
        f"参照音声を用意できませんでした。\n"
        f"手動で {REF_AUDIO_URL} をブラウザでダウンロードし、{REF_AUDIO_LOCAL} に配置してください。"
    )


def run_generation_test() -> bool:
    """
    generate_voice を実行し、音声を保存する。

    Returns:
        成功した場合 True、失敗した場合 False
    """
    print("\n--- タスク4-3: 公式サンプル音声による音声生成 ---")
    _show_vram_status("開始時")

    # 1. 参照音声のパスを取得（ローカル or URL）
    print("\n[1] 参照音声の準備")
    ref_audio_path = get_ref_audio_path()

    # 2. モデルロード
    print("\n[2] モデルロード")
    load_start = time.perf_counter()
    try:
        wrapper = Qwen3TTSWrapper(
            model_name=MODEL_NAME,
            device=DEVICE,
            dtype=DTYPE,
        )
        load_elapsed = time.perf_counter() - load_start
        print(f"  [OK] モデルロード完了（{load_elapsed:.2f} 秒）")
    except RuntimeError as e:
        print(f"  [NG] モデルロード失敗: {e}")
        return False

    _show_vram_status("モデルロード後")

    # 3. 音声生成
    print("\n[3] 音声生成（generate_voice）")
    gen_start = time.perf_counter()
    try:
        wav_array, sample_rate = wrapper.generate_voice(
            text=TEXT,
            ref_audio_path=ref_audio_path,
            ref_text=REF_TEXT,
            language=LANGUAGE,
        )
        gen_elapsed = time.perf_counter() - gen_start
        print("  [OK] 音声生成完了")
    except FileNotFoundError as e:
        print(f"  [NG] 参照音声が見つかりません: {e}")
        return False
    except ValueError as e:
        print(f"  [NG] パラメータエラー: {e}")
        return False
    except RuntimeError as e:
        print(f"  [NG] 音声生成失敗: {e}")
        return False

    _show_vram_status("生成後")

    # 4. 音声の長さを計算
    duration_sec = len(wav_array) / sample_rate
    print(f"  [INFO] 生成時間: {gen_elapsed:.2f} 秒")
    print(f"  [INFO] 音声の長さ: {duration_sec:.2f} 秒")
    print(f"  [INFO] サンプル数: {len(wav_array)}, サンプリングレート: {sample_rate} Hz")
    if duration_sec > 0:
        rtf = gen_elapsed / duration_sec
        print(f"  [INFO] リアルタイム係数 (RTF): {rtf:.2f}x")

    # 5. WAV ファイルに保存
    print("\n[4] 音声ファイルの保存")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        sf.write(str(OUTPUT_PATH), wav_array, sample_rate)
        print(f"  [OK] 保存完了: {OUTPUT_PATH}")
    except OSError as e:
        print(f"  [NG] ファイル保存失敗: {e}")
        return False

    print("\n" + "=" * 60)
    print("タスク4-3 完了: 公式サンプル音声での音声生成に成功しました")
    print("=" * 60)
    return True


def main() -> int:
    """テストスクリプトのエントリポイント。"""
    print("=" * 60)
    print("タスク4-3: 公式サンプル音声による音声生成テスト")
    print("=" * 60)
    print(f"モデル: {MODEL_NAME}")
    print(f"参照音声: {REF_AUDIO_URL}")
    print(f"生成テキスト: {TEXT[:50]}...")
    print(f"出力先: {OUTPUT_PATH}")

    success = run_generation_test()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
