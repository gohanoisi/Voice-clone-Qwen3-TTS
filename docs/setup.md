# 環境構築手順書

WSL2/Ubuntu 24.04 での Voice-clone-Qwen3-TTS 環境構築手順です。

> **開発者が手動で行う作業**（コーパステキスト作成、Discord Token 取得など）の一覧は `docs/manual-tasks.md` を参照。

## 前提条件

- **OS**: WSL2 / Ubuntu 24.04 (noble)
- **GPU**: NVIDIA RTX 4070 Ti (12GB VRAM)
- **メモリ**: 64GB
- **CPU**: 13th Gen Intel Core i7-13700F

## 1. システム準備

### 1.1 NVIDIA ドライバ・CUDA 確認

```bash
# NVIDIA ドライバ確認
nvidia-smi

# CUDA 12.1 が表示されることを確認
```

CUDA が未インストールの場合、[NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads) からインストールしてください。

### 1.2 必要なパッケージのインストール

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip git
```

## 2. Python 仮想環境の作成

```bash
cd /home/gohan/dev/Voice-clone-Qwen3-TTS

# 仮想環境作成（Python 3.12 推奨）
python3.12 -m venv .venv

# 有効化
source .venv/bin/activate
```

## 3. PyTorch（CUDA 12.1）のインストール

```bash
# CUDA 12.1 用 PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## 4. Qwen3-TTS のインストール

```bash
# 公式 qwen-tts パッケージ
pip install -U qwen-tts
```

### 4.1 FlashAttention 2（オプション・推奨）

VRAM 節約・高速化のため、12GB VRAM 環境では推奨です。

```bash
# FlashAttention 2（ビルドに時間がかかります）
pip install -U flash-attn --no-build-isolation

# メモリやCPUコアが少ない場合
# MAX_JOBS=4 pip install -U flash-attn --no-build-isolation
```

> 注意: FlashAttention 2 は対応 GPU が必要です。RTX 4070 Ti は対応しています。

## 5. その他依存パッケージ

```bash
pip install -r requirements.txt
```

または個別に:

```bash
pip install soundfile numpy discord.py
```

## 6. 環境変数の設定

### 6.1 Discord Bot Token

Discord Developer Portal で Bot を作成し、トークンを取得してください。

```bash
# .env ファイルを作成（リポジトリにコミットしない）
echo "DISCORD_TOKEN=your_bot_token_here" > .env
```

または `export` で設定:

```bash
export DISCORD_TOKEN="your_bot_token_here"
```

### 6.2 Hugging Face（オプション）

プライベートモデルやレート制限緩和が必要な場合:

```bash
# Hugging Face にログイン
pip install -U huggingface_hub
huggingface-cli login
```

## 7. ディレクトリ構造の確認

```bash
# 必要ディレクトリの存在確認
ls -la docs/ src/ data/ models/ logs/ tests/
```

## 8. 動作確認

### 8.1 Qwen3-TTS の簡易テスト

```python
# test_tts.py
import torch
from qwen_tts import Qwen3TTSModel

model = Qwen3TTSModel.from_pretrained(
    "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
    device_map="cuda:0",
    dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",  # FlashAttention 導入時
)
print("Qwen3-TTS loaded successfully!")
```

```bash
python test_tts.py
```

### 8.2 Discord.py の簡易テスト

```python
# test_discord.py
import discord
print(f"discord.py version: {discord.__version__}")
```

## 9. トラブルシューティング

| 現象 | 対策 |
|------|------|
| `CUDA out of memory` | 0.6B モデルを使用、または FlashAttention 2 を導入 |
| `ModuleNotFoundError: qwen_tts` | `pip install -U qwen-tts` を再実行 |
| FlashAttention ビルド失敗 | `MAX_JOBS=4` で並列度を下げる、または FlashAttention をスキップ |
| Discord bot が起動しない | `DISCORD_TOKEN` が正しく設定されているか確認 |
| モデルダウンロードが遅い | `HF_ENDPOINT` や プロキシ設定を確認 |

## 10. 参考リンク

- [Qwen3-TTS Hugging Face](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base)
- [Qwen3-TTS 公式リポジトリ](https://github.com/QwenLM/Qwen3-TTS)
- [Qwen3-TTS 日本語環境での攻略（Qiita）](https://qiita.com/GeneLab_999/items/79d8020799c6f9e329dc)
- [discord.py ドキュメント](https://discordpy.readthedocs.io/)
