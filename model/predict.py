"""
EcoSort-Search — Bloc A : prédiction + mapping vers les 5 catégories de tri.

Ce module est conçu pour être importé directement par le Bloc C (app de
Madeleine) : `from model.predict import predire_consigne_tri`.

Usage en ligne de commande (test rapide) :
    python predict.py chemin/vers/image.jpg
"""

import json
import sys

import numpy as np
import tensorflow as tf

IMG_SIZE = (224, 224)
# NB : la normalisation (x/127.5 - 1) est intégrée DANS le modèle (couche
# Rescaling). On donne donc au modèle des pixels bruts 0-255, jamais
# d'image déjà normalisée — sinon double normalisation et prédictions fausses.

# Mapping officiel du sujet : classe du dataset -> (poubelle, couleur UI, hexa)
MAPPING_TRI = {
    "plastic":   {"poubelle": "Poubelle JAUNE",         "couleur": "jaune",  "hex": "#FFD500"},
    "metal":     {"poubelle": "Poubelle JAUNE",         "couleur": "jaune",  "hex": "#FFD500"},
    "cardboard": {"poubelle": "Poubelle JAUNE",         "couleur": "jaune",  "hex": "#FFD500"},
    "glass":     {"poubelle": "Poubelle VERTE",         "couleur": "vert",   "hex": "#2E8B57"},
    "paper":     {"poubelle": "Poubelle BLEUE",         "couleur": "bleu",   "hex": "#1E90FF"},
    "trash":     {"poubelle": "Poubelle MARRON/NOIRE",  "couleur": "marron", "hex": "#5C4033"},
}

# Le bac D3E (électronique) n'existe pas dans le dataset Kaggle :
# le sujet autorise une détection par mots-clés (sur le nom du produit scrapé).
MOTS_CLES_D3E = [
    "phone", "smartphone", "téléphone", "telephone", "écouteur", "ecouteur",
    "earbud", "casque", "chargeur", "charger", "batterie", "battery", "pile",
    "mixeur", "blender", "montre", "watch", "laptop", "ordinateur", "tablette",
    "tablet", "tv", "télévision", "television", "câble", "cable", "usb",
    "enceinte", "speaker", "ventilateur", "fer à repasser", "micro-onde",
]

CONSIGNE_D3E = {"poubelle": "Bac Électronique (D3E)", "couleur": "gris", "hex": "#808080"}

_model = None
_labels = None


def charger_modele(model_path="modele_eco_sort.h5", labels_path="labels.json"):
    """Charge le modèle une seule fois (lazy loading)."""
    global _model, _labels
    if _model is None:
        _model = tf.keras.models.load_model(model_path)
        with open(labels_path, encoding="utf-8") as f:
            _labels = json.load(f)
    return _model, _labels


def est_electronique(nom_produit: str) -> bool:
    """Détection D3E par mots-clés sur le nom du produit (venant du scraper)."""
    nom = nom_produit.lower()
    return any(mot in nom for mot in MOTS_CLES_D3E)


def predire_consigne_tri(image_path: str, nom_produit: str = "",
                         model_path="modele_eco_sort.h5",
                         labels_path="labels.json") -> dict:
    """
    Point d'entrée principal pour le Bloc C.

    Retourne un dict :
    {
        "classe": "plastic",
        "confiance": 0.93,
        "poubelle": "Poubelle JAUNE",
        "couleur": "jaune",
        "hex": "#FFD500"
    }
    """
    # 1. Priorité au D3E si le nom du produit est électronique
    if nom_produit and est_electronique(nom_produit):
        return {"classe": "electronique", "confiance": 1.0, **CONSIGNE_D3E}

    # 2. Sinon, classification par le modèle
    model, labels = charger_modele(model_path, labels_path)

    img = tf.keras.utils.load_img(image_path, target_size=IMG_SIZE)
    arr = tf.keras.utils.img_to_array(img)  # pixels bruts 0-255
    arr = np.expand_dims(arr, axis=0)

    probas = model.predict(arr, verbose=0)[0]
    idx = int(np.argmax(probas))
    classe = labels[idx]

    return {
        "classe": classe,
        "confiance": float(probas[idx]),
        **MAPPING_TRI[classe],
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python predict.py <image.jpg> [nom_du_produit]")
        sys.exit(1)
    nom = sys.argv[2] if len(sys.argv) > 2 else ""
    resultat = predire_consigne_tri(sys.argv[1], nom)
    print(json.dumps(resultat, indent=2, ensure_ascii=False))
