import os
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QCheckBox, QWidget, QAbstractItemView, QHeaderView, QMessageBox, QFileDialog
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt
from core.adbd_dexter import ADBDexter


class PackageManager(QMainWindow):
    """Gestionnaire de packages pour les applications ADB."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestionnaire de Packages")
        self.setMinimumSize(800, 600)

        self.adb_dexter = ADBDexter()
        self.show_system_apps = False  # Variable pour le filtre des apps système

        # Initialiser l'interface utilisateur
        self.init_ui()

        # Charger les packages au démarrage
        self.load_packages()

    def init_ui(self):
        """Initialise l'interface utilisateur."""
        # Créez un widget central pour le contenu
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout(central_widget)

        # Barre de recherche et boutons
        self.top_layout = QHBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Rechercher une application...")
        self.search_bar.textChanged.connect(self.filter_table)
        self.top_layout.addWidget(self.search_bar)

        self.install_button = QPushButton("Installer App")
        self.install_button.clicked.connect(self.install_apk)
        self.top_layout.addWidget(self.install_button)

        self.uninstall_button = QPushButton("Désinstaller App")
        self.uninstall_button.clicked.connect(self.uninstall_package)
        self.top_layout.addWidget(self.uninstall_button)

        # Boutons de filtre
        self.filter_buttons = QHBoxLayout()
        self.system_apps_button = QCheckBox("Afficher apps système")
        self.system_apps_button.setChecked(self.show_system_apps)
        self.system_apps_button.stateChanged.connect(self.toggle_system_apps_filter)
        self.filter_buttons.addWidget(self.system_apps_button)

        self.layout.addLayout(self.top_layout)
        self.layout.addLayout(self.filter_buttons)

        # Tableau des applications
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Icône", "Nom de l'Application", "Nom du Package"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.itemDoubleClicked.connect(self.show_package_details)
        self.layout.addWidget(self.table)

    def load_packages(self):
        """Charge la liste des packages dans le tableau."""
        packages = self.adb_dexter.adb_list_packages(filter_system=self.show_system_apps)
        app_details = []
        for package in packages:
            name = self.adb_dexter.adb_get_app_name(package)
            app_details.append({
                "package": package,
                "name": name,
                "icon": "assets/icons/android-filed-green.png"  # Utiliser une icône par défaut
            })
        self.populate_table(app_details)

    def populate_table(self, packages):
        """Remplit le tableau avec les données des applications."""
        self.table.setRowCount(len(packages))

        for row, app in enumerate(packages):
            # Icône
            icon_item = QTableWidgetItem()
            if app["icon"] and os.path.exists(app["icon"]):
                icon_item.setIcon(QIcon(QPixmap(app["icon"])))
            else:
                icon_item.setIcon(QIcon("assets/icons/android-filed-green.png"))
            self.table.setItem(row, 0, icon_item)

            # Nom
            name_item = QTableWidgetItem(app["name"])
            name_item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Non modifiable
            self.table.setItem(row, 1, name_item)

            # Package
            package_item = QTableWidgetItem(app["package"])
            package_item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Non modifiable
            self.table.setItem(row, 2, package_item)

    def filter_table(self):
        """Filtre les lignes du tableau en fonction de la recherche."""
        search_text = self.search_bar.text().lower()
        for row in range(self.table.rowCount()):
            visible = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    visible = True
                    break
            self.table.setRowHidden(row, not visible)

    def install_apk(self):
        """Permet d'installer un fichier APK via ADB."""
        apk_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier APK", "", "Fichiers APK (*.apk)")
        if apk_path:
            message = self.adb_dexter.adb_install(apk_path)
            QMessageBox.information(self, "Installation APK", message)
            self.load_packages()

    def uninstall_package(self, package_name=None):
        """Désinstalle une application sélectionnée."""
        if not package_name:
            selected_row = self.table.currentRow()
            if selected_row == -1:
                QMessageBox.warning(self, "Aucune sélection", "Veuillez sélectionner une application à désinstaller.")
                return
            package_name = self.table.item(selected_row, 2).text()

        message = self.adb_dexter.adb_uninstall(package_name)
        QMessageBox.information(self, "Désinstallation", message)
        self.load_packages()


    def toggle_system_apps_filter(self):
        """Active ou désactive le filtre des apps système."""
        self.show_system_apps = self.system_apps_button.isChecked()
        self.load_packages()

    def show_package_details(self, item):
        """Affiche les détails d'un package dans une nouvelle fenêtre."""
        row = item.row()
        package_name = self.table.item(row, 2).text()
        details = self.adb_dexter.adb_package_details(package_name)

        details_window = PackageDetailsWindow(package_name, details, self)
        details_window.show()


class PackageDetailsWindow(QMainWindow):
    def __init__(self, package_name, details, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Détails : {package_name}")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Propriété", "Valeur"])
        table.horizontalHeader().setStretchLastSection(True)

        rows = []
        for section, values in details.items():
            for value in values:
                rows.append((section, value))
        table.setRowCount(len(rows))
        for i, (prop, val) in enumerate(rows):
            table.setItem(i, 0, QTableWidgetItem(prop))
            table.setItem(i, 1, QTableWidgetItem(val))

        layout.addWidget(table)

        if parent.adb_dexter.can_uninstall(package_name):
            uninstall_button = QPushButton("Désinstaller")
            uninstall_button.clicked.connect(self.uninstall_package)
            layout.addWidget(uninstall_button)

        self.package_name = package_name
        self.parent = parent

    def uninstall_package(self):
        """Désinstalle le package courant."""
        message = self.parent.adb_dexter.adb_uninstall(self.package_name)
        QMessageBox.information(self, "Désinstallation", message)
        self.parent.load_packages()
        self.close()
