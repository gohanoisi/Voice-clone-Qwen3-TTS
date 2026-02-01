# 手動でやること（開発者の作業）

実装フェーズに入る前に、**開発者が手動で実施すべき作業**をまとめる。各作業の判断・方針を記録する。

---

## 必須作業

### 作業1: 音声サンプル録音用のコーパステキスト作成

| 項目 | 内容 |
|------|------|
| **ファイル** | `data/corpus.txt` |
| **内容** | 録音時に読み上げるテキスト（日本語・英語） |
| **推奨サンプル** | 下記参照 |
| **開発者の判断** | 推奨サンプルを使用する。公式ドキュメントや先人が試した良いコーパスがあれば使いたかったが、関係ないならそれでよい |

**推奨サンプル**（`data/corpus.txt` の初期内容）:

```
こんにちは、私の名前はゴハンです。これはボイスクローンのテストです。
天気予報によると、今日は晴れのち曇りで、最高気温は15度になるそうです。
Hello, my name is Gohan. This is a voice cloning test.
According to the weather forecast, it will be sunny then cloudy today.
```

---

### 作業2: Discord Bot Token の取得

| 項目 | 内容 |
|------|------|
| **必要なタイミング** | タスク6（Discord bot 実装）の前 |
| **開発者の判断** | タスク6の前に取得する予定。Discord ボットの権限や設定もその時に検討する（最適な設定はその時に考える） |

**手順**:

1. [Discord Developer Portal](https://discord.com/developers/applications) にアクセス
2. 「New Application」でアプリ作成
3. 「Bot」タブで Bot を作成し、Token をコピー
4. `.env` ファイルに保存:

```bash
cd /home/gohan/dev/Voice-clone-Qwen3-TTS
echo "DISCORD_TOKEN=your_bot_token_here" > .env
```

> **補足**: Discord ボットの権限・設定（Intents、スラッシュコマンドの登録など）はタスク6着手時に検討する。

---

## 任意作業（後でもOK）

### 作業3: 読み上げコーパスのバリエーション追加

音声品質を向上させるため、以下を追加することが推奨される：

- 感情表現（驚き、疑問、断定）
- 長文・短文のバリエーション
- 数字・固有名詞

| 項目 | 内容 |
|------|------|
| **開発者の判断** | 初回テスト後に改善する。まずは MVP として、自分の声をクローンできるかどうかが優先 |

---

## 関連ドキュメント

- `docs/setup.md` - 環境構築（Discord Token の設定手順を含む）
- `docs/plan-todo.md` - タスク 5-2 で `data/corpus.txt` を参照
- `docs/bolt-plan-01.md` - タスク6の前後に Discord 関連作業が必要
