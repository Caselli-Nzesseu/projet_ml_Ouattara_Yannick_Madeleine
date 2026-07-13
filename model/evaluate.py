"""
EcoSort-Search — Bloc A : évaluation du modèle.
Rapport de classification + matrice de confusion sur le jeu de validation.

Usage : python evaluate.py --data_dir ./data/garbage_classification
"""

import argparse

import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

IMG_SIZE = (224, 224)

parser = argparse.ArgumentParser()
parser.add_argument("--data_dir", required=True)
parser.add_argument("--model", default="modele_eco_sort_v2.h5")
args = parser.parse_args()

# Même split et même seed que train.py -> même jeu de validation
val_ds = tf.keras.utils.image_dataset_from_directory(
    args.data_dir,
    validation_split=0.2,
    subset="validation",
    seed=42,
    image_size=IMG_SIZE,
    batch_size=32,
    label_mode="categorical",
    shuffle=True,
)
class_names = val_ds.class_names

model = tf.keras.models.load_model(args.model)

y_true, y_pred = [], []
for images, labels in val_ds:
    # pixels bruts : la normalisation est intégrée dans le modèle (Rescaling)
    probas = model.predict(images, verbose=0)
    y_true.extend(np.argmax(labels.numpy(), axis=1))
    y_pred.extend(np.argmax(probas, axis=1))

print(classification_report(y_true, y_pred, target_names=class_names))

cm = confusion_matrix(y_true, y_pred)
fig, ax = plt.subplots(figsize=(7, 6))
ax.imshow(cm, cmap="Blues")
ax.set_xticks(range(len(class_names)))
ax.set_xticklabels(class_names, rotation=45, ha="right")
ax.set_yticks(range(len(class_names)))
ax.set_yticklabels(class_names)
for i in range(len(class_names)):
    for j in range(len(class_names)):
        ax.text(j, i, cm[i, j], ha="center", va="center",
                color="white" if cm[i, j] > cm.max() / 2 else "black")
ax.set_xlabel("Prédit")
ax.set_ylabel("Réel")
ax.set_title("Matrice de confusion — validation")
plt.tight_layout()
plt.savefig("confusion_matrix.png", dpi=150)
print("→ confusion_matrix.png sauvegardée (à inclure dans le README)")
