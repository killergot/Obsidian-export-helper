import pytest

from src.FileClasses.Searcher import SearcherAllFiles


class TestLinkFinder:
    """Тесты для класса LinkFinder."""

    @pytest.fixture
    def finder(self):
        class TestSearcher(SearcherAllFiles):
            """Тестовый класс"""

            def refactor_path_files(self, links: list[str]) -> list[str]:
                """Твоя реализация обработки путей."""
                # Здесь твоя логика
                return links

        return TestSearcher()

    # --- Wikilinks [[...]] ---

    def test_simple_wikilink(self, finder):
        text = "Смотри заметку [[MyNote]]"
        assert "MyNote" in finder.find_all_links(text)

    def test_wikilink_with_display_name(self, finder):
        text = "Ссылка на [[MyNote|красивое название]]"
        assert "MyNote" in finder.find_all_links(text)

    def test_wikilink_with_section(self, finder):
        text = "См. [[Example#Details]]"
        assert "Example" in finder.find_all_links(text)

    def test_wikilink_with_section_and_display(self, finder):
        text = "Читай [[Example#Details|Section name]]"
        assert "Example" in finder.find_all_links(text)

    def test_wikilink_with_spaces(self, finder):
        text = "Заметка [[My Cool Note]]"
        assert "My Cool Note" in finder.find_all_links(text)

    # --- Markdown ссылки [...](...)---

    def test_simple_markdown_link(self, finder):
        text = "Кликни [сюда](myfile.md)"
        assert "myfile.md" in finder.find_all_links(text)

    def test_markdown_link_with_section(self, finder):
        text = "Читай [Section name](Example.md#Details)"
        assert "Example.md#Details" in finder.find_all_links(text)

    def test_markdown_link_with_path(self, finder):
        text = "Файл [здесь](notes/subfolder/file.md)"
        assert "notes/subfolder/file.md" in finder.find_all_links(text)

    # --- Ссылки с пробелами ---

    def test_markdown_link_angle_brackets(self, finder):
        text = "Смотри [display](<file name with spaces.md>)"
        assert "file name with spaces.md" in finder.find_all_links(text)

    def test_markdown_link_encoded_spaces(self, finder):
        text = "Открой [ссылка](file%20name.md)"
        assert "file name.md" in finder.find_all_links(text)

    # --- Множественные ссылки ---

    def test_multiple_links(self, finder):
        text = "[[Note1]] и [link](note2.md) и [[Note3|display]]"
        result = finder.find_all_links(text)
        assert "Note1" in result
        assert "note2.md" in result
        assert "Note3" in result

    def test_no_duplicates(self, finder):
        text = "[[MyNote]] и [[MyNote]] и [[MyNote]]"
        result = finder.find_all_links(text)
        assert result.count("MyNote") == 1

    # --- Граничные случаи ---

    def test_empty_text(self, finder):
        assert finder.find_all_links("") == []

    def test_no_links(self, finder):
        text = "Просто текст без ссылок."
        assert finder.find_all_links(text) == []

    def test_broken_wikilink(self, finder):
        text = "Сломанная [[ссылка"
        assert finder.find_all_links(text) == []

    def test_cyrillic_filename(self, finder):
        text = "[[Моя заметка]]"
        assert "Моя заметка" in finder.find_all_links(text)

    def test_special_characters(self, finder):
        text = "[[file-name_123]]"
        assert "file-name_123" in finder.find_all_links(text)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
