# components/menu_manager.py

from PyQt6.QtWidgets import QMenu, QMessageBox
from PyQt6.QtGui import QAction

class MenuManager:
    def __init__(self, main_window, theme_manager):
        self.main_window = main_window
        self.theme_manager = theme_manager

    def create_menu(self):

        """Crée et configure le menu principal."""
        menubar = self.main_window.menuBar()

        # SETTINGS Menu
        self._create_settings_menu(menubar)

        # ADB Menu
        self._create_adb_menu(menubar)

        # SCRIPTS Menu
        self._create_scripts_menu(menubar)

        # Heimdall liason 
        self._create_heimdall_menu(menubar)

    def _create_settings_menu(self, menubar):
        """Crée le menu SETTINGS."""
        settings_menu = QMenu("SETTINGS", self.main_window)

        # Theme Manager
        theme_manager_menu = QMenu("THEME MANAGER", self.main_window)
        available_themes = self.theme_manager.list_available_themes()
        for theme_name in available_themes:
            theme_action = QAction(theme_name.capitalize(), self.main_window)
            theme_action.triggered.connect(lambda _, t=theme_name: self.main_window.change_theme(t))
            theme_manager_menu.addAction(theme_action)

        # Ajouter un thème
        add_theme_action = QAction("+ Add Theme", self.main_window)
        add_theme_action.triggered.connect(self.main_window.add_new_theme)
        theme_manager_menu.addAction(add_theme_action)

        settings_menu.addMenu(theme_manager_menu)

        # Update Packages
        update_action = QAction("UPDATE PACKAGES", self.main_window)
        update_action.triggered.connect(self.main_window.check_packages_update)
        settings_menu.addAction(update_action)

        # Manage Modules
        modules_action = QAction("MODULES", self.main_window)
        modules_action.triggered.connect(self.main_window.manage_modules)
        settings_menu.addAction(modules_action)

        menubar.addMenu(settings_menu)

    def _create_adb_menu(self, menubar):
        """Crée le menu ADB."""
        adb_menu = QMenu("ADB", self.main_window)

        adb_version_action = QAction("ADB VERSION", self.main_window)
        adb_version_action.triggered.connect(self.main_window.show_adb_version)
        adb_menu.addAction(adb_version_action)

        adb_package_manager_action = QAction("PACKAGE MANAGER", self.main_window)
        adb_package_manager_action.triggered.connect(self.main_window.open_package_manager)
        adb_menu.addAction(adb_package_manager_action)


        menubar.addMenu(adb_menu)

    def _create_scripts_menu(self, menubar):
        """Crée le menu SCRIPTS."""
        scripts_menu = QMenu("SCRIPTS", self.main_window)

        magisk_script_action = QAction("MAGISK SCRIPT CONSOLE", self.main_window)
        magisk_script_action.triggered.connect(self.main_window.run_magisk_script)
        scripts_menu.addAction(magisk_script_action)

        bash_script_action = QAction("BASH SCRIPT CONSOLE", self.main_window)
        bash_script_action.triggered.connect(self.main_window.run_bash_script)
        scripts_menu.addAction(bash_script_action)

        menubar.addMenu(scripts_menu)

    def _create_heimdall_menu(self,menubar):
        """Cree le menue de liason avec hemdall"""
        heimdall_menu = QMenu("HEIMDALL", self.main_window)


        menubar.addMenu(heimdall_menu)


