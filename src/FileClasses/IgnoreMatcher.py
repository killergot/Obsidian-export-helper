from dataclasses import dataclass
from pathlib import Path, PurePosixPath


DEFAULT_IGNORE_FILE = ".obsidian-export-ignore"


@dataclass(frozen=True)
class IgnoreRule:
    pattern: str
    negated: bool = False
    directory_only: bool = False
    anchored: bool = False
    has_slash: bool = False


class IgnoreMatcher:
    """Small gitignore-style matcher scoped to the vault root."""

    def __init__(self, vault_path: Path, rules: list[IgnoreRule] | None = None) -> None:
        self.vault_path = vault_path.resolve()
        self.rules = rules or []

    @classmethod
    def empty(cls, vault_path: Path) -> "IgnoreMatcher":
        return cls(vault_path, [])

    @classmethod
    def from_file(cls, vault_path: Path, ignore_file: Path) -> "IgnoreMatcher":
        rules: list[IgnoreRule] = []
        for raw_line in ignore_file.read_text(encoding="utf-8").splitlines():
            rule = cls._parse_rule(raw_line)
            if rule is not None:
                rules.append(rule)
        return cls(vault_path, rules)

    @staticmethod
    def _parse_rule(raw_line: str) -> IgnoreRule | None:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            return None

        negated = line.startswith("!")
        if negated:
            line = line[1:].strip()
            if not line:
                return None

        directory_only = line.endswith("/")
        line = line.strip("/")
        if not line:
            return None

        anchored = raw_line.lstrip().startswith("/")
        has_slash = "/" in line or "\\" in line
        pattern = line.replace("\\", "/")
        return IgnoreRule(
            pattern=pattern,
            negated=negated,
            directory_only=directory_only,
            anchored=anchored,
            has_slash=has_slash,
        )

    def is_ignored(self, path: str | Path, *, is_dir: bool = False) -> bool:
        if not self.rules:
            return False

        rel_path = self._normalize_path(path)
        ignored = False
        for rule in self.rules:
            if self._matches_rule(rel_path, rule, is_dir=is_dir):
                ignored = not rule.negated
        return ignored

    def _normalize_path(self, path: str | Path) -> str:
        candidate = Path(path)
        if candidate.is_absolute():
            try:
                candidate = candidate.resolve().relative_to(self.vault_path)
            except ValueError:
                candidate = Path(candidate.name)
        return candidate.as_posix().replace("\\", "/").strip("/")

    def _matches_rule(self, rel_path: str, rule: IgnoreRule, *, is_dir: bool) -> bool:
        if not rel_path:
            return False

        if rule.directory_only:
            return self._matches_directory_rule(rel_path, rule, is_dir=is_dir)

        if rule.has_slash or rule.anchored:
            return PurePosixPath(rel_path).match(rule.pattern)

        return any(PurePosixPath(part).match(rule.pattern) for part in rel_path.split("/"))

    def _matches_directory_rule(
        self, rel_path: str, rule: IgnoreRule, *, is_dir: bool
    ) -> bool:
        pattern = rule.pattern.rstrip("/")
        if rule.has_slash or rule.anchored:
            if rel_path == pattern:
                return is_dir
            return rel_path.startswith(pattern + "/")

        parts = rel_path.split("/")
        if is_dir and PurePosixPath(parts[-1]).match(pattern):
            return True
        return any(PurePosixPath(part).match(pattern) for part in parts[:-1])
