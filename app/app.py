from flask import Flask, render_template, request

app = Flask(__name__)

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