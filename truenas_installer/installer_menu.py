import asyncio
import os
import sys

import humanfriendly

from .dialog import (
    dialog_checklist,
    dialog_menu,
    dialog_msgbox,
    dialog_password,
    dialog_yesno,
)
from .disks import Disk, list_disks
from .exception import InstallError
from .i18n import _, LANGUAGES, set_language, get_language, get_language_name
from .install import install


class InstallerMenu:
    def __init__(self, installer):
        self.installer = installer

    async def run(self):
        await self._main_menu()

    async def _main_menu(self):
        await dialog_menu(
            _("title_console_setup", vendor=self.installer.vendor, version=self.installer.version),
            {
                _("menu_install_upgrade"): self._install_upgrade,
                _("menu_shell"): self._shell,
                _("menu_reboot"): self._reboot,
                _("menu_shutdown"): self._shutdown,
                _("menu_language"): self._select_language,
            },
        )

    async def _select_language(self):
        """Show language selection menu."""
        language_items = {
            code: name for code, name in LANGUAGES.items()
        }
        
        selected_lang = await dialog_menu(
            _("title_language_select"),
            language_items,
            cancel_label=_("menu_shell") if get_language() == "zh" else None,  # Use Shell as cancel for Chinese
        )
        
        if selected_lang:
            set_language(selected_lang)
            # Return to main menu with new language
            await self._main_menu()
        else:
            # User cancelled, return to main menu
            await self._main_menu()

    async def _install_upgrade(self):
        while True:
            await self._install_upgrade_internal()
            await self._main_menu()

    async def _install_upgrade_internal(self):
        disks = await list_disks()
        vendor = self.installer.vendor

        if not disks:
            await dialog_msgbox(
                _("title_destination_media"),
                _("msg_no_drives")
            )
            return False

        while True:
            destination_disks = await dialog_checklist(
                _("title_destination_media"),
                _("msg_select_disk", vendor=vendor),
                {
                    disk.name: " ".join(
                        [
                            disk.model[:15].ljust(15, " "),
                            disk.label[:15].ljust(15, " "),
                            "--",
                            humanfriendly.format_size(disk.size, binary=True),
                        ]
                    )
                    for disk in disks
                },
            )

            if destination_disks is None:
                # Installation cancelled
                return False

            if not destination_disks:
                await dialog_msgbox(
                    _("title_destination_media"),
                    _("msg_select_at_least_one_disk"),
                )
                continue

            wipe_disks = [
                disk.name
                for disk in disks
                if (
                    any(
                        zfs_member.pool == "boot-pool"
                        for zfs_member in disk.zfs_members
                    )
                    and disk.name not in destination_disks
                )
            ]
            if wipe_disks:
                # The presence of multiple `boot-pool` disks with different guids leads to boot pool import error
                text = _(
                    "msg_boot_pool_exists",
                    disks=", ".join(wipe_disks)
                )
                if not await dialog_yesno(_("title_installation", vendor=vendor), text):
                    continue

            break

        all_disks = sorted(wipe_disks + destination_disks)
        text = _(
            "msg_install_warning",
            disks=", ".join(all_disks),
            dest_disks=", ".join(destination_disks)
        )
        if not await dialog_yesno(_("title_installation", vendor=vendor), text):
            return False

        if vendor == "HexOS":
            authentication_method = await self._authentication_truenas_admin()
        else:
            authentication_method = await dialog_menu(
                _("title_auth_method"),
                {
                    _("label_admin_user"): self._authentication_truenas_admin,
                    _("label_webui_auth"): self._authentication_webui,
                },
            )
            if authentication_method is False:
                return False

        set_pmbr = False
        if not self.installer.efi:
            set_pmbr = await dialog_yesno(
                _("title_legacy_boot"),
                _("msg_legacy_boot"),
            )

        sql = ""

        try:
            await install(
                self._select_disks(disks, destination_disks),
                self._select_disks(disks, wipe_disks),
                set_pmbr,
                authentication_method,
                None,
                sql,
                self._callback,
            )
        except InstallError as e:
            await dialog_msgbox(_("title_installation_error"), e.message)
            return False

        await dialog_msgbox(
            _("title_installation_success"),
            _(
                "msg_install_success",
                vendor=vendor,
                disks=", ".join(destination_disks)
            ),
        )
        return True

    def _select_disks(self, disks: list[Disk], disks_names: list[str]):
        disks_dict = {disk.name: disk for disk in disks}
        return [disks_dict[disk_name] for disk_name in disks_names]

    async def _authentication_truenas_admin(self):
        return await self._authentication_password(
            "truenas_admin",
            _("msg_password_prompt", user="truenas_admin"),
        )

    async def _authentication_password(self, username, title):
        password = await dialog_password(title)
        if password is None:
            return False

        return {"username": username, "password": password}

    async def _authentication_webui(self):
        return None

    async def _shell(self):
        os._exit(1)

    async def _reboot(self):
        process = await asyncio.create_subprocess_exec("reboot")
        await process.communicate()

    async def _shutdown(self):
        process = await asyncio.create_subprocess_exec("shutdown", "now")
        await process.communicate()

    def _callback(self, progress, message):
        sys.stdout.write(f"[{int(progress * 100)}%] {message}\n")
        sys.stdout.flush()
