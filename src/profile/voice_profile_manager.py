# coding=utf-8
"""
声プロファイル（ref_audio + ref_text）の管理。

metadata.csv を読み込み、話者一覧・プロファイル取得を提供する。
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

# 必須カラム
REQUIRED_COLUMNS = ("sample_id", "speaker_name", "audio_path", "corpus_text", "language")
VALID_LANGUAGES = ("ja", "en")


class VoiceProfileManager:
    """
    声プロファイル（ref_audio + ref_text）の管理。
    """

    def __init__(self, metadata_path: str = "data/metadata.csv") -> None:
        """
        Args:
            metadata_path: メタデータファイルのパス（CSV）

        Raises:
            FileNotFoundError: メタデータファイルが存在しない
            ValueError: メタデータの形式が不正（必須カラムがない等）
        """
        path = Path(metadata_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"メタデータファイルが存在しません: {metadata_path}")

        # プロジェクトルート（data/metadata.csv なら data の親）
        self._root = path.parent.parent
        self._metadata_path = path
        self._rows: List[Dict[str, str]] = []

        with open(path, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError("メタデータが空です")
            missing = set(REQUIRED_COLUMNS) - set(reader.fieldnames)
            if missing:
                raise ValueError(f"必須カラムがありません: {missing}")

            for i, row in enumerate(reader):
                # 空行スキップ
                if not any(row.get(k, "").strip() for k in REQUIRED_COLUMNS):
                    continue
                # 必須フィールドの存在チェック
                for col in REQUIRED_COLUMNS:
                    if not (row.get(col) or "").strip():
                        raise ValueError(
                            f"行 {i + 2}: 必須カラム '{col}' が空です"
                        )
                lang = (row.get("language") or "").strip().lower()
                if lang not in VALID_LANGUAGES:
                    raise ValueError(
                        f"行 {i + 2}: language は 'ja' または 'en' である必要があります: {lang!r}"
                    )
                audio_path = (row.get("audio_path") or "").strip()
                full_audio = self._root / audio_path
                if not full_audio.exists():
                    raise ValueError(
                        f"行 {i + 2}: 音声ファイルが存在しません: {audio_path}"
                    )
                self._rows.append(row)

    def list_speakers(self) -> List[str]:
        """
        利用可能な話者名の一覧を返す（重複なし）。

        Returns:
            話者名のリスト（例: ["gohan", "friend_a"]）
        """
        names = [r.get("speaker_name", "").strip() for r in self._rows]
        return list(dict.fromkeys(n for n in names if n))

    def get_profile(self, speaker_name: str) -> Dict[str, Any]:
        """
        指定した話者の声プロファイルを取得（最初の1件）。

        Args:
            speaker_name: 話者名

        Returns:
            sample_id, speaker_name, audio_path, corpus_text, language, description を含む辞書

        Raises:
            ValueError: 話者名が見つからない
        """
        profiles = self.get_all_profiles(speaker_name)
        return profiles[0]

    def get_all_profiles(self, speaker_name: str) -> List[Dict[str, Any]]:
        """
        指定した話者の全サンプルを取得（複数音声サンプルがある場合）。

        Args:
            speaker_name: 話者名

        Returns:
            声プロファイルのリスト（各要素は get_profile と同じ形式）

        Raises:
            ValueError: 話者名が見つからない
        """
        name = speaker_name.strip()
        profiles = [
            {
                "sample_id": r.get("sample_id", "").strip(),
                "speaker_name": r.get("speaker_name", "").strip(),
                "audio_path": r.get("audio_path", "").strip(),
                "corpus_text": r.get("corpus_text", "").strip(),
                "language": r.get("language", "").strip().lower(),
                "description": (r.get("description") or "").strip(),
            }
            for r in self._rows
            if (r.get("speaker_name") or "").strip() == name
        ]
        if not profiles:
            raise ValueError(f"話者名が見つかりません: {speaker_name!r}")
        return profiles
