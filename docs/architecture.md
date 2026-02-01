# アーキテクチャ設計書

Voice-clone-Qwen3-TTS のシステム全体構成・モジュール分割・データフロー・ディレクトリ構造を定義する。

---

## 1.1 システム全体構成

本システムは「音声サンプルからボイスクローンモデルを構築するオフライン処理」と「Discord 上でテキストをクローン音声で読み上げるオンライン処理」の 2 本柱で構成される。

```
[音声サンプル録音] → [Qwen3-TTS学習] → [ボイスクローンモデル]
                                            ↓
[Discordメッセージ] → [TTS生成] → [音声再生（VC）]
```

### 構成要素の説明

| 要素 | 説明 |
|------|------|
| **音声サンプル録音** | 開発者がコーパステキストを読み上げ、MP3 等で保存する（外部ツール: NowSmart Audio Recorder 等）。 |
| **Qwen3-TTS学習** | Qwen3-TTS Base モデルに参照音声（ref_audio）と参照テキスト（ref_text）を渡し、その声で発話する「ボイスクローン」を利用する。本プロジェクトではモデル自体の再学習は行わず、推論時の参照音声でクローンを実現する。 |
| **ボイスクローンモデル** | 参照音声＋参照テキストを登録し、任意テキストをその声で合成する利用形態。Hugging Face の Qwen3-TTS-12Hz-1.7B-Base をベースとする。 |
| **Discordメッセージ** | ユーザーがテキストチャンネルに送信したメッセージ。ボットが同一 VC にいるユーザーの発言を検知する。 |
| **TTS生成** | 受け取ったテキストを、登録した参照音声に基づき WAV 形式で合成する。 |
| **音声再生（VC）** | Discord のボイスチャンネル（VC）で、生成した WAV をストリーミング再生する。 |

---

## 1.2 モジュール分割

### モジュール一覧と責務

| モジュール | パス | 責務 | 主な依存 |
|------------|------|------|----------|
| **TTS Module** | `src/tts/` | Qwen3-TTS のラッパー、参照音声を用いた音声生成、ボイスクローン利用の窓口 | Config, Utils |
| **Discord Bot Module** | `src/bot/` | discord.py による Bot 実装、スラッシュコマンド、メッセージイベントハンドラ | TTS, Audio, Config, Utils |
| **Audio Module** | `src/audio/` | 音声ファイルの一時保存・削除、VC での再生制御（再生キュー・完了待ち等） | Config, Utils |
| **Config Module** | `src/config/` | 環境変数・設定ファイルの読み込み、アプリ全体で使う設定オブジェクトの提供 | Utils（ログ等） |
| **Utils Module** | `src/utils/` | ログ出力、エラーハンドリング、共通ヘルパー関数 | なし（最下層） |

### 依存関係（上位 → 下位）

```
Bot Module  ──→  TTS Module
     │              │
     ├──────────────┼──→  Audio Module
     │              │           │
     └──────────────┴───────────┼──→  Config Module
                                │           │
                                └───────────┴──→  Utils Module
```

- **Utils**: 他モジュールから依存されるが、他に依存しない。
- **Config**: Utils のみ依存。設定の読み込みと公開。
- **TTS**: Config / Utils に依存。外部（Bot）からは「テキスト + 参照音声情報 → WAV」の API を提供。
- **Audio**: Config / Utils に依存。一時 WAV の作成・削除と VC 再生。
- **Bot**: TTS / Audio / Config / Utils に依存。Discord のイベントとコマンドを処理し、TTS と再生を組み合わせる。

### 各モジュールの詳細責務

- **TTS Module**
  - `qwen_wrapper.py`: Qwen3-TTS モデルのロード、`generate_voice(text, ref_audio_path, ref_text, language)` の提供。
  - `voice_clone.py`: 参照音声パス・参照テキスト・言語の管理と、ラッパーを呼び出すボイスクローン API。
- **Discord Bot Module**
  - `main.py`: Bot のエントリポイント、クライアント生成、Cog/コマンドの登録、起動処理。
  - `commands.py`: `/join`, `/leave` 等のスラッシュコマンド定義。
  - `events.py`: `on_message` 等のイベントハンドラ。同一 VC ユーザーのメッセージを検知し、TTS → 再生を依頼。
- **Audio Module**
  - `player.py`: `VoiceClient` と音声ファイルパスを受け取り、再生・完了待ち（必要ならキュー）を担当。
  - `file_manager.py`: WAV 配列から一時ファイル作成、古い一時ファイルの削除。
- **Config Module**
  - `settings.py`: `.env` や設定ファイルの読み込み、Discord Token・モデル名・デバイス・参照音声パス等の保持。
- **Utils Module**
  - `logger.py`: 共通ロガー設定。
  - `error_handler.py`: 共通の例外ハンドリング・ログ出力。

---

## 1.3 データフロー

### メインシナリオ: Discord メッセージ → TTS → VC 再生

1. **ユーザーが Discord でスラッシュコマンド `/join` を実行**
   - Bot がそのユーザーがいるボイスチャンネルに参加する。

2. **Bot がユーザーの VC に参加**
   - `VoiceClient` が確立され、以降その VC で再生可能になる。

3. **ユーザーがテキストチャンネルにメッセージを送信**
   - 例: 「こんにちは、テストです」

4. **Bot がメッセージを検知**
   - `on_message` でメッセージを受信。
   - 条件: 送信者が Bot 自身でない、送信者が Bot のいる VC にいる、対象チャンネルが有効、など。

5. **TTS Module でテキスト → 音声生成（Qwen3-TTS）**
   - 設定されている参照音声（ref_audio）と参照テキスト（ref_text）を渡す。
   - `generate_voice(text=メッセージ内容, ref_audio_path=..., ref_text=..., language="Japanese")` を実行。
   - 出力: 音声配列（numpy）とサンプリングレート。

6. **Audio Module で WAV を VC で再生**
   - 音声配列から一時 WAV ファイルを生成（`file_manager`）。
   - `player.play_audio(voice_client, audio_path)` で再生。
   - 再生完了を待つ（必要に応じてキューで順次再生）。

7. **一時ファイルをクリーンアップ**
   - 再生完了後、または定期的に、一時 WAV を削除（`file_manager.cleanup_temp_files`）。

### データフロー図（メッセージ → 再生まで）

```
[Discord] ユーザーがメッセージ送信
       │
       ▼
[Bot: events.on_message]
       │ メッセージ内容・送信者・VC 情報を取得
       ▼
[Config] 参照音声パス・ref_text・言語を取得
       │
       ▼
[TTS: voice_clone / qwen_wrapper]
       │ generate_voice(text, ref_audio_path, ref_text, language)
       │ → (wav_array, sample_rate)
       ▼
[Audio: file_manager]
       │ create_temp_wav(wav_array, sr) → temp_wav_path
       ▼
[Audio: player]
       │ play_audio(voice_client, temp_wav_path)
       ▼
[Discord] VC で音声再生
       │
       ▼
[Audio: file_manager]
       │ cleanup_temp_files（再生後または定期）
       ▼
完了
```

---

## 1.4 ファイル・ディレクトリ構造（詳細版）

```
Voice-clone-Qwen3-TTS/
├── docs/
│   ├── project-spec.md         # 要求・要件定義
│   ├── architecture.md         # アーキテクチャ設計（本ドキュメント）
│   ├── setup.md                # 環境構築手順
│   ├── bolt-plan-01.md         # タスク分解
│   └── api-design.md           # API 設計
├── src/
│   ├── __init__.py
│   ├── tts/
│   │   ├── __init__.py
│   │   ├── qwen_wrapper.py     # Qwen3-TTS ラッパー
│   │   └── voice_clone.py     # ボイスクローン管理
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── main.py             # Bot エントリポイント
│   │   ├── commands.py         # スラッシュコマンド定義
│   │   └── events.py           # イベントハンドラ（メッセージ検知）
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── player.py           # 音声再生制御
│   │   └── file_manager.py    # 一時ファイル管理
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # 環境変数・設定管理
│   └── utils/
│       ├── __init__.py
│       ├── logger.py           # ログ管理
│       └── error_handler.py   # エラーハンドリング
├── data/
│   ├── voice_samples/          # 録音した音声サンプル
│   └── corpus.txt              # 読み上げコーパス（ref_text 用）
├── models/
│   └── .gitkeep                # モデルキャッシュ（Hugging Face、オプションで明示保存）
├── logs/
│   ├── development-log.md     # 開発ログ
│   └── runtime-logs/          # 実行時ログ（アプリログ出力先）
├── tests/
│   ├── test_tts.py
│   ├── test_bot.py
│   └── test_audio.py
├── .env.example                # 環境変数テンプレート
├── .gitignore
├── README.md
└── requirements.txt
```

### 補足

- `data/voice_samples/`: 開発者が用意する参照音声（例: `my_voice.mp3`）。`data/corpus.txt` はその音声の読み上げ内容（ref_text）と対応させる。
- `models/`: Hugging Face のキャッシュをプロジェクト内に置く場合はここを使用。`technical-decisions.md` の方針に従う。
- `logs/runtime-logs/`: アプリケーションのログファイル出力先。`logger` の設定で指定する。

---

*本ドキュメントは設計フェーズの成果物として作成した。実装は `docs/technical-decisions.md` の未決定事項が確定してから開始する。*
