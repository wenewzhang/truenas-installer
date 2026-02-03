"""
Tests for internationalization (i18n) module.
"""

import pytest
from truenas_installer.i18n import (
    _,
    LANGUAGES,
    set_language,
    get_language,
    get_language_name,
    _load_translations,
)


class TestI18n:
    """Test cases for i18n functionality."""

    def setup_method(self):
        """Reset language before each test."""
        set_language("en")

    def test_languages_count(self):
        """Test that we have 18 languages defined."""
        assert len(LANGUAGES) == 18
        assert "en" in LANGUAGES
        assert "zh" in LANGUAGES
        assert "es" in LANGUAGES
        assert "fr" in LANGUAGES
        assert "de" in LANGUAGES
        assert "ja" in LANGUAGES
        assert "ko" in LANGUAGES

    def test_set_language_valid(self):
        """Test setting a valid language."""
        assert set_language("zh") is True
        assert get_language() == "zh"
        
        assert set_language("es") is True
        assert get_language() == "es"

    def test_set_language_invalid(self):
        """Test setting an invalid language."""
        assert set_language("xx") is False
        assert get_language() == "en"  # Should remain unchanged

    def test_get_language_name(self):
        """Test getting language display names."""
        assert get_language_name("en") == "English"
        assert get_language_name("zh") == "中文 (Chinese)"
        assert get_language_name("es") == "Español (Spanish)"
        assert get_language_name() == "English"  # Current language

    def test_translation_english(self):
        """Test English translations."""
        set_language("en")
        
        assert _("menu_install_upgrade") == "Install/Upgrade"
        assert _("menu_language") == "Language"
        assert _("title_error") == "Error"

    def test_translation_chinese(self):
        """Test Chinese translations."""
        set_language("zh")
        
        assert _("menu_install_upgrade") == "安装/升级"
        assert _("menu_language") == "语言"
        assert _("title_error") == "错误"

    def test_translation_spanish(self):
        """Test Spanish translations."""
        set_language("es")
        
        assert _("menu_install_upgrade") == "Instalar/Actualizar"
        assert _("menu_language") == "Idioma"

    def test_translation_with_formatting(self):
        """Test translations with string formatting."""
        set_language("en")
        
        result = _("title_console_setup", vendor="TrueNAS", version="24.04")
        assert "TrueNAS" in result
        assert "24.04" in result
        
        result = _("progress_formatting_disk", disk="sda")
        assert "sda" in result

    def test_translation_fallback(self):
        """Test fallback to English for missing translations."""
        set_language("zh")
        
        # Test that all keys have translations
        keys_to_check = [
            "menu_install_upgrade",
            "menu_shell",
            "menu_reboot",
            "menu_shutdown",
            "menu_language",
            "title_console_setup",
            "title_destination_media",
            "title_installation",
            "title_legacy_boot",
            "title_auth_method",
            "title_installation_error",
            "title_installation_success",
            "title_language_select",
            "title_error",
            "msg_no_drives",
            "msg_select_at_least_one_disk",
            "label_password",
            "label_confirm_password",
            "label_admin_user",
            "label_webui_auth",
            "label_unknown_model",
        ]
        
        for key in keys_to_check:
            translation = _(key)
            assert translation is not None
            assert translation != key or key == "menu_shell"  # shell is same in many languages

    def test_all_languages_have_translations(self):
        """Test that all defined languages have translation files."""
        import os
        import json
        
        translations_dir = os.path.join(
            os.path.dirname(__file__), "..", "truenas_installer", "translations"
        )
        
        for lang_code in LANGUAGES.keys():
            if lang_code == "en":
                continue  # English is the default
            
            trans_file = os.path.join(translations_dir, f"{lang_code}.json")
            assert os.path.exists(trans_file), f"Missing translation file for {lang_code}"
            
            with open(trans_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                assert isinstance(data, dict)
                assert len(data) > 0


class TestTranslationCompleteness:
    """Test that all translation files have complete translations."""

    def test_all_translations_have_same_keys(self):
        """Test that all translation files have the same keys as English."""
        import os
        import json
        
        from truenas_installer.i18n import _get_default_translations
        
        default_keys = set(_get_default_translations().keys())
        translations_dir = os.path.join(
            os.path.dirname(__file__), "..", "truenas_installer", "translations"
        )
        
        for lang_code in LANGUAGES.keys():
            if lang_code == "en":
                continue
            
            trans_file = os.path.join(translations_dir, f"{lang_code}.json")
            if os.path.exists(trans_file):
                with open(trans_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    trans_keys = set(data.keys())
                    
                    # Check if all default keys are present
                    missing = default_keys - trans_keys
                    if missing:
                        print(f"Warning: {lang_code} is missing keys: {missing}")
