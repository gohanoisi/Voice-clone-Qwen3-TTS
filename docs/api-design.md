# API 設計書

Voice-clone-Qwen3-TTS の各モジュールの公開 API（クラス・関数のシグネチャ、引数、戻り値、例外処理）を定義する。

---

## 2.1 Voice Profile Management Module API

### 2.1.1 `src/profile/voice_profile_manager.py`

#### クラス: `VoiceProfileManager`

声プロファイル（ref_audio + ref_text）の管理。メタデータ（CSV または JSON）を読み込み、話者一覧・プロファイル取得を提供する。

```python
# src/profile/voice_profile_manager.py

from typing import Any, Dict, List


class VoiceProfileManager:
    """声プロファイル（ref_audio + ref_text）の管理"""

    def __init__(self, metadata_path: str = "data/metadata.csv") -> None:
        """
        Args:
            metadata_path: メタデータファイルのパス（CSV or JSON）

        Raises:
            FileNotFoundError: メタデータファイルが存在しない
            ValueError: メタデータの形式が不正
        """
        pass

    def list_speakers(self) -> List[str]:
        """
        利用可能な話者名の一覧を返す。

        Returns:
            話者名のリスト（例: ["gohan", "friend_a"]）
        """
        pass

    def get_profile(self, speaker_name: str) -> Dict[str, Any]:
        """
        指定した話者の声プロファイルを取得（代表 1 件）。

        Args:
            speaker_name: 話者名

        Returns:
            {
                "audio_path": "data/voice_samples/001_gohan.mp3",
                "corpus_text": "こんにちは、私の名前は...",
                "language": "ja",
                "description": "メインの声プロファイル"
            }

        Raises:
            ValueError: 話者名が見つからない
        """
        pass

    def get_all_profiles(self, speaker_name: str) -> List[Dict[str, Any]]:
        """
        指定した話者の全サンプルを取得（複数音声サンプルがある場合）。

        Returns:
            声プロファイルのリスト
        """
        pass
```

---

## 2.2 CLI Tool Interface

### 2.2.1 `src/tools/test_synthesis.py`

話者一覧の表示および、話者指定 + 任意テキストで音声合成を行う CLI。argparse と VoiceProfileManager を連携させる。

```bash
# 話者一覧の表示
python -m src.tools.test_synthesis --list-speakers

# 音声合成（話者指定 + テキスト）
python -m src.tools.test_synthesis --speaker gohan --text "今日はいい天気ですね"

# 音声合成（出力ファイル指定）
python -m src.tools.test_synthesis --speaker gohan --text "テストです" --output outputs/test.wav

# 言語指定（デフォルト: ja）
python -m src.tools.test_synthesis --speaker friend_a --text "Hello world" --language en
```

- **既存 API の修正なし**: `Qwen3TTSWrapper` および `VoiceCloneManager` はそのまま使用する。VoiceProfileManager から取得したプロファイル（audio_path, corpus_text）を VoiceCloneManager に渡して音声生成する。

---

## 2.3 TTS Module API

### 2.3.1 `src/tts/qwen_wrapper.py`

#### クラス: `Qwen3TTSWrapper`

Qwen3-TTS のラッパークラス。モデルのロードと音声生成を担当する。

```python
# src/tts/qwen_wrapper.py

from typing import Tuple
import numpy as np
import torch


class Qwen3TTSWrapper:
    """Qwen3-TTS のラッパークラス"""

    def __init__(self, model_name: str, device: str, dtype: torch.dtype) -> None:
        """
        モデルを初期化する。

        Args:
            model_name: Hugging Face のモデル ID（例: "Qwen/Qwen3-TTS-12Hz-1.7B-Base"）
            device: 実行デバイス（"cuda" or "cpu"）
            dtype: 計算に使う torch の dtype（例: torch.float16, torch.bfloat16）

        Raises:
            RuntimeError: モデルのロードに失敗した場合
            ValueError: model_name / device が不正な場合
        """
        pass

    def generate_voice(
        self,
        text: str,
        ref_audio_path: str,
        ref_text: str,
        language: str = "Japanese",
    ) -> Tuple[np.ndarray, int]:
        """
        テキストから音声を生成する（ボイスクローン）。

        Args:
            text: 読み上げるテキスト
            ref_audio_path: 参照音声ファイルのパス（WAV/MP3 等、Qwen3-TTS が対応する形式）
            ref_text: 参照音声の内容（ref_audio の読み上げテキスト。完全一致が望ましい）
            language: 言語。"Japanese" または "English"

        Returns:
            (wav_array, sample_rate): 音声配列（float, -1.0～1.0）とサンプリングレート（int）

        Raises:
            FileNotFoundError: ref_audio_path が存在しない場合
            ValueError: text が空、または language が未対応の場合
            RuntimeError: モデル推論に失敗した場合（VRAM 不足等）
        """
        pass
```

---

### 2.3.2 `src/tts/voice_clone.py`

#### クラス: `VoiceCloneManager`（または関数群）

参照音声パス・参照テキストを保持し、`Qwen3TTSWrapper` を呼び出す窓口。設定（Config）から参照音声情報を取得する想定。

```python
# src/tts/voice_clone.py

from typing import Tuple
import numpy as np


class VoiceCloneManager:
    """ボイスクローン用の参照音声と TTS ラッパーを管理する"""

    def __init__(self, wrapper: "Qwen3TTSWrapper", ref_audio_path: str, ref_text: str) -> None:
        """
        Args:
            wrapper: 初期化済みの Qwen3TTSWrapper インスタンス
            ref_audio_path: 参照音声ファイルのパス
            ref_text: 参照音声の読み上げテキスト（corpus と一致させる）

        Raises:
            FileNotFoundError: ref_audio_path が存在しない場合
        """
        pass

    def synthesize(self, text: str, language: str = "Japanese") -> Tuple[np.ndarray, int]:
        """
        登録した参照音声でテキストを合成する。

        Args:
            text: 読み上げるテキスト
            language: 言語。"Japanese" または "English"

        Returns:
            (wav_array, sample_rate): 音声配列とサンプリングレート

        Raises:
            ValueError: text が空の場合
            RuntimeError: TTS 生成に失敗した場合
        """
        pass
```

---

## 2.4 Discord Bot API

### 2.4.1 `src/bot/commands.py`

スラッシュコマンドの定義。`discord.app_commands` を使用する想定。

```python
# src/bot/commands.py

import discord
from discord import app_commands


# bot は main.py で定義された discord.Client のインスタンスを想定
# 以下はコマンドのシグネチャと責務のみ定義（実装は pass）


@bot.tree.command(name="join", description="ボイスチャンネルに参加")
async def join_vc(interaction: discord.Interaction) -> None:
    """
    コマンドを実行したユーザーがいるボイスチャンネルに Bot を参加させる。

    事前条件: ユーザーがボイスチャンネルに接続していること。

    Args:
        interaction: Discord のスラッシュコマンド interaction

    Raises:
        (discord 側): ユーザーが VC にいない場合はエラーメッセージを返答
    """
    pass


@bot.tree.command(name="leave", description="ボイスチャンネルから退出")
async def leave_vc(interaction: discord.Interaction) -> None:
    """
    Bot を現在接続しているボイスチャンネルから退出させる。

    Args:
        interaction: Discord のスラッシュコマンド interaction
    """
    pass
```

- **戻り値**: いずれも `None`。応答は `interaction.response.send_message()` で行う。
- **例外**: ハンドラ内で捕捉し、`interaction.followup.send()` または `interaction.response.send_message()` でユーザーにエラー内容を伝える。未処理の例外は Bot 全体のエラーハンドラでログ出力する。

---

### 2.4.2 `src/bot/events.py`

メッセージイベントのハンドラ。テキストを検知し、TTS → 再生を依頼する。

```python
# src/bot/events.py

import discord


@bot.event
async def on_message(message: discord.Message) -> None:
    """
    テキストチャンネルへのメッセージ送信を検知し、条件を満たす場合に TTS 音声を生成して VC で再生する。

    実行条件（すべて満たす場合のみ TTS を実行）:
    - メッセージ送信者が Bot 自身ではない（message.author.bot == False）
    - メッセージ送信者が何らかのボイスチャンネルに接続している
    - Bot が同じボイスチャンネルに接続している
    - メッセージ内容が空でない（空白のみは除外してよい）

    処理の流れ:
    1. 上記条件をチェック
    2. TTS Module で message.content から音声生成
    3. Audio Module で一時 WAV 作成 → 再生 → クリーンアップ（または再生完了後に削除）

    Args:
        message: Discord の Message オブジェクト

    Raises:
        (内部で捕捉): TTS 失敗・再生失敗時はログに記録し、必要に応じてメッセージチャンネルにエラーを返す
    """
    pass
```

- **戻り値**: `None`
- **例外**: TTS や再生で発生した例外はハンドラ内で捕捉し、ログ出力とユーザーへの簡潔なエラー通知を行う。`on_message` 内で未処理の例外を残さない。

---

## 2.5 Audio Module API

### 2.5.1 `src/audio/player.py`

VC での音声再生を管理する。

```python
# src/audio/player.py

import discord


class AudioPlayer:
    """Discord VC での音声再生を管理する"""

    async def play_audio(
        self,
        voice_client: discord.VoiceClient,
        audio_path: str,
    ) -> None:
        """
        指定した音声ファイルを VC で再生する。
        再生が完了するまで待機する（キューがある場合は順次再生）。

        Args:
            voice_client: 接続済みの discord.VoiceClient
            audio_path: 再生する WAV ファイルのパス（ローカルパス）

        Raises:
            FileNotFoundError: audio_path が存在しない場合
            discord.ClientException: voice_client が未接続または無効な場合
            Exception: 再生ソースの作成・再生に失敗した場合（内部でログ出力し、再 raise するかは実装で決定）
        """
        pass
```

- **補足**: 複数メッセージが短時間に連続した場合のキューイングの有無は実装で決定する。API としては「再生が完了するまで待つ」を保証する。

---

### 2.5.2 `src/audio/file_manager.py`

一時 WAV ファイルの作成と削除を管理する。

```python
# src/audio/file_manager.py

from typing import Optional
import numpy as np


class TempFileManager:
    """一時 WAV ファイルの作成・削除を管理する"""

    def __init__(self, temp_dir: Optional[str] = None) -> None:
        """
        Args:
            temp_dir: 一時ファイルを保存するディレクトリ。
                       None の場合はアプリの設定（例: logs/temp_audio/）またはシステムの一時ディレクトリを使用。
        """
        pass

    def create_temp_wav(self, wav_array: np.ndarray, sample_rate: int) -> str:
        """
        WAV 配列から一時ファイルを作成し、そのパスを返す。

        Args:
            wav_array: 音声データ（float, -1.0～1.0）。1次元を想定
            sample_rate: サンプリングレート（int）

        Returns:
            作成した一時 WAV ファイルの絶対パス（str）。呼び出し側で再生後に削除するか、cleanup_temp_files に任せる

        Raises:
            ValueError: wav_array が空または不正な shape の場合
            OSError: ファイルの書き込みに失敗した場合
        """
        pass

    def cleanup_temp_files(self) -> None:
        """
        このマネージャが作成した古い一時ファイルを削除する。
        削除対象の基準（例: 作成から N 分経過）は実装で定義する。
        再生中またはロック中のファイルは削除しない。
        """
        pass
```

- **補足**: 一時ファイルの命名（UUID やタイムスタンプ）と、`cleanup_temp_files` の呼び出しタイミング（再生完了時・定期ジョブ等）は実装時に `technical-decisions.md` と合わせて決定する。

---

## 2.6 Config Module API（参考）

Bot や TTS から利用する設定の窓口。API 設計の一環としてシグネチャのみ記載する。

```python
# src/config/settings.py

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Settings:
    """アプリケーション設定（環境変数・.env から読み込み）"""

    discord_token: str
    model_name: str
    device: str
    ref_audio_path: Path
    ref_text: str
    temp_audio_dir: Optional[Path] = None
    # 必要に応じて dtype, language のデフォルト等を追加

    @classmethod
    def load(cls) -> "Settings":
        """
        環境変数および .env から設定を読み込み、Settings インスタンスを返す。

        Raises:
            ValueError: 必須項目（例: DISCORD_TOKEN）が未設定の場合
        """
        pass
```

---

## 2.7 モジュール間の呼び出し関係（まとめ）

| 呼び出し元 | 呼び出し先 | 主な API |
|------------|------------|----------|
| Bot (events) | Profile (voice_profile_manager) | `VoiceProfileManager.get_profile(speaker_name)` |
| Bot (events) | TTS (voice_clone) | `VoiceCloneManager.synthesize(text, language)` |
| Bot (events) | Audio (file_manager) | `TempFileManager.create_temp_wav(wav_array, sr)` |
| Bot (events) | Audio (player) | `AudioPlayer.play_audio(voice_client, audio_path)` |
| CLI (test_synthesis) | Profile | `VoiceProfileManager.list_speakers()`, `get_profile()` |
| CLI (test_synthesis) | TTS (voice_clone) | `VoiceCloneManager.synthesize(text, language)`（プロファイル取得後に ref_audio, ref_text を渡して生成） |
| Bot / TTS | Config | `Settings.load()` または注入された `Settings` |
| TTS (voice_clone) | TTS (qwen_wrapper) | `Qwen3TTSWrapper.generate_voice(...)` |

---

*本ドキュメントは設計フェーズの成果物。実装時はこのシグネチャと例外仕様に従い、詳細は `docs/architecture.md` および `docs/technical-decisions.md` と整合させる。*
