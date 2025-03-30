import subprocess
from PyQt6.QtCore import QProcess


class ScrcpyManager:
    """Gestion de scrcpy avec intégration dans PyQt."""

    def __init__(self):
        self.scrcpy_process = None
        self.window_id = None

    @staticmethod
    def is_scrcpy_installed():
        """Vérifie si scrcpy est installé."""
        try:
            subprocess.run(["scrcpy", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except FileNotFoundError:
            return False

    def launch_scrcpy_in_container(self, container_widget, device_id=None, resolution="1024", bit_rate="8M", max_fps=60):
        """Lance scrcpy et intègre la fenêtre dans un widget PyQt."""
        if not self.is_scrcpy_installed():
            return "scrcpy non installé. Veuillez l'installer."

        # Terminer les anciens processus scrcpy
        if self.scrcpy_process and self.scrcpy_process.state() == QProcess.ProcessState.Running:
            self.scrcpy_process.terminate()
            self.scrcpy_process.waitForFinished(3000)

        # Construire les arguments pour scrcpy
        args = [
            "--window-title", "scrcpy",
            "--window-borderless",
            "--max-size", resolution,
            "--bit-rate", bit_rate,
            "--max-fps", str(max_fps),
        ]
        if device_id:
            args += ["--serial", device_id]

        # Lancer scrcpy
        self.scrcpy_process = QProcess()
        self.scrcpy_process.setProgram("scrcpy")
        self.scrcpy_process.setArguments(args)
        self.scrcpy_process.start()

        if not self.scrcpy_process.waitForStarted(3000):
            return "Échec du lancement de scrcpy."

        # Attendre que la fenêtre scrcpy soit disponible
        import time
        time.sleep(2)  # Laisser le temps à scrcpy de démarrer

        # Obtenir l'ID de la fenêtre scrcpy
        self.window_id = self.get_window_id()
        if not self.window_id:
            return "Impossible de trouver la fenêtre scrcpy."

        # Intégrer scrcpy dans le conteneur
        self.position_scrcpy_window(container_widget)
        return "scrcpy lancé avec succès."

    def get_window_id(self):
        """Trouve l'ID de la fenêtre scrcpy."""
        try:
            window_ids = subprocess.check_output(
                ["xdotool", "search", "--name", "scrcpy"], universal_newlines=True
            ).strip().splitlines()

            if not window_ids:
                print("[ERROR] Aucune fenêtre contenant 'scrcpy' n'a été trouvée.")
                return None

            # Retourner le premier ID trouvé
            return window_ids[0]
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Erreur lors de la recherche de la fenêtre scrcpy : {e}")
            return None

    def position_scrcpy_window(self, container_widget):
        """Déplace et redimensionne la fenêtre scrcpy dans un conteneur PyQt."""
        if not self.window_id:
            print("[ERROR] Aucun ID de fenêtre scrcpy trouvé.")
            return

        # Obtenir la géométrie du conteneur PyQt
        container_geometry = container_widget.geometry()
        print(f"[DEBUG] Géométrie du conteneur : {container_geometry}")

        try:
            # Déplacer la fenêtre scrcpy à l'intérieur du conteneur
            subprocess.run([
                "xdotool", "windowmove", self.window_id,
                str(container_geometry.x()), str(container_geometry.y())
            ], check=True)

            # Redimensionner la fenêtre scrcpy pour qu'elle corresponde au conteneur
            subprocess.run([
                "xdotool", "windowsize", self.window_id,
                str(container_geometry.width()), str(container_geometry.height())
            ], check=True)

            print("[DEBUG] Fenêtre scrcpy repositionnée et redimensionnée avec succès.")
        except FileNotFoundError:
            print("[ERROR] xdotool non trouvé. Installez xdotool pour gérer les fenêtres.")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Impossible de repositionner la fenêtre scrcpy : {e}")

    def stop_scrcpy(self):
        """Arrête scrcpy."""
        if self.scrcpy_process and self.scrcpy_process.state() == QProcess.ProcessState.Running:
            self.scrcpy_process.terminate()
            self.scrcpy_process.waitForFinished(3000)
            self.scrcpy_process = None
            return "scrcpy arrêté avec succès."
        return "Aucun processus scrcpy en cours."
