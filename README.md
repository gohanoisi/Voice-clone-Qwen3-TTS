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

## ドキュメント

- [プロジェクト仕様書（完全版）](docs/project-spec.md)
- [環境構築手順](docs/setup.md)
- [実装計画（Bolt Plan 01）](docs/bolt-plan-01.md)
- [開発ログ](logs/development-log.md)

## ライセンス

個人利用のみ。Qwen3-TTSはApache 2.0 License。
