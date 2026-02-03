# coding=utf-8
"""
タスク5.6-4: VoiceProfileManager 単体テスト

正常系: __init__, list_speakers, get_profile, get_all_profiles
異常系: メタデータ不在 → FileNotFoundError, 必須カラム欠如 → ValueError,
       存在しない話者 → ValueError

実行方法:
    cd /home/gohan/dev/Voice-clone-Qwen3-TTS
    python -m pytest tests/test_voice_profile_manager.py -v

または:
    python -m tests.test_voice_profile_manager
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

# プロジェクトルートをパスに追加
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import pytest

from src.profile import VoiceProfileManager


# メタデータパス（プロジェクトルート基準）
METADATA_PATH = _PROJECT_ROOT / "data" / "metadata.csv"


def test_init_loads_metadata():
    """__init__: metadata.csv の正常な読み込み"""
    manager = VoiceProfileManager(str(METADATA_PATH))
    assert manager._rows
    assert len(manager.list_speakers()) >= 1


def test_list_speakers():
    """話者一覧の取得"""
    manager = VoiceProfileManager(str(METADATA_PATH))
    speakers = manager.list_speakers()
    assert "gohan" in speakers
    assert len(speakers) >= 1


def test_get_profile():
    """声プロファイルの取得"""
    manager = VoiceProfileManager(str(METADATA_PATH))
    profile = manager.get_profile("gohan")
    assert profile["speaker_name"] == "gohan"
    assert "sample_id" in profile
    assert "audio_path" in profile
    assert "corpus_text" in profile
    assert profile["language"] in ("ja", "en")
    assert (Path(profile["audio_path"])).name.endswith(".mp3") or profile["audio_path"].endswith(".mp3")


def test_get_all_profiles():
    """指定話者の全プロファイル取得（1件）"""
    manager = VoiceProfileManager(str(METADATA_PATH))
    profiles = manager.get_all_profiles("gohan")
    assert len(profiles) >= 1
    assert all(p["speaker_name"] == "gohan" for p in profiles)
    assert profiles[0]["sample_id"] == "001"


def test_get_profile_not_found():
    """存在しない話者 → ValueError"""
    manager = VoiceProfileManager(str(METADATA_PATH))
    with pytest.raises(ValueError, match="話者名が見つかりません"):
        manager.get_profile("nonexistent_speaker")


def test_get_all_profiles_not_found():
    """存在しない話者で get_all_profiles → ValueError"""
    manager = VoiceProfileManager(str(METADATA_PATH))
    with pytest.raises(ValueError, match="話者名が見つかりません"):
        manager.get_all_profiles("nonexistent_speaker")


def test_metadata_not_found():
    """メタデータファイルが存在しない → FileNotFoundError"""
    with pytest.raises(FileNotFoundError, match="メタデータファイルが存在しません"):
        VoiceProfileManager("nonexistent.csv")


def test_init_missing_required_columns():
    """必須カラムがないCSV → ValueError"""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, encoding="utf-8"
    ) as f:
        f.write("wrong_col_a,wrong_col_b\n")
        f.write("a,b\n")
        tmp_path = f.name
    try:
        with pytest.raises(ValueError, match="必須カラムがありません"):
            VoiceProfileManager(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
