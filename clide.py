#clide.py
import sys
import subprocess
import logging
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from core.adbd_dexter import ADBDexter
from core.settings import ThemeManager

from utils.ri_downgrade_checker import DowngradeChecker
from utils.partition_utils import PartitionManager
from core.rom_api import ROMApi
from utils.scrcpy_in_qt import ScrcpyManager

from components.rom_browser import ROMBrowser
from components.menu_manager import MenuManager
from components.package_manager import PackageManager

logging.basicConfig(level=logging.DEBUG)

class CLIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.partition_manager = None
        self.rom_manager = ROMApi()
        self.scrcpy_manager = ScrcpyManager()
        self.theme_manager = ThemeManager()
        self.package_manager = None
        self.setWindowTitle("CLIDE - OMEGA GSM")
        self.setGeometry(120, 120, 1200, 880)
        # Forcer l'affichage du menu dans la fenêtre (utile sur Linux)
        self.menuBar().setNativeMenuBar(False)
        # Widgets
        self.init_widgets()
        # Layout principal
        self.init_layouts()
        # Configuration ADB
        self.adb_dexter = ADBDexter()
        self.current_device = None
        self.device_properties = {}
        # Appliquer le thème par défaut si disponible
        default_theme = "light-blue"  # Définir un thème par défaut, par exemple
        if default_theme in self.theme_manager.list_available_themes():
            self.change_theme(default_theme)
        # Menu Manager
        self.menu_manager = MenuManager(self, self.theme_manager)
        self.menu_manager.create_menu()


    def init_widgets(self):
        """Initialiser tous les widgets de l'application."""
        self.device_info_label = QLabel("Aucun périphérique détecté")
        self.device_info_label.setObjectName("device_info_label")

        self.run_button = QPushButton("Afficher les clefs ADB")
        self.run_button.clicked.connect(self.run_adb_command)
        self.run_button.setEnabled(False)

        self.check_downgrade_button = QPushButton(QIcon("./assets/icons/time-downgrade-checker-blue.png"),"Vérifier Downgrade")
        self.check_downgrade_button.clicked.connect(self.check_downgrade)
        self.check_downgrade_button.setEnabled(False)

        self.scrcpy_container = QWidget()
        self.scrcpy_container.setObjectName("scrcpy_container")
        self.scrcpy_container.setFixedSize(380, 670)
        self.scrcpy_container.setStyleSheet("background-color: #263238; border: 1px solid #4caf50;")

        # En-tête avec boutons pour le conteneur scrcpy
        self.scrcpy_header = QWidget(self.scrcpy_container)
        self.scrcpy_header.setFixedHeight(20)
        self.scrcpy_header.setStyleSheet("background-color: #4caf50;")
        header_layout = QHBoxLayout(self.scrcpy_header)
        header_layout.setContentsMargins(2, 2, 4, 4)

        self.scrcpy_button = QPushButton("+", self.scrcpy_header)
        self.scrcpy_button.setFixedSize(60, 60)
        self.scrcpy_button.clicked.connect(self.launch_scrcpy)

        self.scrcpy_close_button = QPushButton("✖", self.scrcpy_header)
        self.scrcpy_close_button.setFixedSize(30, 30)
        self.scrcpy_close_button.clicked.connect(self.stop_scrcpy)


        # Layout du conteneur scrcpy
        scrcpy_layout = QVBoxLayout(self.scrcpy_container)
        scrcpy_layout.addWidget(self.scrcpy_header)
        scrcpy_layout.addStretch()

        self.adb_play_pause_button = QPushButton("Connecter à ADB")
        self.adb_play_pause_button.clicked.connect(self.toggle_adb_connection)
        self.adb_play_pause_button.setEnabled(True)

        self.capture_screen_button = QPushButton("Capturer écran")
        self.capture_screen_button.clicked.connect(self.capture_screen)
        self.capture_screen_button.setEnabled(False)

        self.reboot_device_button = QPushButton("Redémarrer appareil")
        self.reboot_device_button.clicked.connect(self.reboot_device)
        self.reboot_device_button.setEnabled(False)

        self.show_partitions_button = QPushButton("Afficher les partitions")
        self.show_partitions_button.clicked.connect(self.show_partitions)
        self.show_partitions_button.setEnabled(False)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["Properties", "Values"])
        self.tree.setColumnWidth(40, 150)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search")
        self.search_bar.textChanged.connect(self.filter_tree)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("status_label")
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

    def init_layouts(self):
        """Configurer les layouts principaux de l'application."""
        # Layout pour la zone Scrcpy
        scrcpy_layout = QVBoxLayout()
        scrcpy_layout.addWidget(self.scrcpy_container)

        # Ajouter les boutons Play/Pause comme dans Android Studio
        scrcpy_controls_layout = QHBoxLayout()
        self.play_button = QPushButton("▶ Play")
        self.play_button.clicked.connect(self.launch_scrcpy)
        self.pause_button = QPushButton("❚❚ Pause")
        self.pause_button.clicked.connect(self.stop_scrcpy)
        self.pause_button.setEnabled(False)  # Désactivé par défaut
        scrcpy_controls_layout.addWidget(self.play_button)
        scrcpy_controls_layout.addWidget(self.pause_button)
    
        scrcpy_layout.addLayout(scrcpy_controls_layout)
        main_layout = QHBoxLayout()
        menu_layout = QVBoxLayout()
        menu_layout.addWidget(self.adb_play_pause_button)
        menu_layout.addWidget(self.run_button)
        menu_layout.addWidget(self.check_downgrade_button)
        menu_layout.addWidget(self.scrcpy_button)
        menu_layout.addWidget(self.capture_screen_button)
        menu_layout.addWidget(self.reboot_device_button)
        menu_layout.addWidget(self.show_partitions_button)
        menu_layout.addStretch()

        content_layout = QVBoxLayout()
        content_layout.addWidget(self.device_info_label)
        content_layout.addWidget(self.search_bar)
        content_layout.addWidget(self.tree)
        content_layout.addWidget(self.status_label)
        content_layout.addWidget(self.progress_bar)

        

        main_layout.addLayout(menu_layout, 1)
        main_layout.addLayout(scrcpy_layout, 3)
        main_layout.addLayout(content_layout, 4)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)


    
    def launch_scrcpy(self):
        """Lancer Scrcpy"""
        result = self.scrcpy_manager.launch_scrcpy_in_container(self.scrcpy_container, self.current_device)
        if "succès" in result:
            self.launch_scrcpy_button.setEnabled(False)
            self.stop_scrcpy_button.setEnabled(True)
        else:
            QMessageBox.critical(self, "Erreur", result)

    def stop_scrcpy(self):
        """Arrêter Scrcpy"""
        result = self.scrcpy_manager.stop_scrcpy()
        QMessageBox.information(self, "Info", result)
        self.launch_scrcpy_button.setEnabled(True)
        self.stop_scrcpy_button.setEnabled(False)


    def change_theme(self, theme_name):
        """Applique un thème via le ThemeManager."""
        success = self.theme_manager.apply_theme(theme_name, self)
        if success:
            self.status_label.setText(f"Thème '{theme_name}' appliqué avec succès.")

    def add_new_theme(self):
        """Ajoute un nouveau thème via le ThemeManager."""
        self.theme_manager.add_new_theme(self)
        self.create_menu_bar()  # Recharge le menu pour inclure le nouveau thème

    def check_packages_update(self):
        # Implémentez la logique pour vérifier les mises à jour des packages ici
        QMessageBox.information(self, "PACKAGES UPDATE CHECK", "Vérification des mises à jour des packages.")

    def manage_modules(self):
        # Implémentez la logique pour gérer les modules ici
        QMessageBox.information(self, "MODULES", "Gestion des modules.")

    def show_adb_version(self):
        """Afficher la version d'ADB."""
        try:
            adb_version = subprocess.check_output(["adb", "version"], universal_newlines=True)
            QMessageBox.information(self, "ADB VERSION", f"Version ADB :\n{adb_version}")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de récupérer la version ADB.\n{e}")

    def run_magisk_script(self):
        """Exécuter un script Magisk."""
        # Implémentez la logique pour exécuter un script Magisk ici
        QMessageBox.information(self, "MAGISK SCRIPT", "Exécution d'un script Magisk.")

    def run_bash_script(self):
        """Exécuter un script Bash."""
        # Implémentez la logique pour exécuter un script Bash ici
        QMessageBox.information(self, "BASH SCRIPT", "Exécution d'un script Bash.")

    def connect_signals(self):
        # Les signaux sont déjà connectés dans __init__ pour certains boutons.
        # Ajoutez d'autres signaux ici si nécessaire.
        pass

    def toggle_adb_connection(self):
        if self.current_device:
            self.disconnect_adb()
        else:
            self.check_adb_connection()

    def disconnect_adb(self):
        self.current_device = None
        self.device_info_label.setText("Aucun périphérique détecté")
        self.device_info_label.setStyleSheet("color: red; font-weight: bold;")
        self.run_button.setEnabled(False)
        self.check_downgrade_button.setEnabled(False)
        self.scrcpy_button.setEnabled(False)
        self.capture_screen_button.setEnabled(False)
        self.reboot_device_button.setEnabled(False)
        self.show_partitions_button.setEnabled(False)
        self.adb_play_pause_button.setText("Connecter à ADB")
        self.status_label.setText("Déconnecté.")

    def check_adb_connection(self):
        self.current_device = self.adb_dexter.is_device_connected()
        if self.current_device:
            self.device_info_label.setText(f"Périphérique détecté : {self.current_device}")
            self.device_info_label.setStyleSheet("color: green; font-weight: bold;")
            self.run_button.setEnabled(True)
            self.check_downgrade_button.setEnabled(True)
            self.scrcpy_button.setEnabled(True)
            self.capture_screen_button.setEnabled(True)
            self.reboot_device_button.setEnabled(True)
            self.show_partitions_button.setEnabled(True)
            self.adb_play_pause_button.setText("Déconnecter ADB")
            self.status_label.setText("Connecté au périphérique.")
        else:
            self.show_adb_connect_popup()

    def show_adb_connect_popup(self):
        ip, ok = QInputDialog.getText(self, "ADB Connect", "Entrez l'adresse IP et le port (IP:PORT) :")
        if ok and ip:
            try:
                subprocess.check_output(["adb", "connect", ip], universal_newlines=True)
                self.status_label.setText(f"Connecté à {ip}")
                self.check_adb_connection()
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "Erreur de connexion", str(e))

    def run_adb_command(self):
        """Récupère les propriétés de l'appareil via ADB et les affiche dans l'interface."""
        categorized_data = self.adb_dexter.get_device_properties_categorized()
        if categorized_data:
            self.populate_tree(categorized_data)
            self.status_label.setText("Propriétés récupérées.")
        else:
            self.status_label.setText("Erreur : Propriétés non récupérées.")
            
    def open_package_manager(self):
        print("Ouverture du gestionnaire de packages")
        if not self.package_manager:
            self.package_manager = PackageManager(self)
        self.package_manager.show()


    def check_downgrade(self):
        if DowngradeChecker.is_downgradable(self.device_properties):
            self.status_label.setText("Le périphérique est éligible au downgrade.")
        else:
            self.status_label.setText("Le périphérique n'est pas éligible au downgrade.")

    def capture_screen(self):
        message = self.adb_dexter.capture_screenshot("capture.png")
        QMessageBox.information(self, "Capture d'écran", message)


    def reboot_device(self):
        if self.current_device:
            result = DeviceRebootOption.reboot()
            self.status_label.setText(result)

    def show_partitions(self):
        if not self.current_device:
            QMessageBox.warning(self, "Erreur", "Aucun périphérique connecté.")
            return
        try:
            partition_manager = PartitionManager()
            partition_manager.detect_partitions()
            partitions = partition_manager.partitions
            if partitions:
                details = "\n".join([f"{name}: {path}" for name, path in partitions.items()])
                QMessageBox.information(self, "Partitions détectées", details)
            else:
                QMessageBox.warning(self, "Aucune partition", "Aucune partition détectée sur l'appareil.")
        except RuntimeError as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def categorize_properties(self, properties):
        return ADBDexter.categorize_properties(properties)

    def populate_tree(self, categorized_data):
        ADBDexter.populate_tree(self, categorized_data)

    def filter_tree(self):
        ADBDexter.filter_tree(self)
        
 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CLIDE()
    window.show()
    sys.exit(app.exec())