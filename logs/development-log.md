# 開発ログ

Cursor がアクションを取るたびに、以下を記録します。

- **日時**
- **実施内容**
- **結果**
- **次のアクション**

---

## ログ履歴

### 2025-02-02

#### [時刻] プロジェクト初期化

- **実施内容**:
  - `docs/project-spec.md` 完全版ドキュメント作成（AI-DLCメタデータ・要求定義・要件定義を統合）
  - GitHub リポジトリ用の初期ディレクトリ構造作成（docs/, src/, data/, models/, logs/, tests/）
  - `.gitignore`, `README.md`, `requirements.txt` 作成
  - `docs/setup.md` 環境構築手順書作成
  - `docs/bolt-plan-01.md` 実装計画（Bolt Plan 01）作成
  - `logs/development-log.md` ログ管理仕組み構築

- **結果**: タスク1〜5 を完了。プロジェクトの土台が整った。

- **次のアクション**:
  1. 開発者による確認
  2. Bolt Plan 01 のタスク1（仮想環境構築）から実装開始
  3. 必要に応じて `docs/prompts.md`, `docs/learnings.md` を追加

---

### 2026-02-02

#### [02:11] Bolt Plan 01 タスク1: 仮想環境構築

- **実施内容**:
  1. プロジェクトディレクトリ `/home/gohan/dev/Voice-clone-Qwen3-TTS` で `.venv` を作成（Python 3.12.3）
  2. PyTorch 2.5.1+cu121（CUDA 12.1）をインストール
  3. qwen-tts, soundfile, discord.py および依存パッケージをインストール
  4. CUDA/PyTorch 動作確認: RTX 4070 Ti 認識済み
  5. qwen_tts, discord.py, soundfile のインポート確認完了

- **結果**: タスク1 完了。仮想環境構築と依存パッケージインストールが成功。

- **環境情報**:
  - リポジトリ: `/home/gohan/dev/Voice-clone-Qwen3-TTS`
  - Python: 3.12.3
  - PyTorch: 2.5.1+cu121
  - CUDA: 12.1, RTX 4070 Ti
  - qwen-tts: 0.0.5
  - discord.py: 2.6.4

- **補足・注意**:
  - SoX 未インストール: `sudo apt install sox` で導入可能（qwen-tts の一部機能で使用）
  - FlashAttention 2 未導入: VRAM 節約が必要な場合に `pip install flash-attn --no-build-isolation` を検討

- **次のアクション**:
  1. Bolt Plan 01 タスク2: FlashAttention 2 のインストール（オプション）
  2. Bolt Plan 01 タスク4: Qwen3-TTS Base モデルでサンプル音声生成の検証

---

#### [02:30] 設計フェーズ開始

- **実施内容**:
  - アーキテクチャ設計書作成（`docs/architecture.md`）
  - API 設計書作成（`docs/api-design.md`）
  - 技術選定の最終確認（`docs/technical-decisions.md`）
  - Plan TODO 詳細化（`docs/plan-todo.md`）

- **結果**:
  - 実装前の設計ドキュメントが揃った
  - 未決定事項は開発者により判断・確定済み（ref_text 手動 / Bot 起動は `python -m src.bot.main` / 一時保存は `logs/temp_audio/` / モデルキャッシュは HF デフォルト）

- **次のアクション**:
  1. Bolt Plan 01 のタスク 4（TTS 実装）に着手（`docs/plan-todo.md` の 4-1 から）
  2. 必要に応じて `docs/architecture.md`・`docs/api-design.md` に技術選定の反映を追記

---

#### [14:00] タスク4-1: `src/tts/qwen_wrapper.py` 実装

- **実施内容**:
  1. `src/tts/` ディレクトリを作成
  2. `docs/api-design.md` の「2.1 TTS Module API」に沿い、`src/tts/qwen_wrapper.py` を実装
  3. `Qwen3TTSWrapper` クラス: `__init__`（モデルロード）、`generate_voice`（音声生成）、`_load_ref_audio`（参照音声読み込み）
  4. エラーハンドリング: `FileNotFoundError`, `ValueError`, `RuntimeError` を仕様どおり送出
  5. 参照音声は `torchaudio.load` で WAV/MP3 等を読み込み、(wav, sr) 形式で Qwen3-TTS に渡す

- **結果**:
  - `Qwen3TTSWrapper` クラス定義完了
  - `__init__` で `Qwen3TTSModel.from_pretrained` によりモデルロード可能
  - `generate_voice` でボイスクローン音声生成の API を実装
  - 構文エラーなし、`from src.tts import Qwen3TTSWrapper` で import 可能

- **次のアクション**:
  - タスク4-2: Qwen3-TTS-12Hz-1.7B-Base のモデルロード動作確認

---

#### [時刻] タスク4-2: Qwen3-TTS モデルロード動作確認

- **実施内容**:
  1. `tests/test_qwen_tts_load.py` を作成
  2. `Qwen3TTSWrapper` のインスタンス化（model_name, device, dtype 指定）によるモデルロード動作確認
  3. VRAM 使用量の表示（torch.cuda.memory_allocated() / reserved()）
  4. エラーハンドリング確認: 不正な model_name で RuntimeError、空の model_name で ValueError

- **結果**: タスク4-2 完了。全 3 テスト成功。

- **実行結果サマリ**:
  | 項目 | 値 |
  |------|-----|
  | モデル | Qwen/Qwen3-TTS-12Hz-1.7B-Base |
  | デバイス | cuda (RTX 4070 Ti) |
  | dtype | torch.bfloat16 |
  | モデルロード | 成功 |
  | VRAM 使用量（ロード後） | 使用中: 4004.46 MB / 予約: 4134.00 MB |
  | 所要時間 | 約 55 秒（初回ダウンロード含む） |
  | 不正 model_name | RuntimeError 発生（期待どおり） |
  | 空 model_name | ValueError 発生（期待どおり） |

- **補足・警告**（動作に影響なし）:
  - SoX 未インストール: qwen-tts の一部機能で使用。`sudo apt install sox` で導入可能
  - flash-attn 未導入: 推論速度向上のため `pip install flash-attn --no-build-isolation` を検討

- **成果物**:
  - `tests/test_qwen_tts_load.py`
  - `tests/__init__.py`（パッケージ化のため追加）

- **次のアクション**:
  - タスク4-3: 公式サンプル音声でテスト実行（ref_audio + ref_text で generate_voice を呼び出し）

---

#### [時刻] タスク4-3: 公式サンプル音声による音声生成テスト

- **実施内容**:
  1. `tests/test_qwen_tts_generate.py` を作成
  2. `Qwen3TTSWrapper.generate_voice` を公式サンプル（ref_audio + ref_text）で実行
  3. 生成音声を `outputs/test_generated.wav` に保存
  4. `src/tts/qwen_wrapper.py` に URL 対応を追加（ref_audio_path が http(s) の場合はモデルに直接渡す）
  5. 公式 URL が 403 の場合は gTTS で ref_text から参照音声を生成するフォールバックを実装

- **結果**: タスク4-3 完了。音声生成に成功。

- **実行結果サマリ**:
  | 項目 | 値 |
  |------|-----|
  | 参照音声 | gTTS で生成（公式 URL は 403 のためフォールバック） |
  | ref_text | "Okay. Yeah. I resent you. I love you. ..." |
  | 生成テキスト | "This is a test of voice cloning with Qwen3-TTS. ..." |
  | モデルロード時間 | 約 8 秒 |
  | 音声生成時間 | 15.50 秒 |
  | 音声の長さ | 6.63 秒 |
  | リアルタイム係数 (RTF) | 2.34x |
  | VRAM（モデルロード後） | 4004.46 MB |
  | VRAM（生成後） | 4044.59 MB / 予約 4868 MB |
  | 出力ファイル | `outputs/test_generated.wav` |

- **補足**:
  - 公式サンプル URL (`qianwen-res.oss-cn-beijing.aliyuncs.com`) は 403 を返すため、gTTS で英語 ref_text から音声を生成して使用
  - 手動で公式 clone.wav を `data/samples/clone.wav` に配置すれば、より高品質なボイスクローンが期待できる

- **成果物**:
  - `tests/test_qwen_tts_generate.py`
  - `outputs/test_generated.wav`（生成音声）
  - `src/tts/qwen_wrapper.py` の URL 対応

- **次のアクション**:
  - タスク5: 自分の音声でのボイスクローン（data/voice_samples/my_voice.mp3 + data/corpus.txt）

---

#### [時刻] タスク5-3 & 5-4: VoiceCloneManager 実装・ボイスクローン実行テスト

- **実施内容**:
  1. `src/tts/voice_clone.py` を作成し、`VoiceCloneManager` クラスを実装
  2. `__init__`: ref_audio_path, ref_text, language を受け取り、内部で Qwen3TTSWrapper をインスタンス化
  3. `synthesize(text, language="ja")`: テキストを受け取り (wav_array, sample_rate) を返す
  4. エラーハンドリング: FileNotFoundError（参照音声なし）、ValueError（不正なパラメータ）、RuntimeError（推論失敗）
  5. `src/tts/__init__.py` に `VoiceCloneManager` をエクスポート追加
  6. `tests/test_voice_clone.py` を作成し、data/voice_samples/my_voice.mp3 と data/corpus.txt でボイスクローン実行
  7. 生成音声を `outputs/voice_clone_test.wav` に保存
  8. エラーハンドリング確認（ref_audio_path 不正 → FileNotFoundError、ref_text 空 → ValueError）

- **結果**: タスク5-3・5-4 完了。VoiceCloneManager のインスタンス化・synthesize・音声保存・エラーハンドリングが正常に動作。

- **実行結果サマリ**:
  | 項目 | 値 |
  |------|-----|
  | 参照音声 | data/voice_samples/my_voice.mp3 |
  | コーパス | data/corpus.txt（197 文字） |
  | 生成テキスト | 「今日はいい天気ですね。ボイスクローンのテストです。」 |
  | モデルロード時間 | 7.70 秒 |
  | 音声生成時間 | 14.11 秒 |
  | 音声の長さ | 3.59 秒 |
  | リアルタイム係数 (RTF) | 3.93x |
  | VRAM（モデルロード後） | 4004.46 MB |
  | VRAM（生成後） | 4044.59 MB / 予約 5196 MB |
  | 出力ファイル | `outputs/voice_clone_test.wav` |
  | エラー | なし |

- **動作確認項目**:
  - [x] VoiceCloneManager が正常にインスタンス化できるか → 成功
  - [x] synthesize() が正常に音声を生成するか → 成功
  - [x] 生成された音声が保存されるか → outputs/voice_clone_test.wav に保存
  - [x] エラーハンドリング（ref_audio_path 不正、ref_text 空）が動作するか → FileNotFoundError / ValueError 発生確認

- **成果物**:
  - `src/tts/voice_clone.py`（VoiceCloneManager 実装）
  - `src/tts/__init__.py`（VoiceCloneManager エクスポート追加）
  - `tests/test_voice_clone.py`（ボイスクローン実行テスト・エラーハンドリング確認）
  - `outputs/voice_clone_test.wav`（生成音声）

- **次のアクション**:
  - タスク5-5: 主観評価（outputs/voice_clone_test.wav を再生し、声質・自然さを確認）
  - タスク6: Discord bot 実装

---

### 2026-02-03

#### [時刻] タスク5.5: ドキュメント更新

- **実施内容**:
  1. `docs/project-spec.md` 更新（今回やることに複数話者・声プロファイル管理・話者選択・テスト合成を追加、やらないことから「複数人の声のクローン」を削除、用語の明確化、Discord レイテンシ対策を追記）
  2. `docs/architecture.md` 更新（データ構造変更・VoiceProfileManager・CLI ツール・キャッシュ戦略・データフロー追加、ディレクトリ構造に profile/・tools/・metadata.csv を反映）
  3. `docs/api-design.md` 更新（Voice Profile Management Module API・VoiceProfileManager クラス、CLI Tool Interface を追加、セクション番号を 2.1〜2.7 に整理、モジュール間呼び出しに Profile・CLI を追加）
  4. `docs/technical-decisions.md` 更新（声プロファイル管理方式・メタデータ形式・テスト合成 UI・モデル永続化・Discord レイテンシ対策の決定事項テーブル、ファインチューニング方針を追加）
  5. `docs/plan-todo.md` 更新（完了済みタスク概要、タスク5.5〜5.7のサブタスク・チェックリスト・依存関係、metadata.csv スキーマ例を追加）

- **結果**: タスク5.5 完了。5 つのドキュメントがプロンプトの更新方針に沿って更新され、用語・相互参照の整合性を確認した。

- **成果物**:
  - `docs/project-spec.md` 更新版
  - `docs/architecture.md` 更新版
  - `docs/api-design.md` 更新版
  - `docs/technical-decisions.md` 更新版
  - `docs/plan-todo.md` 更新版

- **次のアクション**:
  1. タスク5.6: 声プロファイル管理の実装（metadata.csv スキーマ・VoiceProfileManager・テスト）
  2. タスク5.7: CLI ツール実装（test_synthesis）
  3. タスク6: Discord Bot 実装

---

#### [時刻] タスク5.6: 声プロファイル管理の実装

- **実施内容**:
  1. **5.6-1** `data/metadata.csv` のスキーマ設計・サンプル作成（sample_id, speaker_name, audio_path, corpus_text, language, description）。既存の `my_voice.mp3` と `corpus.txt` を参照する1件のサンプルを登録。
  2. **5.6-2** `src/profile/voice_profile_manager.py` に `VoiceProfileManager` を実装（`__init__`, `list_speakers`, `get_profile`, `get_all_profiles`）。`csv.DictReader` で読み込み、必須カラム・音声ファイル存在・language 妥当性を検証。`src/profile/__init__.py` でエクスポート。
  3. **5.6-3** テストデータは既存データのみで進める方針のためスキップ。
  4. **5.6-4** `tests/test_voice_profile_manager.py` で単体テストを実装（正常系: 読み込み・話者一覧・プロファイル取得・全プロファイル取得、異常系: メタデータ不在 → FileNotFoundError、必須カラム欠如・存在しない話者 → ValueError）。

- **結果**: タスク5.6 完了。全8件のテストがパス。

- **テスト実行結果**:
  ```
  tests/test_voice_profile_manager.py::test_init_loads_metadata PASSED
  tests/test_voice_profile_manager.py::test_list_speakers PASSED
  tests/test_voice_profile_manager.py::test_get_profile PASSED
  tests/test_voice_profile_manager.py::test_get_all_profiles PASSED
  tests/test_voice_profile_manager.py::test_get_profile_not_found PASSED
  tests/test_voice_profile_manager.py::test_get_all_profiles_not_found PASSED
  tests/test_voice_profile_manager.py::test_metadata_not_found PASSED
  tests/test_voice_profile_manager.py::test_init_missing_required_columns PASSED
  8 passed in 0.02s
  ```

- **動作確認項目**:
  - [x] `VoiceProfileManager("data/metadata.csv")` でインスタンス化できること → 成功
  - [x] `list_speakers()` で `["gohan"]` が返ること → 成功
  - [x] `get_profile("gohan")` で正しいプロファイルが返ること → 成功
  - [x] 異常系（メタデータ不在・必須カラム欠如・存在しない話者）で適切な例外 → 成功

- **成果物**:
  - `data/metadata.csv`（スキーマ + サンプル1件）
  - `src/profile/__init__.py`
  - `src/profile/voice_profile_manager.py`（VoiceProfileManager）
  - `tests/test_voice_profile_manager.py`（単体テスト8件）

- **次のアクション**:
  1. タスク5.7: CLI ツール実装（test_synthesis）
  2. タスク6: Discord Bot 実装

---

#### [時刻] タスク5.7: CLIツール実装

- **実施内容**:
  1. **5.7-1** `src/tools/test_synthesis.py` を実装（argparse: `--list-speakers`, `--speaker`, `--text`, `--output`, `--language`, `--metadata`）。話者一覧表示モードと音声合成モードを分岐。VoiceProfileManager でプロファイル取得 → VoiceCloneManager で合成 → soundfile.write で保存。デフォルト出力: `outputs/synthesis_YYYYMMDD_HHMMSS.wav`。エラーハンドリング: 必須引数不足・話者未検出・メタデータ不在・音声生成失敗。
  2. **5.7-2** 動作確認: `--list-speakers` で話者一覧表示、`--speaker gohan --text "テストです" --output outputs/cli_test.wav` で音声合成・保存、存在しない話者・必須引数不足で適切なエラーメッセージを確認。
  3. **5.7-3** `README.md` に「CLIツールの使い方」セクションを追加（話者一覧・音声合成コマンド例・オプション一覧）。

- **結果**: タスク5.7 完了。CLIツールが仕様どおり動作。

- **動作確認結果**:
  | 項目 | 結果 |
  |------|------|
  | `--list-speakers` | 利用可能な話者: gohan を表示 |
  | 音声合成（--speaker gohan --text "テストです" --output outputs/cli_test.wav） | 約15秒で完了、outputs/cli_test.wav に保存 |
  | 存在しない話者（--speaker unknown） | エラー: 話者 'unknown' が見つかりません。利用可能な話者: gohan |
  | 必須引数不足（--text なし） | エラー: 音声合成には --text を指定してください。 |

- **成果物**:
  - `src/tools/__init__.py`
  - `src/tools/test_synthesis.py`（CLIツール）
  - `README.md` 更新（CLIツールの使い方）
  - `outputs/cli_test.wav`（動作確認で生成した音声）

- **次のアクション**:
  1. タスク6: Discord Bot 実装
