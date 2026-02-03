# Voice-clone-Qwen3-TTS

Qwen3-TTS（2026年1月公開）を用いて自分の声をクローンし、Discord上でテキストメッセージを自分の声で読み上げるボットを実現するプロジェクトです。

## プロジェクト概要

- **ゴール1**: 自分のボイスクローンモデルを作成する
- **ゴール2**: Discord読み上げボットに組み込む

## 技術スタック

- **TTS**: Qwen3-TTS-12Hz-1.7B-Base (Hugging Face)
- **Discord**: discord.py (Python)
- **実行環境**: WSL2/Ubuntu 24.04, CUDA 12.1, PyTorch 2.0+, RTX 4070 Ti (12GB VRAM)

## ディレクトリ構造

```
Voice-clone-Qwen3-TTS/
├── docs/           # ドキュメント
├── src/            # ソースコード
├── data/           # 音声サンプル
├── models/         # 学習済みモデル
├── logs/           # 実行ログ
├── tests/          # テストコード
├── .gitignore
├── README.md
└── requirements.txt
```

## セットアップ

詳細は [docs/setup.md](docs/setup.md) を参照してください。

## CLIツールの使い方

話者を選択し、任意のテキストで音声を合成するCLIツール（`src.tools.test_synthesis`）が利用できます。

### 話者一覧の確認

```bash
python -m src.tools.test_synthesis --list-speakers
```

### 音声合成

```bash
# 基本的な使い方
python -m src.tools.test_synthesis --speaker gohan --text "合成したいテキスト"

# 出力ファイルを指定
python -m src.tools.test_synthesis --speaker gohan --text "テキスト" --output outputs/my_voice.wav

# 英語で合成
python -m src.tools.test_synthesis --speaker gohan --text "Hello world" --language en
```

### オプション

| オプション | 説明 |
|------------|------|
| `--list-speakers` | 利用可能な話者一覧を表示 |
| `--speaker <名前>` | 話者名を指定（音声合成時必須） |
| `--text <テキスト>` | 合成するテキスト（音声合成時必須） |
| `--output <パス>` | 出力WAVファイルパス（デフォルト: `outputs/synthesis_YYYYMMDD_HHMMSS.wav`） |
| `--language <言語>` | 言語（`ja` / `en`、デフォルト: `ja`） |
| `--metadata <パス>` | メタデータCSVのパス（デフォルト: `data/metadata.csv`） |

## ドキュメント

- [プロジェクト仕様書（完全版）](docs/project-spec.md)
- [環境構築手順](docs/setup.md)
- [実装計画（Bolt Plan 01）](docs/bolt-plan-01.md)
- [開発ログ](logs/development-log.md)

## ライセンス

個人利用のみ。Qwen3-TTSはApache 2.0 License。
