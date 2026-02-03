"""
Internationalization (i18n) support for TrueNAS Installer.
Supports 18 most popular languages in the world.
"""

import json
import os
from typing import Dict, Optional

# Current language setting
_current_language = "en"

# Available languages (18 most popular languages in the world by number of speakers)
LANGUAGES = {
    "en": "English",
    "zh": "中文 (Chinese)",
    "hi": "हिन्दी (Hindi)",
    "es": "Español (Spanish)",
    "fr": "Français (French)",
    "ar": "العربية (Arabic)",
    "bn": "বাংলা (Bengali)",
    "pt": "Português (Portuguese)",
    "ru": "Русский (Russian)",
    "ur": "اردو (Urdu)",
    "id": "Bahasa Indonesia (Indonesian)",
    "de": "Deutsch (German)",
    "ja": "日本語 (Japanese)",
    "tr": "Türkçe (Turkish)",
    "vi": "Tiếng Việt (Vietnamese)",
    "ko": "한국어 (Korean)",
    "it": "Italiano (Italian)",
    "th": "ไทย (Thai)",
}

# Translation dictionary
_translations: Dict[str, Dict[str, str]] = {}


def _get_default_translations():
    """Get default English translations (source strings)."""
    return {
        # Menu items
        "menu_install_upgrade": "Install/Upgrade",
        "menu_shell": "Shell",
        "menu_reboot": "Reboot System",
        "menu_shutdown": "Shutdown System",
        "menu_language": "Language",
        
        # Titles
        "title_console_setup": "{vendor} {version} Console Setup",
        "title_destination_media": "Choose Destination Media",
        "title_installation": "{vendor} Installation",
        "title_legacy_boot": "Legacy Boot",
        "title_auth_method": "Web UI Authentication Method",
        "title_installation_error": "Installation Error",
        "title_installation_success": "Installation Succeeded",
        "title_language_select": "Select Language",
        "title_error": "Error",
        
        # Messages
        "msg_no_drives": "No drives available",
        "msg_select_disk": (
            "Install {vendor} to a drive. If desired, select multiple drives to provide redundancy. {vendor} "
            "installation drive(s) are not available for use in storage pools. Use arrow keys to navigate "
            "options. Press spacebar to select."
        ),
        "msg_select_at_least_one_disk": "Select at least one disk to proceed with the installation.",
        "msg_boot_pool_exists": (
            "Disk(s) {disks} contain existing TrueNAS boot pool, but they were not "
            "selected for TrueNAS installation. This configuration will not work unless these disks "
            "are erased.\n\n"
            "Proceed with erasing {disks}?"
        ),
        "msg_install_warning": (
            "WARNING:\n"
            "- This erases ALL partitions and data on {disks}.\n"
            "- {dest_disks} will be unavailable for use in storage pools.\n\n"
            "NOTE:\n"
            "- Installing on SATA, SAS, or NVMe flash media is recommended.\n"
            "  USB flash sticks are discouraged.\n\n"
            "Proceed with the installation?"
        ),
        "msg_install_success": (
            "The {vendor} installation on {disks} succeeded!\n"
            "Please reboot and remove the installation media."
        ),
        "msg_legacy_boot": (
            "Allow EFI boot? Enter Yes for systems with newer components such as NVMe devices. Enter No when "
            "system hardware requires legacy BIOS boot workaround."
        ),
        "msg_password_prompt": 'Enter your "{user}" user password. Root password login will be disabled.',
        "msg_password_empty": "Empty passwords are not allowed.",
        "msg_password_mismatch": "Passwords do not match.",
        
        # Labels
        "label_password": "Password:",
        "label_confirm_password": "Confirm Password:",
        "label_admin_user": "Administrative user (truenas_admin)",
        "label_webui_auth": "Configure using Web UI",
        "label_unknown_model": "Unknown Model",
        
        # Installation progress
        "progress_formatting_disk": "Formatting disk {disk}",
        "progress_wiping_disk": "Wiping disk {disk}",
        "progress_creating_boot_pool": "Creating boot pool",
        "progress_warning_zfs_wipe": "Warning: unable to wipe ZFS label from {device}: {error}",
        "progress_warning_partition_wipe": "Warning: unable to wipe partition table for {disk}: {error}",
        "progress_failed_partition": "Failed to find partition number {num} on {disk}",
        "progress_failed_data_partition": "Failed to find data partition on {disk}",
        
        # Errors
        "error_command_failed": "Command {cmd} failed:\n{error}",
        "error_abnormal_termination": "Abnormal installer process termination with code {code}",
    }


def _load_translations():
    """Load all translation files."""
    global _translations
    
    # Set default English translations
    _translations["en"] = _get_default_translations()
    
    # Load other language files
    translations_dir = os.path.join(os.path.dirname(__file__), "translations")
    if os.path.exists(translations_dir):
        for lang in LANGUAGES.keys():
            if lang == "en":
                continue
            trans_file = os.path.join(translations_dir, f"{lang}.json")
            if os.path.exists(trans_file):
                try:
                    with open(trans_file, "r", encoding="utf-8") as f:
                        _translations[lang] = json.load(f)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Warning: Could not load translation file {trans_file}: {e}")


def set_language(lang: str) -> bool:
    """Set the current language."""
    global _current_language
    if lang in LANGUAGES:
        _current_language = lang
        return True
    return False


def get_language() -> str:
    """Get the current language."""
    return _current_language


def get_language_name(lang: Optional[str] = None) -> str:
    """Get the display name of a language."""
    if lang is None:
        lang = _current_language
    return LANGUAGES.get(lang, lang)


def _(key: str, **kwargs) -> str:
    """Translate a key with optional formatting arguments."""
    # Ensure translations are loaded
    if not _translations:
        _load_translations()
    
    # Get translation for current language, fallback to English
    text = _translations.get(_current_language, {}).get(key)
    if text is None:
        text = _translations.get("en", {}).get(key, key)
    
    # Apply formatting if kwargs provided
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass  # Keep original if formatting fails
    
    return text


# Load translations on module import
_load_translations()
