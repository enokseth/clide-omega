import os
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import QFileDialog

class PartitionManager:
    """Gère les partitions Android via ADB."""

    def __init__(self, adb_path="adb"):
        self.adb_path = adb_path
        self.partitions = {}

    def detect_partitions(self):
        """
        Détecte les partitions disponibles sur l'appareil connecté via ADB.
        """
        try:
            # Exécute la commande pour récupérer les partitions
            result = subprocess.check_output([self.adb_path, "shell", "ls", "/dev/block/by-name"], universal_newlines=True)
            partition_list = result.strip().split("\n")

            # Formate les partitions détectées
            for partition in partition_list:
                partition_path = f"/dev/block/by-name/{partition}"
                self.partitions[partition] = partition_path

            if not self.partitions:
                raise RuntimeError("Aucune partition détectée sur l'appareil.")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erreur lors de la détection des partitions : {e}")
        except FileNotFoundError:
            raise RuntimeError("ADB n'est pas installé ou introuvable dans PATH.")

    def create_symlinks(self, target_dir="partitions"):
        """
        Crée des liens symboliques locaux vers les partitions détectées.
        """
        os.makedirs(target_dir, exist_ok=True)
        for name, path in self.partitions.items():
            link_path = os.path.join(target_dir, name)
            try:
                if not os.path.exists(link_path):
                    os.symlink(path, link_path)
                elif os.path.islink(link_path):
                    if os.readlink(link_path) != path:
                        os.remove(link_path)
                        os.symlink(path, link_path)
            except OSError as e:
                print(f"Erreur lors de la création du lien symbolique pour '{name}': {e}")
