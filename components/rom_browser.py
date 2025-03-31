from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QAbstractItemView, QHBoxLayout, QLabel
)
from PyQt5.QtCore import Qt
import webbrowser


class ROMBrowser(QDialog):
    def __init__(self, roms, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ROMs disponibles")
        self.setGeometry(100, 100, 900, 600)

        # Layout principal
        layout = QVBoxLayout()

        # Label d'information
        self.info_label = QLabel(f"{len(roms)} ROM(s) disponible(s)")
        self.info_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.info_label)

        # Table pour afficher les ROMs
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Nom de la ROM", "Lien"])
        self.table.setRowCount(len(roms))
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        for row, rom in enumerate(roms):
            self.table.setItem(row, 0, QTableWidgetItem(rom["name"]))
            link_item = QTableWidgetItem(rom["url"])
            link_item.setToolTip("Cliquez pour ouvrir dans le navigateur.")
            self.table.setItem(row, 1, link_item)

        self.table.resizeColumnsToContents()
        self.table.cellDoubleClicked.connect(self.open_link)  # Double clic pour ouvrir un lien
        layout.addWidget(self.table)

        # Boutons d'action
        button_layout = QHBoxLayout()

        copy_button = QPushButton("Copier le lien")
        copy_button.clicked.connect(self.copy_link)
        button_layout.addWidget(copy_button)

        close_button = QPushButton("Fermer")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def open_link(self, row, column):
        """Ouvre le lien dans le navigateur si la colonne du lien est cliquée."""
        if column == 1:  # La colonne des liens
            url = self.table.item(row, column).text()
            webbrowser.open(url)

    def copy_link(self):
        """Copie le lien de la ROM sélectionnée dans le presse-papiers."""
        selected_items = self.table.selectedItems()
        if not selected_items:
            self.show_message("Aucune ROM sélectionnée.")
            return

        link = None
        for item in selected_items:
            if self.table.column(item) == 1:  # La colonne des liens
                link = item.text()
                break

        if link:
            QApplication.clipboard().setText(link)
            self.show_message(f"Le lien a été copié dans le presse-papiers : {link}")
        else:
            self.show_message("Aucun lien valide trouvé dans la sélection.")

    def show_message(self, message):
        """Affiche un message d'information temporaire."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Information")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
