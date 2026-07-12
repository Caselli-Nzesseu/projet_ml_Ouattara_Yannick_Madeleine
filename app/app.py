from flask import Flask, render_template, request

app = Flask(__name__)

# Données factices simulant le futur retour du scraper de Yannick
PRODUITS_FACTICES = [
    {
        "nom": "Coca-Cola bouteille plastique 1.5L",
        "prix": "1 200 FCFA",
        "image_url": "https://placehold.co/300x300/1565C0/white?text=Produit+1",
    },
    {
        "nom": "Coca-Cola canette 33cl",
        "prix": "500 FCFA",
        "image_url": "https://placehold.co/300x300/F5B700/white?text=Produit+2",
    },
    {
        "nom": "Coca-Cola pack de 6 bouteilles verre",
        "prix": "3 500 FCFA",
        "image_url": "https://placehold.co/300x300/2E7D32/white?text=Produit+3",
    },
    {
        "nom": "Coca-Cola Zero bouteille plastique 1L",
        "prix": "900 FCFA",
        "image_url": "https://placehold.co/300x300/6D4C33/white?text=Produit+4",
    },
]

# Mapping temporaire — sera remplacé par model.predict.predire_consigne_tri
MAPPING_TEMP = {
    "poubelle": "Poubelle JAUNE",
    "couleur_classe": "jaune",
    "confiance": 87,
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/rechercher", methods=["POST"])
def rechercher():
    requete = request.form.get("produit", "")

    # TODO : remplacer par l'appel réel au scraper de Yannick
    # produits = scraper.jumia_scraper.rechercher_produits(requete)
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

    # TODO : brancher ici le modèle d'Ouattara
    # resultat = model.predict.predire_consigne_tri(image_url, nom_produit)

    return render_template(
        "resultat.html",
        nom_produit=nom_produit,
        poubelle=MAPPING_TEMP["poubelle"],
        couleur_classe=MAPPING_TEMP["couleur_classe"],
        confiance=MAPPING_TEMP["confiance"],
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8501)

@app.route("/rechercher", methods=["POST"])
def rechercher():
    nom_produit = request.form.get("produit", "")

    # TODO : brancher ici le scraper de Yannick (résultats Jumia)
    # TODO : brancher ici le modèle d'Ouattara (model.predict.predire_consigne_tri)

    return render_template(
        "resultat.html",
        nom_produit=nom_produit,
        poubelle=MAPPING_TEMP["poubelle"],
        couleur_classe=MAPPING_TEMP["couleur_classe"],
        confiance=MAPPING_TEMP["confiance"],
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8501)