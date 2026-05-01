import subprocess
import sys
from pathlib import Path


def _create_vault(tmp_path: Path) -> tuple[Path, Path]:
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "sub").mkdir()

    source_file = vault / "note1.md"
    source_file.write_text(
        "See [doc](attach.txt)\nAnd [other](sub/note2.md)\n",
        encoding="utf-8",
    )
    (vault / "attach.txt").write_text("attachment", encoding="utf-8")
    (vault / "sub" / "note2.md").write_text("child note", encoding="utf-8")
    return vault, source_file


def _run_main(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "main.py", *args]
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert result.returncode == 0, (
        f"Command failed: {cmd}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    return result


def test_default_vault_path_uses_source_parent(tmp_path: Path) -> None:
    vault, source_file = _create_vault(tmp_path)
    output_dir = tmp_path / "out"

    repo_root = Path(__file__).resolve().parents[1]
    _run_main([str(source_file), "-o", str(output_dir)], cwd=repo_root)

    assert (output_dir / "note1.md").exists()
    assert (output_dir / "note2.md").exists()
    assert (output_dir / "attach.txt").exists()
    assert (output_dir / "sub").exists() is False
    assert (vault / "note1.md").exists()
    assert (vault / "sub" / "note2.md").exists()


def test_folder_flag_preserves_structure(tmp_path: Path) -> None:
    vault, source_file = _create_vault(tmp_path)
    output_dir = tmp_path / "out"
    output_dir.mkdir()

    repo_root = Path(__file__).resolve().parents[1]
    _run_main(
        [str(source_file), "-o", str(output_dir), "--folder"],
        cwd=repo_root,
    )

    assert (output_dir / "note1.md").exists()
    assert (output_dir / "attach.txt").exists()
    assert (output_dir / "sub" / "note2.md").exists()


def test_delete_flag_moves_files(tmp_path: Path) -> None:
    vault, source_file = _create_vault(tmp_path)
    output_dir = tmp_path / "out"
    output_dir.mkdir()

    repo_root = Path(__file__).resolve().parents[1]
    _run_main(
        [str(source_file), "-o", str(output_dir), "--delete"],
        cwd=repo_root,
    )

    assert (output_dir / "note1.md").exists()
    assert (output_dir / "note2.md").exists()
    assert (output_dir / "attach.txt").exists()
    assert (vault / "note1.md").exists() is False
    assert (vault / "sub" / "note2.md").exists() is False
    assert (vault / "attach.txt").exists() is False


def test_explicit_vault_path_flag(tmp_path: Path) -> None:
    vault, source_file = _create_vault(tmp_path)
    output_dir = tmp_path / "out"
    output_dir.mkdir()

    repo_root = Path(__file__).resolve().parents[1]
    _run_main(
        [str(source_file), "-o", str(output_dir), "--vault_path", str(vault)],
        cwd=repo_root,
    )

    assert (output_dir / "note1.md").exists()
    assert (output_dir / "note2.md").exists()
    assert (output_dir / "attach.txt").exists()


def test_vault_path_keeps_source_relative_path_with_folder(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    notes = vault / "Notes"
    notes.mkdir(parents=True)
    source_file = notes / "index.md"
    source_file.write_text("See [child](child.md)\n", encoding="utf-8")
    (notes / "child.md").write_text("child", encoding="utf-8")
    output_dir = tmp_path / "out"

    repo_root = Path(__file__).resolve().parents[1]
    _run_main(
        [
            str(source_file),
            "-o",
            str(output_dir),
            "--folder",
            "--vault_path",
            str(vault),
        ],
        cwd=repo_root,
    )

    assert (output_dir / "Notes" / "index.md").exists()
    assert (output_dir / "Notes" / "child.md").exists()


def test_markdown_anchor_links_are_copied(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    source_file = vault / "index.md"
    source_file.write_text("See [child](child.md#section)\n", encoding="utf-8")
    (vault / "child.md").write_text("child", encoding="utf-8")
    output_dir = tmp_path / "out"

    repo_root = Path(__file__).resolve().parents[1]
    _run_main(
        [str(source_file), "-o", str(output_dir), "--vault_path", str(vault)],
        cwd=repo_root,
    )

    assert (output_dir / "index.md").exists()
    assert (output_dir / "child.md").exists()
