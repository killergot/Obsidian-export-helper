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


def _run_main_allow_fail(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "main.py", *args]
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


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


def test_source_without_suffix_uses_markdown_file(tmp_path: Path) -> None:
    vault, source_file = _create_vault(tmp_path)
    output_dir = tmp_path / "out"

    repo_root = Path(__file__).resolve().parents[1]
    result = _run_main(
        [
            str(source_file.with_suffix("")),
            "-o",
            str(output_dir),
            "--vault_path",
            str(vault),
        ],
        cwd=repo_root,
    )

    assert (output_dir / "note1.md").exists()
    assert "- notes: 2" in result.stdout
    assert "- output: " in result.stdout


def test_non_markdown_source_file_has_clear_error(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    source_file = vault / "note.txt"
    source_file.write_text("not markdown", encoding="utf-8")

    repo_root = Path(__file__).resolve().parents[1]
    result = _run_main_allow_fail(
        [str(source_file), "--vault_path", str(vault)],
        cwd=repo_root,
    )

    assert result.returncode != 0
    assert "source_file must be a Markdown file (.md)" in result.stderr


def test_missing_source_file_has_clear_error(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()

    repo_root = Path(__file__).resolve().parents[1]
    result = _run_main_allow_fail(
        ["missing-note", "--vault_path", str(vault)],
        cwd=repo_root,
    )

    assert result.returncode != 0
    assert "source file not found" in result.stderr
    assert "missing-note.md" in result.stderr


def test_vault_path_must_contain_source_file(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    outside = tmp_path / "outside"
    vault.mkdir()
    outside.mkdir()
    source_file = outside / "note.md"
    source_file.write_text("outside", encoding="utf-8")

    repo_root = Path(__file__).resolve().parents[1]
    result = _run_main_allow_fail(
        [str(source_file), "--vault_path", str(vault)],
        cwd=repo_root,
    )

    assert result.returncode != 0
    assert "--vault_path does not contain source_file" in result.stderr


def test_report_includes_summary_and_missing_links(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    source_file = vault / "report-source.md"
    source_file.write_text(
        "See [missing](missing.md)\n![image](image.png)\n",
        encoding="utf-8",
    )
    (vault / "image.png").write_text("png", encoding="utf-8")
    output_dir = tmp_path / "out"

    repo_root = Path(__file__).resolve().parents[1]
    report_file = repo_root / "export-report-report-source.md"
    if report_file.exists():
        report_file.unlink()

    try:
        result = _run_main(
            [
                str(source_file),
                "-o",
                str(output_dir),
                "--vault_path",
                str(vault),
                "--report",
            ],
            cwd=repo_root,
        )

        report = report_file.read_text(encoding="utf-8")

        assert (output_dir / "report-source.md").exists()
        assert (output_dir / "image.png").exists()
        assert report_file.exists()
        assert (output_dir / "export-report-report-source.md").exists() is False
        assert "- notes: 1" in result.stdout
        assert "- images: 1" in result.stdout
        assert "- missing links: 1" in result.stdout
        assert "missing.md (linked target is missing)" in report
        assert "image.png" in report
    finally:
        if report_file.exists():
            report_file.unlink()
