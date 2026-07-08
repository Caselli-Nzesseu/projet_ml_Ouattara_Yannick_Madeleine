# EcoSort-Search

Application web d'aide au tri sélectif combinant deep learning et scraping.

## Équipe
- Madeleine
- Ouattara
- Yannick

## Structure du projet
- `model/` : entraînement du modèle de classification (Jalon 1)
- `scraper/` : scraping du site Jumia (Jalon 2)
- `app/` : application web Streamlit/Flask
- `notebooks/` : exploration et tests

## Lancer le projet
\`\`\`bash
docker build -t ecosort .
docker run -p 8501:8501 ecosort
\`\`\`
