"""
EcoSort-Search — Scraper Jumia
Recherche un mot-clé sur Jumia et extrait les produits correspondants.
"""

import requests
from bs4 import BeautifulSoup

JUMIA_BASE_URL = "https://www.jumia.ci"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


def search_jumia(keyword: str, max_results: int = 5):
    url = f"{JUMIA_BASE_URL}/catalog/?q={keyword}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Erreur lors de la requete vers Jumia : {e}")
        return []

    print("Status code:", response.status_code)

    soup = BeautifulSoup(response.text, "html.parser")
    cartes = soup.select("article.prd")
    print("Nombre de cartes trouvees:", len(cartes))

    produits = []

    for carte in cartes[:max_results]:
        lien_tag = carte.select_one("a.core")
        nom_tag = carte.select_one("h3.name")
        prix_tag = carte.select_one("div.prc")
        img_tag = carte.select_one("img.img")

        if not (lien_tag and nom_tag):
            continue

        nom = nom_tag.get_text(strip=True)
        prix = prix_tag.get_text(strip=True) if prix_tag else "Prix inconnu"
        lien = JUMIA_BASE_URL + lien_tag.get("href", "")
        image = img_tag.get("data-src", "") if img_tag else ""

        produits.append({
            "nom": nom,
            "prix": prix,
            "lien": lien,
            "image": image,
        })

    return produits

def download_image(image_url: str, save_path: str = "produit_image.jpg"):
    """Telecharge l'image d'un produit et la sauvegarde localement.
    Renvoie True si succes, False sinon (sans jamais planter)."""
    if not image_url:
        print("Aucune URL d'image fournie.")
        return False

    try:
        response = requests.get(image_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Erreur lors du telechargement de l'image : {e}")
        return False

    with open(save_path, "wb") as f:
        f.write(response.content)

    print(f"Image telechargee et sauvegardee dans {save_path}")
    return True

if __name__ == "__main__":
    resultats = search_jumia("bouteille eau")
    print(f"\n--- {len(resultats)} produits extraits ---\n")
    for p in resultats:
        print(f"Nom   : {p['nom']}")
        print(f"Prix  : {p['prix']}")
        print(f"Lien  : {p['lien']}")
        print(f"Image : {p['image']}")
        print("-" * 50)

  