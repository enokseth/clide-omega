import os
from PyQt6.QtWidgets import QFileDialog, QInputDialog, QMessageBox

class ThemeManager:
    """Gestionnaire de thèmes pour l'application."""

    def __init__(self, stylesheet_directory="./assets/styles"):
        self.stylesheet_directory = stylesheet_directory

    def apply_theme(self, theme_name, main_window):
        """Applique un thème à l'application.

        Args:
            theme_name (str): Nom du fichier QSS sans extension (e.g., "light" ou "dark").
            main_window (QMainWindow): Instance principale de l'application.

        Returns:
            bool: True si le thème est appliqué avec succès, False sinon.
        """
        theme_file = os.path.join(self.stylesheet_directory, f"{theme_name}.qss")

        if not os.path.exists(theme_file):
            QMessageBox.critical(
                main_window,
                "Erreur de thème",
                f"Le fichier de thème '{theme_name}.qss' est introuvable."
            )
            return False

        try:
            with open(theme_file, "r") as file:
                main_window.setStyleSheet(file.read())
            if hasattr(main_window, 'status_label'):  # Assurez-vous que le label existe
                main_window.status_label.setText(f"Thème '{theme_name}' appliqué avec succès.")
            return True
        except Exception as e:
            QMessageBox.critical(
                main_window,
                "Erreur d'application du thème",
                f"Une erreur est survenue lors de l'application du thème: {str(e)}"
            )
            return False

    def list_available_themes(self):
        """Liste tous les thèmes disponibles dans le répertoire des stylesheets.

        Returns:
            list: Liste des noms de thèmes disponibles (sans extension).
        """
        try:
            return [
                os.path.splitext(file)[0]
                for file in os.listdir(self.stylesheet_directory)
                if file.endswith(".qss")
            ]
        except FileNotFoundError:
            return []

    def add_theme(self, source_file, theme_name=None):
        """Ajoute un nouveau fichier de thème dans le répertoire des stylesheets.

        Args:
            source_file (str): Chemin du fichier QSS source à ajouter.
            theme_name (str, optional): Nom du thème (sans extension). Si None, utilise le nom du fichier source.

        Returns:
            bool: True si le thème est ajouté avec succès, False sinon.
        """
        if not os.path.exists(source_file) or not source_file.endswith(".qss"):
            return False

        theme_name = theme_name or os.path.splitext(os.path.basename(source_file))[0]
        destination_file = os.path.join(self.stylesheet_directory, f"{theme_name}.qss")

        try:
            os.makedirs(self.stylesheet_directory, exist_ok=True)
            with open(source_file, "r") as src:
                with open(destination_file, "w") as dst:
                    dst.write(src.read())
            return True
        except Exception as e:
            print(f"[ERROR] Impossible d'ajouter le thème: {e}")
            return False

    def add_new_theme(self, main_window):
        """Ajoute un nouveau thème à partir d'un fichier QSS sélectionné par l'utilisateur.

        Args:
            main_window (QMainWindow): Instance principale de l'application.
        """
        file_dialog = QFileDialog(main_window)
        file_dialog.setNameFilter("QSS FILE (*.qss)")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                theme_file = selected_files[0]
                theme_name, ok = QInputDialog.getText(main_window, "Nom du thème", "Entrez un nom pour le nouveau thème :")
                if ok and theme_name:
                    if self.add_theme(theme_file, theme_name):
                        QMessageBox.information(main_window, "Succès", f"Thème '{theme_name}' ajouté avec succès.")
                    else:
                        QMessageBox.critical(main_window, "Erreur", "Impossible d'ajouter le thème.")
