import subprocess
import os
from PyQt6.QtWidgets import *

class ADBDexter:
    """Gère les interactions avec ADB."""

    @staticmethod

    def is_device_connected():
        """Vérifie si un appareil est connecté via ADB."""
        output = ADBDexter.execute_command(["adb", "devices"])
        devices = [
            line.split("\t")[0]
            for line in output.splitlines()[1:] if "device" in line
        ]
        return devices[0] if devices else None

    @staticmethod

    def get_device_properties():
        """Récupère les propriétés système de l'appareil via ADB."""
        output = ADBDexter.execute_command(["adb", "shell", "getprop"])
        properties = {}
        if output:
            for line in output.split("\n"):
                if "]: [" in line:
                    key, value = line.split("]: [")
                    properties[key.strip("[").strip()] = value.strip("]").strip()
        return properties

    @staticmethod

    def get_device_properties_categorized():
        """
        Récupère les propriétés de l'appareil et les catégorise pour l'affichage.
        
        Returns:
            dict: Catégories et propriétés.
        """
        properties = ADBDexter.get_device_properties()
        return ADBDexter.categorize_properties(properties)


    @staticmethod
    def capture_screenshot(filename="screenshot.png"):
            """
            Capture une capture d'écran et la sauvegarde localement.

            Args:
                filename (str): Chemin du fichier pour sauvegarder la capture.

            Returns:
                str: Message de confirmation ou d'erreur.
            """
            try:
                screenshot = subprocess.check_output(["adb", "exec-out", "screencap", "-p"], stderr=subprocess.STDOUT)
                with open(filename, "wb") as f:  # Utiliser "wb" pour écrire en mode binaire
                    f.write(screenshot)
                return f"Capture d'écran enregistrée sous {filename}."
            except subprocess.CalledProcessError as e:
                return f"Erreur lors de la capture d'écran : {e.output.decode('utf-8', errors='ignore')}"
            except Exception as e:
                return f"Erreur inattendue : {str(e)}"

    @staticmethod
    def adb_get_app_name(package_name):
        """
        Récupère le nom d'affichage de l'application via ADB.

        Args:
            package_name (str): Nom du package de l'application.

        Returns:
            str: Nom d'affichage de l'application ou le package si non disponible.
        """
        try:
            # Récupérer les détails du package
            output = ADBDexter.execute_command(["adb", "shell", "dumpsys", "package", package_name, "|", "grep", "labelRes"],use_shell=True)

            if not output:
                print(f"Erreur : Aucun résultat pour le package {package_name}")
                return package_name

            # Extraire la ligne contenant "labelRes"
            for line in output.splitlines():
                if "label=" in line:
                    return line.split("label=")[-1].strip()

            # Retourner le package name si "labelRes" n'est pas trouvé
            return package_name
        except Exception as e:
            print(f"Erreur lors de la récupération du nom d'affichage pour {package_name} : {e}")
            return package_name


    
    @staticmethod
    def get_app_icon(package_name):
        """
        Récupère le chemin de l'icône d'une application ou retourne une icône par défaut.

        Args:
            package_name (str): Nom du package.

        Returns:
            str: Chemin de l'icône ou chemin par défaut.
        """
        try:
            # Récupérer le chemin de l'APK
            apk_path = ADBDexter.execute_command(["adb", "shell", "pm", "path", package_name])
            if not apk_path:
                print(f"Erreur : Chemin APK introuvable pour {package_name}")
                return "assets/icons/android-filed-green.png"
            apk_path = apk_path.replace("package:", "").strip()

            # Utiliser aapt pour extraire l'icône
            local_apk_path = f"{package_name}.apk"
            ADBDexter.execute_command(["adb", "pull", apk_path, local_apk_path])
            icon_line = subprocess.check_output(["aapt", "dump", "badging", local_apk_path], universal_newlines=True)
            for line in icon_line.splitlines():
                if "application-icon" in line:
                    # Extraire le chemin de l'icône depuis la sortie
                    icon_path = line.split(":")[-1].strip()
                    return icon_path

            # Icône par défaut si rien n'est trouvé
            return "assets/icons/android-filed-green.png"
        except Exception as e:
            print(f"Erreur lors de la récupération de l'icône pour {package_name} : {e}")
            return "assets/icons/android-filed-green.png"


    @staticmethod
    def adb_list_apps_with_details(filter_system=False):
        """
        Liste les applications installées avec leurs noms et icônes.

        Args:
            filter_system (bool): Si True, liste uniquement les applications système.

        Returns:
            list: Liste des dictionnaires avec 'package', 'name', et 'icon'.
        """
        try:
            packages = ADBDexter.adb_list_packages(filter_system=filter_system)
            apps = []
            for package in packages:
                name = ADBDexter.adb_get_app_name(package)
                icon = ADBDexter.get_app_icon(package) or "assets/icons/default-app-icon.png"
                apps.append({"package": package, "name": name, "icon": icon})
            return apps
        except Exception as e:
            print(f"Erreur lors de la récupération des applications : {e}")
            return []

            
    @staticmethod
    def adb_install(apk_path):
            """
            Installe une application via ADB.

            Args:
                apk_path (str): Chemin du fichier APK à installer.

            Returns:
                str: Message de confirmation ou d'erreur.
            """
            try:
                result = ADBDexter.execute_command(["adb", "install", apk_path])
                return f"Application installée : {apk_path}" if result else "Erreur lors de l'installation."
            except Exception as e:
                return f"Erreur inattendue : {str(e)}"

    @staticmethod
    def adb_uninstall(package_name):
        """
        Désinstalle une application via ADB.

        Args:
            package_name (str): Nom du package de l'application à désinstaller.

        Returns:
            str: Message de confirmation ou d'erreur.
        """
        try:
            result = ADBDexter.execute_command(["adb", "uninstall", package_name])
            return f"Application désinstallée : {package_name}" if result else "Erreur lors de la désinstallation."
        except Exception as e:
            return f"Erreur inattendue : {str(e)}"

    @staticmethod
    def can_uninstall(package_name):
        """
        Vérifie si un package peut être désinstallé en fonction de ses permissions.

        Args:
            package_name (str): Nom du package.

        Returns:
            bool: True si désinstallable, False sinon.
        """
        details = ADBDexter.adb_package_details(package_name)
        permissions = details.get("permissions", [])
        if any("INSTALL_PACKAGES" in perm or "SYSTEM" in perm for perm in permissions):
            return False
        return True

    @staticmethod
    def adb_list_packages(filter_system=False):
        """
        Liste les packages installés sur l'appareil.

        Args:
            filter_system (bool): Si True, affiche uniquement les packages système.

        Returns:
            list: Liste des packages installés.
        """
        try:
            command = ["adb", "shell", "pm", "list", "packages"]
            if filter_system:
                command.append("-s")
            output = ADBDexter.execute_command(command)
            packages = [
                line.replace("package:", "").strip()
                for line in output.splitlines()
                if line.strip()  # Ignore les lignes vides
            ]
            return packages
        except Exception as e:
            print(f"Erreur lors de la récupération des packages : {e}")
            return []
        

    @staticmethod
    def adb_package_details(package_name):
        """
        Récupère les détails d'un package spécifique via ADB.

        Args:
            package_name (str): Nom du package à inspecter.

        Returns:
            dict: Détails du package, y compris les permissions et chemins.
        """
        try:
            output = ADBDexter.execute_command(["adb", "shell", "dumpsys", "package", package_name])
            details = {}
            current_section = None
            for line in output.splitlines():
                line = line.strip()
                if not line:
                    continue
                if ":" in line and not line.startswith(" "):
                    current_section = line.replace(":", "").strip()
                    details[current_section] = []
                elif current_section:
                    details[current_section].append(line)
            return details
        except Exception as e:
            return {"Erreur": [str(e)]}
            
    @staticmethod
    def adb_list_apps_with_details(filter_system=False):
        """
        Liste les applications installées avec leurs noms et icônes.

        Args:
            filter_system (bool): Si True, liste uniquement les applications système.

        Returns:
            list: Liste des dictionnaires avec 'package', 'name', et 'icon_path'.
        """
        try:
            packages = ADBDexter.adb_list_packages(filter_system=filter_system)
            apps = []
            for package in packages:
                name = ADBDexter.adb_get_app_name(package)
                icon = ADBDexter.adb_get_app_icon(package, output_path=f"{package}_icon.png")
                apps.append({"package": package, "name": name, "icon": icon})
            return apps
        except Exception as e:
            print(f"Erreur lors de la récupération des applications : {e}")
            return []


    @staticmethod
    def categorize_properties(properties):
        """Catégorise les propriétés de l'appareil dans des catégories prédéfinies."""
        categorized_data = {
            "System": [],
            "Architecture": [],
            "Version Android": [],
            "Version Modem": [],
            "Version PIT": [],
            "CPU": [],
            "Kernel": [],
            "Kernel State": [],
            "Root": [],
            "Root State": [],
        }
        for key, value in properties.items():
            if "ro.system" in key:
                categorized_data["System"].append((key, value))
            elif "ro.product.cpu" in key or "dalvik.vm" in key:
                categorized_data["Architecture"].append((key, value))
            elif "ro.build.version" in key or "ro.build.fingerprint" in key:
                categorized_data["Version Android"].append((key, value))
            elif "ril.modem" in key or "gsm.version.baseband" in key:
                categorized_data["Version Modem"].append((key, value))
            elif "pit" in key.lower():
                categorized_data["Version PIT"].append((key, value))
            elif "ro.hardware" in key or "cpu" in key.lower():
                categorized_data["CPU"].append((key, value))
            elif "ro.kernel" in key or "sys.kernel" in key.lower():
                categorized_data["Kernel"].append((key, value))
            elif "ro.boot" in key:
                categorized_data["Kernel State"].append((key, value))
            elif "ro.debuggable" in key or "service.adb.root" in key:
                categorized_data["Root State"].append((key, value))
        return categorized_data

    @staticmethod
    def execute_command(command, capture_output=True):
        """
        Exécute une commande ADB et retourne son résultat.

        Args:
            command (list): Liste représentant la commande ADB à exécuter.
            capture_output (bool): Capture ou non la sortie de la commande.

        Returns:
            str: Résultat de la commande si capture_output est True.
        """
        try:
            print(f"Exécution de la commande : {' '.join(command)}")  # Ajout du journal
            if capture_output:
                result = subprocess.check_output(command, universal_newlines=True, stderr=subprocess.STDOUT)
                return result.strip()
            else:
                subprocess.call(command)
                return None
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de la commande : {command}\nSortie : {e.output.strip()}")
            return None


    @staticmethod
    def is_device_connected():
        """Vérifie si un appareil est connecté via ADB."""
        output = ADBDexter.execute_command(["adb", "devices"])
        devices = [
            line.split("\t")[0]
            for line in output.splitlines()[1:] if "device" in line
        ]
        return devices[0] if devices else None

    @staticmethod
    def get_device_properties():
        """Récupère les propriétés système de l'appareil via ADB."""
        output = ADBDexter.execute_command(["adb", "shell", "getprop"])
        properties = {}
        if output:
            for line in output.split("\n"):
                if "]: [" in line:
                    key, value = line.split("]: [")
                    properties[key.strip("[").strip()] = value.strip("]").strip()
        return properties

    @staticmethod
    def reboot_device(option="normal"):
        """
        Redémarre l'appareil avec une option donnée.

        Args:
            option (str): Option de redémarrage ("normal", "recovery", "bootloader", "download").

        Returns:
            str: Message de confirmation ou d'erreur.
        """
        if option == "normal":
            ADBDexter.execute_command(["adb", "reboot"], capture_output=False)
        elif option == "recovery":
            ADBDexter.execute_command(["adb", "reboot", "recovery"], capture_output=False)
        elif option == "bootloader":
            ADBDexter.execute_command(["adb", "reboot", "bootloader"], capture_output=False)
        elif option == "download":
            ADBDexter.execute_command(["adb", "reboot", "download"], capture_output=False)
        else:
            return "Option de redémarrage invalide."
        return f"L'appareil redémarre en mode {option}."

    @staticmethod
    def adb_list_apps_with_details(filter_system=False):
        """
        Liste les applications installées avec leurs noms et icônes.

        Args:
            filter_system (bool): Si True, liste uniquement les applications système.

        Returns:
            list: Liste des dictionnaires avec 'package', 'name', et 'icon'.
        """
        try:
            packages = ADBDexter.adb_list_packages(filter_system=filter_system)
            apps = []
            for package in packages:
                name = ADBDexter.adb_get_app_name(package)
                icon = ADBDexter.get_app_icon(package)
                apps.append({"package": package, "name": name, "icon": icon if icon else "assets/icons/android-filed-green.png"})
            return apps
        except Exception as e:
            print(f"Erreur lors de la récupération des applications : {e}")
            return []


    @staticmethod
    def get_app_real_name(package_name):
        """
        Récupère le nom réel de l'application via ADB.

        Args:
            package_name (str): Nom du package.

        Returns:
            str: Nom réel de l'application.
        """
        try:
            output = ADBDexter.execute_command(
                ["adb", "shell", "dumpsys", "package", package_name]
            )
            for line in output.splitlines():
                if "label=" in line:
                    return line.split("label=")[-1].strip()
            return package_name
        except Exception:
            return package_name

    @staticmethod
    def get_app_icon(package_name):
        """
        Récupère l'icône d'une application sous forme de chemin temporaire.

        Args:
            package_name (str): Nom du package.

        Returns:
            str: Chemin vers l'icône ou None.
        """
        try:
            # Récupérer le chemin de l'APK
            apk_path = ADBDexter.execute_command(["adb", "shell", "pm", "path", package_name])
            apk_path = apk_path.replace("package:", "").strip()

            if not apk_path:
                return None

            # Copier l'APK en local
            local_apk_path = f"{package_name}.apk"
            ADBDexter.execute_command(["adb", "pull", apk_path, local_apk_path])

            # Utiliser `aapt` pour extraire l'icône (si `aapt` est installé)
            icon_path = f"{package_name}_icon.png"
            subprocess.run(
                ["aapt", "dump", "badging", local_apk_path, "|", "grep", "application-icon"],
                stdout=open(icon_path, "wb"),
            )

            # Nettoyage
            os.remove(local_apk_path)
            return icon_path if os.path.exists(icon_path) else None
        except Exception as e:
            print(f"Erreur lors de la récupération de l'icône : {e}")
            return None


    @staticmethod
    def populate_tree(widget, categorized_data):
        """Remplit un QTreeWidget avec les données catégorisées."""
        widget.tree.clear()
        for category, items in categorized_data.items():
            category_item = QTreeWidgetItem([category])
            widget.tree.addTopLevelItem(category_item)
            for key, value in items:
                child_item = QTreeWidgetItem([key, value])
                category_item.addChild(child_item)
        widget.tree.collapseAll()

    @staticmethod
    def filter_tree(widget):
        """Filtre les éléments du QTreeWidget en fonction de la recherche."""
        search_text = widget.search_bar.text().lower()
        for i in range(widget.tree.topLevelItemCount()):
            category_item = widget.tree.topLevelItem(i)
            category_visible = False
            for j in range(category_item.childCount()):
                child_item = category_item.child(j)
                key = child_item.text(0).lower()
                value = child_item.text(1).lower()
                is_visible = search_text in key or search_text in value
                child_item.setHidden(not is_visible)
                if is_visible:
                    category_visible = True
            category_item.setHidden(not category_visible)
    @staticmethod
    def populate_table(table_widget, app_list):
        """
        Remplit un QTableWidget avec la liste des applications.

        Args:
            table_widget (QTableWidget): Widget où afficher les applications.
            app_list (list): Liste des applications avec 'package', 'name', et 'icon_path'.
        """
        table_widget.setRowCount(len(app_list))
        table_widget.setColumnCount(3)
        table_widget.setHorizontalHeaderLabels(["Icône", "Nom de l'application", "Nom du package"])

        for row, app in enumerate(app_list):
            icon_item = QTableWidgetItem()
            if app["icon_path"] and os.path.exists(app["icon_path"]):
                icon_item.setIcon(QIcon(QPixmap(app["icon_path"])))

            table_widget.setItem(row, 0, icon_item)
            table_widget.setItem(row, 1, QTableWidgetItem(app["name"]))
            table_widget.setItem(row, 2, QTableWidgetItem(app["package"]))
