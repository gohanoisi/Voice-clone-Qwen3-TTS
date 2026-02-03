# coding=utf-8
"""
ボイスクローン用マネージャ。
参照音声パス・参照テキストを保持し、Qwen3TTSWrapper を呼び出す窓口。
"""

from pathlib import Path
from typing import TYPE_CHECKING, Tuple

import numpy as np
import torch

from src.tts.qwen_wrapper import Qwen3TTSWrapper

if TYPE_CHECKING:
    pass  # Qwen3TTSWrapper は上で import 済み

# 言語コードと Qwen3TTSWrapper の language の対応
_LANG_MAP = {
    "ja": "Japanese",
    "en": "English",
    "Japanese": "Japanese",
    "English": "English",
    "Auto": "Auto",
}


class VoiceCloneManager:
    """ボイスクローン用の参照音声と TTS ラッパーを管理する。"""

    def __init__(
        self,
        ref_audio_path: str,
        ref_text: str,
        language: str = "ja",
        *,
        model_name: str = "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        device: str | None = None,
        dtype: torch.dtype | None = None,
    ) -> None:
        """
        参照音声とコーパステキストを登録し、Qwen3TTSWrapper を初期化する。

        Args:
            ref_audio_path: 参照音声ファイルのパス（WAV/MP3 等）
            ref_text: 参照音声の読み上げテキスト（corpus と一致させる）
            language: 参照音声の言語。"ja" / "en" または "Japanese" / "English"
            model_name: Qwen3-TTS のモデル ID（オプション）
            device: 実行デバイス。None の場合は "cuda" または "cpu"
            dtype: 計算に使う dtype。None の場合は torch.bfloat16（CUDA 時）または torch.float32

        Raises:
            FileNotFoundError: ref_audio_path が存在しない場合
            ValueError: ref_text が空、または language が未対応の場合
            RuntimeError: モデルのロードに失敗した場合
        """
        if not ref_text or not ref_text.strip():
            raise ValueError("ref_text を指定してください。")

        norm_lang = _normalize_language(language)
        if norm_lang not in Qwen3TTSWrapper.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"language は 'ja' / 'en' または {Qwen3TTSWrapper.SUPPORTED_LANGUAGES} のいずれかを指定してください。"
            )

        # ローカルファイルの存在確認（URL の場合はスキップ）
        path_str = ref_audio_path.strip()
        if not path_str.startswith(("http://", "https://")):
            path = Path(path_str)
            if not path.exists():
                raise FileNotFoundError(f"参照音声ファイルが見つかりません: {ref_audio_path}")

        self._ref_audio_path = path_str
        self._ref_text = ref_text.strip()
        self._language = norm_lang

        _device = device if device is not None else ("cuda" if torch.cuda.is_available() else "cpu")
        _dtype = dtype if dtype is not None else (torch.bfloat16 if _device.startswith("cuda") else torch.float32)

        try:
            self._wrapper = Qwen3TTSWrapper(
                model_name=model_name,
                device=_device,
                dtype=_dtype,
            )
        except Exception as e:
            raise RuntimeError(f"モデルのロードに失敗しました: {e}") from e

    def synthesize(self, text: str, language: str = "ja") -> Tuple[np.ndarray, int]:
        """
        登録した参照音声でテキストを合成する。

        Args:
            text: 読み上げるテキスト
            language: 合成時の言語。"ja" / "en" または "Japanese" / "English"

        Returns:
            (wav_array, sample_rate): 音声配列（float, -1.0～1.0）とサンプリングレート（int）

        Raises:
            ValueError: text が空、または language が未対応の場合
            RuntimeError: TTS 生成に失敗した場合
        """
        if not text or not text.strip():
            raise ValueError("text を指定してください。")

        norm_lang = _normalize_language(language)
        if norm_lang not in Qwen3TTSWrapper.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"language は 'ja' / 'en' または {Qwen3TTSWrapper.SUPPORTED_LANGUAGES} のいずれかを指定してください。"
            )

        try:
            wav_array, sample_rate = self._wrapper.generate_voice(
                text=text.strip(),
                ref_audio_path=self._ref_audio_path,
                ref_text=self._ref_text,
                language=norm_lang,
            )
        except FileNotFoundError:
            raise
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"音声生成に失敗しました: {e}") from e

        return wav_array, sample_rate


def _normalize_language(lang: str) -> str:
    """言語コードを Qwen3TTSWrapper の language に正規化する。"""
    key = lang.strip() if lang else ""
    return _LANG_MAP.get(key, lang.strip())
