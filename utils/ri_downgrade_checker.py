class DowngradeChecker:
    """Détermine si un périphérique est éligible pour un downgrade."""

    @staticmethod
    def is_downgradable(properties):
        """
        Analyse les propriétés ADB pour vérifier l'éligibilité au downgrade.
        
        :param properties: Dictionnaire des propriétés récupérées via adb shell getprop
        :return: True si le périphérique est éligible, sinon False
        """
        # 1. Vérification de l'état du bootloader
        if properties.get("ro.boot.verifiedbootstate", "").lower() not in ("orange", "yellow", "red"):
            # Si le bootloader est "green", c'est verrouillé
            return False
        
        # 2. Vérification des clés de signature
        build_tags = properties.get("ro.build.tags", "")
        if "test-keys" in build_tags:
            return True  # Signé avec des clés de test
        
        build_type = properties.get("ro.build.type", "")
        if build_type == "userdebug" or build_type == "eng":
            return True  # Appareil en mode débogage
        
        # 3. Vérification de la version du correctif de sécurité
        security_patch = properties.get("ro.build.version.security_patch", "0").replace("-", "")
        try:
            if int(security_patch) < 20210501:
                return True  # Correctifs de sécurité avant mai 2021
        except ValueError:
            pass  # Si la valeur est incorrecte, continuer la vérification

        # 4. Vérification de la version du bootloader

        bootloader = properties.get("ro.boot.bootloader", "").lower()
        if "downgrade" in bootloader or "dev" in bootloader:
            return True  # Bootloader indique une version compatible downgrade
        
        # 5. Vérification du déverrouillage du bootloader

        oem_unlock_allowed = properties.get("sys.oem_unlock_allowed", "0")
        if oem_unlock_allowed == "1":
            return True
        
        # 6. Vérification des propriétés spécifiques aux marques

        manufacturer = properties.get("ro.product.manufacturer", "").lower()
        if manufacturer == "samsung":
            # Vérification pour Samsung (bootloader et baseband)

            baseband = properties.get("ro.boot.baseband", "")
            if "downgrade" in baseband or "test" in baseband:
                return True
            
        # Si aucune des conditions n'est remplie, le downgrade n'est pas possible
        
        return False
