import os
import sys
import tempfile

import requests
from flask import Flask, render_template, request

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from model.predict import predire_consigne_tri  # noqa: E402
from scraper.jumia_scraper import search_jumia  # noqa: E402

app = Flask(__name__)


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

    resultats_bruts = search_jumia(requete)

    # Normalisation des clés du scraper (nom, prix, lien, image)
    # vers celles attendues par le template (nom, prix, image_url)
    produits = [
        {
            "nom": p["nom"],
            "prix": p["prix"],
            "image_url": p["image"],
        }
        for p in resultats_bruts
    ]

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
        confiance=round(resultat["confiance"] * 100),
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8501)