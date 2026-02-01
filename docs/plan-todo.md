# Plan TODO（Bolt Plan 01 タスク詳細化）

Bolt Plan 01 のタスク 4・5 をサブタスクに分解し、完了条件・所要時間・依存関係を明記する。実装時はこの順序で進める。

> **開発者の手動作業**（コーパステキスト、Discord Token など）の詳細は `docs/manual-tasks.md` を参照。

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
