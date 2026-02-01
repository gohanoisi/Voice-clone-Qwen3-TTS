# coding=utf-8
"""
Qwen3-TTS のラッパークラス。
モデルのロードと音声生成（ボイスクローン）を担当する。
"""

from pathlib import Path
from typing import Tuple

import numpy as np
import torch
import torchaudio

from qwen_tts import Qwen3TTSModel


class Qwen3TTSWrapper:
    """Qwen3-TTS のラッパークラス。"""

    # 対応言語（API 設計に合わせて Japanese / English を明示）
    SUPPORTED_LANGUAGES = ("Japanese", "English", "Auto")

    def __init__(
        self,
        model_name: str = "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        device: str = "cuda:0",
        dtype: torch.dtype = torch.bfloat16,
        attn_implementation: str | None = None,
    ) -> None:
        """
        モデルを初期化する。

        Args:
            model_name: Hugging Face のモデル ID（例: "Qwen/Qwen3-TTS-12Hz-1.7B-Base"）
            device: 実行デバイス（"cuda:0", "cuda", "cpu" 等）
            dtype: 計算に使う torch の dtype（例: torch.float16, torch.bfloat16）
            attn_implementation: 注意力実装（"flash_attention_2" 等）。未指定時は PyTorch 標準。

        Raises:
            RuntimeError: モデルのロードに失敗した場合
            ValueError: model_name または device が不正な場合
        """
        if not model_name or not model_name.strip():
            raise ValueError("model_name を指定してください。")
        if not device or not device.strip():
            raise ValueError("device を指定してください。")

        self._model_name = model_name.strip()
        self._device = device.strip()
        self._dtype = dtype

        load_kwargs: dict = {
            "device_map": self._device,
            "dtype": self._dtype,
        }
        if attn_implementation is not None:
            load_kwargs["attn_implementation"] = attn_implementation

        try:
            self._model = Qwen3TTSModel.from_pretrained(
                self._model_name,
                **load_kwargs,
            )
        except Exception as e:
            raise RuntimeError(f"モデルのロードに失敗しました: {e}") from e

    def generate_voice(
        self,
        text: str,
        ref_audio_path: str,
        ref_text: str,
        language: str = "Japanese",
        max_new_tokens: int = 2048,
    ) -> Tuple[np.ndarray, int]:
        """
        テキストから音声を生成する（ボイスクローン）。

        Args:
            text: 読み上げるテキスト
            ref_audio_path: 参照音声のパス（ローカルパスまたは http(s) URL。Qwen3-TTS が対応する形式）
            ref_text: 参照音声の内容（ref_audio の読み上げテキスト。完全一致が望ましい）
            language: 言語。"Japanese", "English", "Auto" のいずれか
            max_new_tokens: 生成トークン数の上限（デフォルト 2048）

        Returns:
            (wav_array, sample_rate): 音声配列（float, -1.0～1.0）とサンプリングレート（int）

        Raises:
            FileNotFoundError: ref_audio_path が存在しない場合
            ValueError: text が空、または language が未対応の場合
            RuntimeError: モデル推論に失敗した場合（VRAM 不足等）
        """
        if not text or not text.strip():
            raise ValueError("text を指定してください。")
        if not ref_text or not ref_text.strip():
            raise ValueError("ref_text を指定してください。")
        if language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"language は {self.SUPPORTED_LANGUAGES} のいずれかを指定してください。"
            )

        # URL の場合はモデルに直接渡す（Qwen3TTSModel が URL をサポート）
        is_url = ref_audio_path.strip().startswith(("http://", "https://"))
        if is_url:
            ref_audio_input: str | Tuple[np.ndarray, int] = ref_audio_path.strip()
        else:
            path = Path(ref_audio_path)
            if not path.exists():
                raise FileNotFoundError(f"参照音声ファイルが見つかりません: {ref_audio_path}")
            ref_audio_input = self._load_ref_audio(str(path))

        try:
            wavs, sample_rate = self._model.generate_voice_clone(
                text=text.strip(),
                language=language,
                ref_audio=ref_audio_input,
                ref_text=ref_text.strip(),
                x_vector_only_mode=False,
                non_streaming_mode=True,
                max_new_tokens=max_new_tokens,
            )
        except Exception as e:
            raise RuntimeError(f"音声生成に失敗しました: {e}") from e

        if not wavs or len(wavs) == 0:
            raise RuntimeError("音声が生成されませんでした。")

        wav = np.asarray(wavs[0], dtype=np.float32)
        # 1次元に揃える（複数チャンネルの場合はモノラル化）
        if wav.ndim > 1:
            wav = np.mean(wav, axis=-1)
        # -1.0～1.0 にクリップ
        wav = np.clip(wav, -1.0, 1.0)

        return wav, int(sample_rate)

    def _load_ref_audio(self, path: str) -> Tuple[np.ndarray, int]:
        """
        参照音声ファイルを読み込み、(wav_array, sample_rate) のタプルで返す。
        WAV/MP3 等は torchaudio で読み、float32 の -1.0～1.0 に正規化する。
        """
        waveform, sample_rate = torchaudio.load(path)
        # モノラル化
        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)
        # float32 に変換し、-1.0～1.0 に正規化（整数入力の場合）
        wav = waveform.squeeze(0).numpy()
        if wav.dtype != np.float32:
            wav = wav.astype(np.float32) / np.iinfo(wav.dtype).max
        wav = np.clip(wav, -1.0, 1.0)
        return (wav, int(sample_rate))
