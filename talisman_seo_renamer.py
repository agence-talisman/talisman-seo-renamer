#!/usr/bin/env python3
"""
Talisman SEO Renamer
Glisse des images sur l'icône Dock → propose un slug SEO → renomme sur place
Utilise les dialogs natifs macOS via osascript — aucune dépendance UI requise
"""

import os
import sys
import base64
import subprocess
import urllib.request
import urllib.error
import json
from pathlib import Path
from PIL import Image

# ── Config ───────────────────────────────────────────────────────────────────
API_KEY_FILE = Path.home() / ".talisman_api_key"
MODEL        = "claude-sonnet-4-5"

PROMPT = """Tu es un expert SEO e-commerce.
Analyse cette image produit et génère UN SEUL slug SEO en français, optimisé pour le référencement naturel.
Règles : tout en minuscules, mots séparés par des tirets, 3 à 6 mots, type de produit + attribut distinctif + nom de marque si pertinent, pas de mots vides (le/la/de/des/pour).
Réponds UNIQUEMENT avec le slug, rien d'autre.
Exemple : chaussure-running-trail-homme-légère"""


# ── Dialogs natifs macOS ─────────────────────────────────────────────────────
def dialog(message, title="Talisman SEO Renamer"):
    subprocess.run(
        ["osascript", "-e",
         f'display dialog "{message}" with title "{title}" buttons {{"OK"}} default button "OK"'],
        capture_output=True
    )

def dialog_input(message, default="", hidden=False):
    hidden_str = "with hidden answer" if hidden else ""
    script = f'''
        set result to display dialog "{message}" default answer "{default}" {hidden_str} ¬
            buttons {{"Annuler", "OK"}} default button "OK" with title "Talisman SEO Renamer"
        return text returned of result
    '''
    r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return r.stdout.strip()

def dialog_yesno(message, title="Talisman SEO Renamer"):
    script = f'''
        set result to display dialog "{message}" ¬
            buttons {{"Non", "Oui"}} default button "Oui" with title "{title}"
        return button returned of result
    '''
    r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return r.stdout.strip() == "Oui"


# ── Clé API ──────────────────────────────────────────────────────────────────
def get_api_key():
    if API_KEY_FILE.exists():
        key = API_KEY_FILE.read_text().strip()
        if key:
            return key
    # Demande à l'utilisateur
    key = dialog_input("Entre ta clé API Anthropic :", hidden=True)
    if key:
        API_KEY_FILE.write_text(key)
        API_KEY_FILE.chmod(0o600)
    return key


# ── Appel API Anthropic ──────────────────────────────────────────────────────
def get_slug_from_image(image_path: Path, api_key: str) -> str:
    suffix = image_path.suffix.lower()
    media_types = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp"
    }
    media_type = media_types.get(suffix, "image/jpeg")

    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    payload = {
        "model": MODEL,
        "max_tokens": 100,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data
                        }
                    },
                    {
                        "type": "text",
                        "text": PROMPT
                    }
                ]
            }
        ]
    }

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    slug = data["content"][0]["text"].strip().lower()
    # Nettoyage : on s'assure que c'est bien un slug
    import re
    slug = re.sub(r"[^a-z0-9\-]", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


# ── Traitement d'un fichier ──────────────────────────────────────────────────
def process_file(image_path: Path, api_key: str):
    if not image_path.exists():
        dialog(f"Fichier introuvable :\n{image_path.name}")
        return

    valid_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    if image_path.suffix.lower() not in valid_exts:
        dialog(f"Format non supporté : {image_path.suffix}\n({image_path.name})")
        return

    try:
        slug = get_slug_from_image(image_path, api_key)
    except Exception as e:
        dialog(f"Erreur API pour {image_path.name} :\n{str(e)[:200]}")
        return

    while True:
        confirmed = dialog_yesno(
            f"Fichier : {image_path.name}\n\nSlug proposé :\n{slug}\n\nValider ce nom ?"
        )
        if confirmed:
            webp_path = image_path.parent / (slug + ".webp")
            try:
                img = Image.open(image_path)
                img.save(webp_path, "WEBP", quality=85)
                image_path.unlink()  # supprime l'original
            except Exception as e:
                dialog(f"Erreur conversion WebP :\n{str(e)[:200]}\nFichier original conservé.")
                new_name = image_path.parent / (slug + image_path.suffix.lower())
                image_path.rename(new_name)
            break
        else:
            # Proposer de régénérer ou saisir manuellement
            script = '''
                set result to display dialog "Que veux-tu faire ?" ¬
                    buttons {"Quitter", "Saisir manuellement", "Régénérer"} ¬
                    default button "Régénérer" with title "Talisman SEO Renamer"
                return button returned of result
            '''
            r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            choice = r.stdout.strip()

            if choice == "Régénérer":
                try:
                    slug = get_slug_from_image(image_path, api_key)
                except Exception as e:
                    dialog(f"Erreur API :\n{str(e)[:200]}")
                    return
            elif choice == "Saisir manuellement":
                manual = dialog_input("Entre le slug manuellement :", default=slug)
                if manual:
                    import re
                    slug = re.sub(r"[^a-z0-9\-]", "-", manual.lower())
                    slug = re.sub(r"-+", "-", slug).strip("-")
            else:
                # Quitter = on skip ce fichier
                break


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    files = sys.argv[1:]

    if not files:
        dialog("Glisse des images sur l'icône dans le Dock pour les renommer.")
        return

    api_key = get_api_key()
    if not api_key:
        dialog("Clé API manquante. Abandon.")
        return

    for f in files:
        process_file(Path(f), api_key)

    dialog(f"{len(files)} image(s) traitée(s). C'est fini !")


if __name__ == "__main__":
    main()
