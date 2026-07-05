from __future__ import annotations

from pathlib import Path

import pytest

import replay.cli as cli_mod
from replay.schema import ReplayValidationError


@pytest.fixture()
def temp_private_dirs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> list[Path]:
    monkeypatch.chdir(tmp_path)
    private_dirs = [tmp_path / "data" / "raw", tmp_path / "data" / "private"]
    for private_dir in private_dirs:
        private_dir.mkdir(parents=True)
    monkeypatch.setattr(cli_mod, "PRIVATE_DIRS", private_dirs)
    return private_dirs


@pytest.mark.parametrize("private_dir", ["raw", "private"])
def test_guard_refuses_paths_under_private_dirs(
    temp_private_dirs: list[Path], private_dir: str
) -> None:
    with pytest.raises(ReplayValidationError, match="refusing to read or write private path"):
        cli_mod._guard_public_path(Path("data") / private_dir / "draft.md")


def test_guard_allows_ordinary_public_path(temp_private_dirs: list[Path]) -> None:
    cli_mod._guard_public_path(Path("negotiations") / "2026-07-example.md")


def test_guard_allows_path_that_only_shares_private_dir_prefix(
    temp_private_dirs: list[Path],
) -> None:
    cli_mod._guard_public_path(Path("data") / "raw-backup" / "draft.md")


@pytest.mark.parametrize("command", ["redact-check", "validate", "show"])
@pytest.mark.parametrize("private_dir", ["raw", "private"])
def test_main_refuses_private_paths_for_file_commands(
    temp_private_dirs: list[Path],
    tmp_path: Path,
    command: str,
    private_dir: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    private_path = tmp_path / "data" / private_dir / "draft.md"
    private_path.write_text("clean role-level replay", encoding="utf-8")

    if command == "validate":
        config_path = tmp_path / "config" / "repo_index.yaml"
        config_path.parent.mkdir()
        config_path.write_text("{}", encoding="utf-8")

    assert cli_mod.main([command, str(private_path)]) != 0
    captured = capsys.readouterr()
    assert "refusing to read or write private path" in captured.err
