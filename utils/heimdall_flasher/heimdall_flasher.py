import subprocess


class HeimdallFlasher:
    """Gère le flashing avec Heimdall."""

    @staticmethod
    def flash_partition(partition, file_path):
        """Flashe une partition avec Heimdall."""
        try:
            subprocess.run(["heimdall", "flash", f"--{partition}", file_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors du flashing de {partition}: {e}")

    @staticmethod
    def flash_all(partitions):
        """Flashe toutes les partitions détectées."""
        for partition, file_path in partitions.items():
            HeimdallFlasher.flash_partition(partition, file_path)
