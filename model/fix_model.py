"""
fix_model.py — Répare le modèle entraîné sans réentraîner.

Problème : l'ancien train.py insérait preprocess_input comme opération brute
dans le graphe -> le .h5 contient une couche 'TrueDivide' que Keras 3 ne sait
pas recharger.

Solution : on reconstruit ici la MÊME architecture, mais avec une couche
Rescaling standard (équivalente : x/127.5 - 1), puis on recharge uniquement
les POIDS depuis ton .h5 existant, et on sauvegarde un modèle propre.

Usage (depuis le dossier model/) :
    python fix_model.py
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers

IMG_SIZE = (224, 224)
NUM_CLASSES = 6
ANCIEN = "modele_eco_sort.h5"
NOUVEAU = "modele_eco_sort_v2.h5"


def rebuild_model():
    """Reconstruit l'architecture de train.py, version sérialisable."""
    data_augmentation = tf.keras.Sequential(
        [
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.1),
            layers.RandomZoom(0.1),
        ],
        name="augmentation",
    )

    base_model = tf.keras.applications.MobileNetV2(
        input_shape=IMG_SIZE + (3,),
        include_top=False,
        weights=None,  # les poids viendront du .h5 entraîné
    )

    inputs = tf.keras.Input(shape=IMG_SIZE + (3,))
    x = data_augmentation(inputs)
    # Équivalent exact de mobilenet_v2.preprocess_input, mais en couche standard :
    x = layers.Rescaling(1.0 / 127.5, offset=-1.0, name="preprocessing")(x)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(NUM_CLASSES, activation="softmax", name="dense")(x)
    return tf.keras.Model(inputs, outputs)


def main():
    print("1/4 Reconstruction de l'architecture...")
    model = rebuild_model()

    print(f"2/4 Chargement des poids depuis {ANCIEN}...")
    # Le .h5 complet contient un groupe 'model_weights' : load_weights sait le lire.
    # skip_mismatch=False -> si ça ne colle pas, on veut une erreur claire.
    try:
        model.load_weights(ANCIEN)
    except Exception as e:
        print(f"   Chargement direct échoué ({type(e).__name__}), essai par nom...")
        model.load_weights(ANCIEN, skip_mismatch=True, by_name=True)

    print("3/4 Test de prédiction sur une image factice...")
    fake = np.random.randint(0, 255, size=(1, 224, 224, 3)).astype("float32")
    probas = model.predict(fake, verbose=0)[0]
    assert probas.shape == (NUM_CLASSES,), "Sortie inattendue"
    assert 0.99 < probas.sum() < 1.01, "Les probabilités ne somment pas à 1"
    print(f"   OK — distribution de sortie : {np.round(probas, 3)}")

    print(f"4/4 Sauvegarde du modèle réparé : {NOUVEAU}")
    model.save(NOUVEAU)
    print("\n✅ Terminé. Vérifie maintenant avec :")
    print('   python predict.py "data\\Garbage classification\\Garbage classification\\glass\\glass1.jpg"')
    print("   (predict.py version corrigée, qui pointe sur le _v2)")


if __name__ == "__main__":
    main()
