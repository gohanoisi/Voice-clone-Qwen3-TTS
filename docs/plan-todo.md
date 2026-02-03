# Plan TODO（Bolt Plan 01 タスク詳細化）

Bolt Plan 01 のタスク 4・5 をサブタスクに分解し、完了条件・所要時間・依存関係を明記する。実装時はこの順序で進める。

> **開発者の手動作業**（コーパステキスト、Discord Token など）の詳細は `docs/manual-tasks.md` を参照。

---

## 完了済みタスク（概要）

- **タスク1**: 環境構築
- **タスク2**: （スキップ）
- **タスク3**: （スキップ）
- **タスク4**: TTS 実装（公式サンプル）
- **タスク5**: 単一話者でのボイスクローン

---

## タスク 5.5: ドキュメント更新（現在のタスク）

**完了条件**: 以下の 5 ドキュメントがプロンプトの更新方針に沿って更新され、整合性が取れていること。

| ID | サブタスク | 完了条件 |
|----|------------|----------|
| 5.5-1 | `docs/project-spec.md` 更新 | 今回やること/やらないこと、用語の明確化、Discord レイテンシ対策を反映 |
| 5.5-2 | `docs/architecture.md` 更新 | データ構造変更、VoiceProfileManager・CLI、キャッシュ戦略を反映 |
| 5.5-3 | `docs/api-design.md` 更新 | VoiceProfileManager API、CLI インターフェースを追加 |
| 5.5-4 | `docs/technical-decisions.md` 更新 | 声プロファイル関連の決定事項テーブル、ファインチューニング方針を追加 |
| 5.5-5 | `docs/plan-todo.md` 更新 | タスク 5.5〜5.7、依存関係を反映（本タスク） |

### チェックリスト（タスク 5.5）

- [ ] 5.5-1. `docs/project-spec.md` 更新
- [ ] 5.5-2. `docs/architecture.md` 更新
- [ ] 5.5-3. `docs/api-design.md` 更新
- [ ] 5.5-4. `docs/technical-decisions.md` 更新
- [ ] 5.5-5. `docs/plan-todo.md` 更新

---

## タスク 5.6: 声プロファイル管理の実装

**完了条件**: VoiceProfileManager がメタデータを読み込み、話者一覧・プロファイル取得ができること。単体テストが通ること。

| ID | サブタスク | 完了条件 | 依存 |
|----|------------|----------|------|
| 5.6-1 | `data/metadata.csv` のスキーマ設計・サンプル作成 | カラム: sample_id, speaker_name, audio_path, corpus_text, language, description。サンプル行を 1 件以上用意 | タスク 5.5 完了 |
| 5.6-2 | `src/profile/voice_profile_manager.py` 実装 | VoiceProfileManager が `docs/api-design.md` のシグネチャに沿って定義され、list_speakers / get_profile / get_all_profiles が動作する | 5.6-1 |
| 5.6-3 | テストデータ作成 | 複数話者の音声サンプルを data/voice_samples に追加し、metadata.csv に登録（既存 my_voice を 001_gohan 等にリネームしても可） | 5.6-1 |
| 5.6-4 | 単体テスト実装 | `tests/test_voice_profile_manager.py` で list_speakers / get_profile 等をテスト | 5.6-2 |

### チェックリスト（タスク 5.6）

- [ ] 5.6-1. `data/metadata.csv` スキーマ・サンプル作成
- [ ] 5.6-2. `src/profile/voice_profile_manager.py` 実装
- [ ] 5.6-3. テストデータ作成（複数話者）
- [ ] 5.6-4. `tests/test_voice_profile_manager.py` 実装

---

## タスク 5.7: CLI ツール実装

**完了条件**: `python -m src.tools.test_synthesis --list-speakers` で話者一覧が表示され、`--speaker` + `--text` で音声が生成されること。

| ID | サブタスク | 完了条件 | 依存 |
|----|------------|----------|------|
| 5.7-1 | `src/tools/test_synthesis.py` 実装 | argparse、VoiceProfileManager 連携。--list-speakers / --speaker / --text / --output / --language をサポート | タスク 5.6 完了 |
| 5.7-2 | 動作確認 | 話者一覧表示、音声合成テストを手動で実施 | 5.7-1 |
| 5.7-3 | README 更新 | CLI ツールの使い方（上記コマンド例）を README に追記 | 5.7-2 |

### チェックリスト（タスク 5.7）

- [ ] 5.7-1. `src/tools/test_synthesis.py` 実装
- [ ] 5.7-2. 動作確認（話者一覧、音声合成）
- [ ] 5.7-3. README 更新

---

## タスク 6: Discord Bot 実装（変更なし）

既存のタスク 6 をそのまま維持する。Bot 実装時には VoiceProfileManager から話者プロファイルを取得し、TTS に渡す構成とする。

---

## 依存関係（全体）

```
タスク5 完了 → タスク5.5（Doc更新） → タスク5.6（プロファイル管理） → タスク5.7（CLI） → タスク6（Discord Bot）
```

---

## 元のタスク 4: Qwen3-TTS Base モデルでサンプル音声を生成する

**Bolt 上の完了条件**: 公式サンプル（ref_audio + ref_text）で WAV が出力される。

### サブタスク一覧

| ID | サブタスク | 完了条件 | 所要時間（目安） | 依存 |
|----|------------|----------|------------------|------|
| 4-1 | `src/tts/qwen_wrapper.py` を実装する | `Qwen3TTSWrapper` が `docs/api-design.md` のシグネチャに沿って定義され、`__init__` でモデルがロードできる | 30分 | なし |
| 4-2 | Qwen3-TTS-12Hz-1.7B-Base をロードする | `Qwen3TTSWrapper(model_name, device, dtype)` でモデルが正常にロードされ、VRAM 内で動作する（必要なら FlashAttention 2 を使用） | 15分 | 4-1 |
| 4-3 | 公式サンプル音声でテスト実行する | Qwen3-TTS 公式の ref_audio + ref_text で `generate_voice()` を呼び出し、例外なく (wav_array, sr) が返る | 20分 | 4-2 |
| 4-4 | 生成音声を `logs/test_audio/sample_output.wav` に保存する | 4-3 の出力を soundfile 等で WAV として保存し、ファイルが存在することを確認する | 10分 | 4-3 |
| 4-5 | 音声品質を主観評価する | 保存した WAV を再生し、聞き取り可能・自然であることを開発者が確認する。問題あればメモに残す | 15分 | 4-4 |

### チェックリスト（タスク 4）

- [ ] 4-1. `src/tts/qwen_wrapper.py` 実装
- [ ] 4-2. Qwen3-TTS-12Hz-1.7B-Base をロード
- [ ] 4-3. 公式サンプル音声でテスト実行
- [ ] 4-4. 生成音声を `logs/test_audio/sample_output.wav` に保存
- [ ] 4-5. 音声品質を主観評価

### 依存関係（タスク 4）

```
4-1 → 4-2 → 4-3 → 4-4 → 4-5
```

---

## 元のタスク 5: 自分の音声サンプルでボイスクローンを試す

**Bolt 上の完了条件**: data/ に配置した音声からクローン音声が生成される。

### サブタスク一覧

| ID | サブタスク | 完了条件 | 所要時間（目安） | 依存 |
|----|------------|----------|------------------|------|
| 5-1 | `data/voice_samples/my_voice.mp3` を用意する | コーパステキスト（後述 5-2）を読み上げて録音した音声を MP3 で配置する。Qwen3-TTS が読める形式であれば WAV 等でも可 | 20分 | なし（5-2 と並行可） |
| 5-2 | `data/corpus.txt` にコーパステキストを記述する | 5-1 の録音内容と完全に一致するテキストを 1 ファイルに記載する（ref_text として使用）。`technical-decisions.md` で B 採用のため手動で一致させる | 10分 | なし（5-1 と並行可） |
| 5-3 | `src/tts/voice_clone.py` を実装する | `VoiceCloneManager` が `Qwen3TTSWrapper` と ref_audio_path / ref_text を受け取り、`synthesize(text, language)` で音声を返す（`docs/api-design.md` に準拠） | 25分 | タスク 4 完了（4-5） |
| 5-4 | ボイスクローンを実行する（ref_audio + ref_text → WAV） | `VoiceCloneManager` に `data/voice_samples/my_voice.mp3` と `data/corpus.txt` の内容を渡し、任意の日本語テキストで WAV が生成される | 15分 | 5-1, 5-2, 5-3 |
| 5-5 | 生成音声を主観評価する | 生成 WAV を再生し、「本人の声」と認識できるか開発者が確認する。友人に聞いてもらってもよい | 15分 | 5-4 |
| 5-6 | 必要に応じてサンプルを再録音する | 品質が不足している場合のみ実施。録音条件（環境ノイズ・長さ・発音）を見直し、5-1 をやり直す | 20分 | 5-5（条件付き） |

### チェックリスト（タスク 5）

- [ ] 5-1. `data/voice_samples/my_voice.mp3` を用意
- [ ] 5-2. `data/corpus.txt` にコーパステキストを記述
- [ ] 5-3. `src/tts/voice_clone.py` 実装
- [ ] 5-4. ボイスクローン実行（ref_audio + ref_text → WAV）
- [ ] 5-5. 生成音声を主観評価
- [ ] 5-6. 必要に応じてサンプル再録音

### 依存関係（タスク 5）

```
5-1 ─┐
     ├→ 5-4 → 5-5 → 5-6（条件付き）
5-2 ─┘
       ↑
タスク4完了 → 5-3 ─┘
```

---

## 技術選定との対応

- **ref_text**: `docs/technical-decisions.md` で B（コーパステキスト手動）を採用しているため、5-2 の `data/corpus.txt` と 5-1 の録音内容を手動で一致させる。
- **一時保存場所**: B 採用のため、実装では `logs/temp_audio/` を使用する（タスク 4・5 ではテスト用に `logs/test_audio/` も使用）。
- **モデルキャッシュ**: A 採用のため、Hugging Face デフォルト（`~/.cache/huggingface/`）を使用する。

---

## 実行ログ

サブタスクの実施・完了は `logs/development-log.md` に記録する。

---

## metadata.csv スキーマ例（参考）

```text
sample_id,speaker_name,audio_path,corpus_text,language,description
001,gohan,data/voice_samples/001_gohan.mp3,"こんにちは、私の名前はゴハンです。これはボイスクローンのテストです。天気予報によると、今日は晴れのち曇りで、最高気温は15度になるそうです。",ja,メインの声プロファイル
002,gohan,data/voice_samples/002_gohan_long.mp3,"...(長めのコーパス)...",ja,長文サンプル
003,friend_a,data/voice_samples/003_friend_a.mp3,"こんにちは。友人Aです。テストをしています。",ja,友人Aの声
```
