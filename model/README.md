# Bloc A — Modèle IA (EcoSort-Search)

## Ce que fait ce bloc
Transfer Learning MobileNetV2 (Keras/TensorFlow) sur le dataset Kaggle
Garbage Classification (6 classes : cardboard, glass, metal, paper, plastic,
trash), mappé vers les 5 catégories de tri du sujet.

## Installation
pip install -r requirements-model.txt

## Entraîner (reproduit le modèle livré)
python train.py --data_dir "./data/Garbage classification/Garbage classification" --epochs 15 --fine_tune_epochs 5
Entraînement réalisé sur Google Colab (GPU T4), ~5 min.

## Évaluer
python evaluate.py --data_dir "./data/Garbage classification/Garbage classification" --model modele_eco_sort.h5

## Prédire
python predict.py image.jpg "nom du produit"

## Résultats
- Accuracy validation : 84.95 %
- Matrice de confusion : voir confusion_matrix.png

## Interface pour l'app (Bloc C)
from model.predict import predire_consigne_tri
Retourne un dict : classe, confiance, poubelle, couleur, hex.
La détection D3E se fait par mots-clés sur le nom du produit (pas de classe
électronique dans le dataset, approche autorisée par le sujet).

## Limites connues
- Modèle entraîné sur des photos de déchets ; les images Jumia sont des
  photos produits (fond blanc). Compensé par les mots-clés D3E.
- La normalisation (Rescaling x/127.5 - 1) est intégrée DANS le modèle :
  lui fournir des pixels bruts 0-255, jamais d'image déjà normalisée.
