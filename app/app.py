import os
import sys
import tempfile

import requests
from flask import Flask, render_template, request

# Permet d'importer le module model/ situé au niveau du dossier parent
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from model.predict import predire_consigne_tri  # noqa: E402

app = Flask(__name__)

# Données factices simulant le futur retour du scraper de Yannick
PRODUITS_FACTICES = [
    {
        "nom": "Coca-Cola bouteille plastique 1.5L",
        "prix": "1 200 FCFA",
        "image_url": "https://placehold.co/300x300/1565C0/white.png?text=Produit+1",
    },
    {
        "nom": "Coca-Cola canette 33cl",
        "prix": "500 FCFA",
        "image_url": "https://placehold.co/300x300/F5B700/white.png?text=Produit+2",
    },
    {
        "nom": "Coca-Cola pack de 6 bouteilles verre",
        "prix": "3 500 FCFA",
        "image_url": "https://placehold.co/300x300/2E7D32/white.png?text=Produit+3",
    },
    {
        "nom": "Coca-Cola Zero bouteille plastique 1L",
        "prix": "900 FCFA",
        "image_url": "https://placehold.co/300x300/6D4C33/white.png?text=Produit+4",
    },
]


def telecharger_image_temp(image_url: str) -> str:
    """Télécharge une image depuis une URL vers un fichier temporaire local."""
    reponse = requests.get(image_url, timeout=10)
    reponse.raise_for_status()

    fichier_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    fichier_temp.write(reponse.content)
    fichier_temp.close()
    return fichier_temp.name


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/rechercher", methods=["POST"])
def rechercher():
    requete = request.form.get("produit", "")

    # TODO : remplacer par l'appel réel au scraper de Yannick
    produits = PRODUITS_FACTICES

    return render_template(
        "resultats_recherche.html",
        requete=requete,
        produits=produits,
    )


@app.route("/choisir", methods=["POST"])
def choisir():
    nom_produit = request.form.get("nom_produit", "")
    image_url = request.form.get("image_url", "")

    chemin_image_temp = None
    try:
        chemin_image_temp = telecharger_image_temp(image_url)
        resultat = predire_consigne_tri(chemin_image_temp, nom_produit)
        print("Résultat brut du modèle :", resultat)
    except Exception as e:
        print(f"Erreur lors de la prediction : {e}")
        resultat = {
            "poubelle": "Erreur d'analyse",
            "couleur": "gris",
            "confiance": 0,
        }
    finally:
        if chemin_image_temp and os.path.exists(chemin_image_temp):
            os.remove(chemin_image_temp)

    return render_template(
        "resultat.html",
        nom_produit=nom_produit,
        poubelle=resultat["poubelle"],
        couleur_classe=resultat["couleur"],
        confiance=resultat["confiance"],
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8501)