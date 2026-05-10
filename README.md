# Talisman SEO Renamer

Outil macOS pour renommer automatiquement des images produit avec un slug SEO optimisé et les convertir en format WebP.

Développé par [Talisman](https://talisman.agency) — IA créative & acquisition pour PME.

---

## Ce que fait l'outil

- Glisse une ou plusieurs images sur l'icône dans le Dock
- L'IA (Claude) analyse visuellement chaque image
- Elle propose un slug SEO en français
- Tu valides ou tu régénères
- Le fichier est renommé et converti en `.webp` sur place

**Exemple**

```
IMG_4521.jpg  →  weasy-ceinture-running-femme-ajustable.webp
```

---

## Installation rapide

### 1. Télécharger le script

Télécharge `talisman_seo_renamer.py` depuis ce repo et place-le dans un dossier permanent :

```bash
mkdir -p ~/Library/Mobile\ Documents/com~apple~CloudDocs/Scripts
mv ~/Downloads/talisman_seo_renamer.py ~/Library/Mobile\ Documents/com~apple~CloudDocs/Scripts/
```

### 2. Installer les dépendances

```bash
pip3 install anthropic Pillow
```

### 3. Enregistrer ta clé API Anthropic

Crée une clé sur [console.anthropic.com](https://console.anthropic.com), puis :

```bash
echo "sk-ant-TACLÉ" > ~/.talisman_api_key
chmod 600 ~/.talisman_api_key
```

### 4. Créer l'app Automator

- Ouvre **Automator** → Nouveau document → **Application**
- Ajoute l'action **Exécuter un script Shell**
- Shell : `/bin/bash` — Pass input : `as arguments`
- Commande :

```bash
/usr/bin/python3 ~/Library/Mobile\ Documents/com~apple~CloudDocs/Scripts/talisman_seo_renamer.py "$@"
```

- Sauvegarde sous le nom `Talisman SEO Renamer` dans Applications
- Glisse l'icône dans le Dock

---

## Guide complet

Installation détaillée, dépannage et exemples : **[voir le guide Notion](#)** *(remplace ce lien par ton URL Notion)*

---

## Coût d'utilisation

Chaque image consomme environ 0,01 à 0,03 € via l'API Anthropic. Pour 100 images, moins de 3 €.

---

## Licence

Usage libre pour les clients Talisman.
