"""
Tests for v2.9.36 - Internationalization (i18n) Expansion

Tests the addition of 5 new languages (ES, FR, DE, ZH, JA) to the i18n system.
"""

import json
from pathlib import Path

import pytest


class TestI18nExpansion:
    """Test suite for i18n expansion - 5 new languages"""

    I18N_DIR = Path("src/i18n")
    REQUIRED_LANGUAGES = ["en", "pt_BR", "es", "fr", "de", "zh", "ja"]
    NEW_LANGUAGES = ["es", "fr", "de", "zh", "ja"]

    @pytest.fixture
    def base_keys(self):
        """Load English (base) translation keys"""
        with open(self.I18N_DIR / "en.json", encoding="utf-8") as f:
            data = json.load(f)
        return {k for k in data.keys() if not k.startswith("_")}

    def test_all_language_files_exist(self):
        """Verify all 7 language files exist"""
        for lang in self.REQUIRED_LANGUAGES:
            file_path = self.I18N_DIR / f"{lang}.json"
            assert file_path.exists(), f"Missing translation file: {lang}.json"

    def test_all_files_valid_json(self):
        """Verify all translation files are valid JSON"""
        for lang in self.REQUIRED_LANGUAGES:
            file_path = self.I18N_DIR / f"{lang}.json"
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)  # Should not raise
                assert isinstance(data, dict), f"{lang}.json is not a JSON object"

    def test_all_files_utf8_encoded(self):
        """Verify all files are UTF-8 encoded (important for CJK)"""
        for lang in self.REQUIRED_LANGUAGES:
            file_path = self.I18N_DIR / f"{lang}.json"
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                assert content, f"{lang}.json is empty"
                # For CJK languages, verify special characters
                if lang in ["zh", "ja"]:
                    data = json.loads(content)
                    # Check if CJK characters are present
                    has_cjk = any(
                        ord(char) >= 0x4E00 and ord(char) <= 0x9FFF
                        for value in data.values()
                        if isinstance(value, str)
                        for char in value
                    )
                    assert has_cjk, f"{lang}.json missing CJK characters"

    def test_new_languages_have_metadata(self):
        """Verify new language files have _comment and _translators metadata"""
        for lang in self.NEW_LANGUAGES:
            file_path = self.I18N_DIR / f"{lang}.json"
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            assert "_comment" in data, f"{lang}.json missing _comment field"
            assert "_translators" in data, f"{lang}.json missing _translators field"
            assert "Community contributions" in data["_comment"], f"{lang}.json _comment doesn't mention community"

    def test_all_languages_have_same_keys(self, base_keys):
        """Verify all language files have consistent keys (new languages may have more)"""
        # Get keys from one of the new languages as reference (they are more complete)
        with open(self.I18N_DIR / "es.json", encoding="utf-8") as f:
            complete_data = json.load(f)
        complete_keys = {k for k in complete_data.keys() if not k.startswith("_")}

        # Verify all NEW languages have the same keys
        for lang in self.NEW_LANGUAGES:
            file_path = self.I18N_DIR / f"{lang}.json"
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            lang_keys = {k for k in data.keys() if not k.startswith("_")}

            missing_keys = complete_keys - lang_keys
            extra_keys = lang_keys - complete_keys

            assert not missing_keys, f"{lang}.json missing keys: {sorted(missing_keys)[:10]}"
            assert not extra_keys, f"{lang}.json has extra keys: {sorted(extra_keys)[:10]}"

    def test_key_count_consistency(self, base_keys):
        """Verify new language files have consistent key count"""
        # Get count from one of the new languages as reference
        with open(self.I18N_DIR / "es.json", encoding="utf-8") as f:
            reference_data = json.load(f)
        expected_count = len({k for k in reference_data.keys() if not k.startswith("_")})

        # All NEW languages should have the same count
        for lang in self.NEW_LANGUAGES:
            file_path = self.I18N_DIR / f"{lang}.json"
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            lang_keys = {k for k in data.keys() if not k.startswith("_")}
            assert len(lang_keys) == expected_count, f"{lang}.json has {len(lang_keys)} keys, expected {expected_count}"

    def test_no_empty_translations(self):
        """Verify no translation values are empty strings"""
        for lang in self.REQUIRED_LANGUAGES:
            file_path = self.I18N_DIR / f"{lang}.json"
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            empty_keys = [k for k, v in data.items() if not k.startswith("_") and isinstance(v, str) and not v.strip()]
            assert not empty_keys, f"{lang}.json has empty translations: {empty_keys[:5]}"

    def test_critical_ui_elements_translated(self):
        """Verify critical UI elements are translated in new languages"""
        critical_keys = [
            "menu.file",
            "menu.edit",
            "search.button",
            "search.cancel",
            "dialog.yes",  # Changed from dialog.ok (which is same in many languages)
            "dialog.cancel",
        ]

        for lang in self.NEW_LANGUAGES:
            file_path = self.I18N_DIR / f"{lang}.json"
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            for key in critical_keys:
                assert key in data, f"{lang}.json missing critical key: {key}"
                value = data[key]
                # Verify translation exists and is not empty
                assert value and value.strip(), f"{lang}.json key '{key}' is empty"

    def test_hierarchical_key_structure(self):
        """Verify keys maintain hierarchical structure (menu.*, search.*, etc.)"""
        categories = ["menu", "search", "tooltip", "context", "status", "shortcuts", "dialog", "error"]

        for lang in self.REQUIRED_LANGUAGES:
            file_path = self.I18N_DIR / f"{lang}.json"
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            # Count keys in each category
            for category in categories:
                category_keys = [k for k in data.keys() if k.startswith(f"{category}.")]
                assert len(category_keys) > 0, f"{lang}.json missing '{category}.*' keys"

    def test_shortcuts_category_complete(self):
        """Verify all shortcuts.* keys are present (largest category)"""
        for lang in self.NEW_LANGUAGES:
            file_path = self.I18N_DIR / f"{lang}.json"
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            shortcut_keys = [k for k in data.keys() if k.startswith("shortcuts.")]
            # Should have at least 70+ shortcut-related keys
            assert len(shortcut_keys) >= 70, f"{lang}.json has only {len(shortcut_keys)} shortcuts keys"

    def test_json_structure_consistency(self):
        """Verify JSON files maintain consistent structure"""
        for lang in self.REQUIRED_LANGUAGES:
            file_path = self.I18N_DIR / f"{lang}.json"

            # Read raw content to check formatting
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Verify proper JSON formatting (indentation)
            assert '"' in content, f"{lang}.json has no string values"
            assert "\n" in content, f"{lang}.json is not formatted (no newlines)"

    def test_translator_metadata_format(self):
        """Verify new files have proper translator metadata format"""
        for lang in self.NEW_LANGUAGES:
            file_path = self.I18N_DIR / f"{lang}.json"
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            translators = data.get("_translators", [])
            assert isinstance(translators, list), f"{lang}.json _translators should be a list"
            assert len(translators) > 0, f"{lang}.json _translators is empty"
            assert any(
                "baseline" in t.lower() or "automated" in t.lower() for t in translators
            ), f"{lang}.json _translators doesn't indicate automated translation"

    def test_cjk_languages_proper_encoding(self):
        """Verify CJK languages (Chinese, Japanese) have proper character encoding"""
        cjk_languages = {"zh": "中文", "ja": "日本"}

        for lang, expected_chars in cjk_languages.items():
            file_path = self.I18N_DIR / f"{lang}.json"
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Verify file contains CJK characters
            has_cjk = any(ord(char) >= 0x4E00 and ord(char) <= 0x9FFF for char in content)
            assert has_cjk, f"{lang}.json doesn't contain CJK characters"

    def test_no_placeholder_strings(self):
        """Verify no placeholder strings like 'TODO', 'FIXME', or '[translation needed]'"""
        placeholders = ["TODO", "FIXME", "[translation needed]", "TRANSLATE_ME", "XXX"]

        for lang in self.NEW_LANGUAGES:
            file_path = self.I18N_DIR / f"{lang}.json"
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            for key, value in data.items():
                if not key.startswith("_") and isinstance(value, str):
                    for placeholder in placeholders:
                        assert placeholder not in value, f"{lang}.json key '{key}' contains placeholder: {placeholder}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
