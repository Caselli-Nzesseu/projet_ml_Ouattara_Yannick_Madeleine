"""
EcoSort-Search — Bloc A : Entraînement du modèle IA (Jalon 1)
Responsable : Ouattara | Doublure : Madeleine

Transfer Learning avec MobileNetV2 (Keras/TensorFlow) sur le dataset
Kaggle "Garbage Classification" (6 classes : cardboard, glass, metal,
paper, plastic, trash).

Usage :
    python train.py --data_dir ./data/garbage_classification --epochs 15

Livrable : modele_eco_sort.h5 + labels.json
"""

import argparse
import json
import os

import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2

IMG_SIZE = (224, 224)


def build_datasets(data_dir, batch_size, seed=42):
    """Charge les images depuis data_dir (un sous-dossier par classe)."""
    train_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="training",
        seed=seed,
        image_size=IMG_SIZE,
        batch_size=batch_size,
        label_mode="categorical",
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="validation",
        seed=seed,
        image_size=IMG_SIZE,
        batch_size=batch_size,
        label_mode="categorical",
    )
    class_names = train_ds.class_names
    print(f"Classes détectées : {class_names}")

    autotune = tf.data.AUTOTUNE
    train_ds = train_ds.prefetch(autotune)
    val_ds = val_ds.prefetch(autotune)
    return train_ds, val_ds, class_names


def build_model(num_classes):
    """MobileNetV2 pré-entraîné sur ImageNet + tête de classification."""
    data_augmentation = tf.keras.Sequential(
        [
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.1),
            layers.RandomZoom(0.1),
        ],
        name="augmentation",
    )

    base_model = MobileNetV2(
        input_shape=IMG_SIZE + (3,),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False  # Phase 1 : on gèle le backbone

    inputs = tf.keras.Input(shape=IMG_SIZE + (3,))
    x = data_augmentation(inputs)
    # Normalisation MobileNetV2 (x/127.5 - 1) en couche standard sérialisable
    # (surtout PAS preprocess_input en op brute : le .h5 ne se recharge pas)
    x = layers.Rescaling(1.0 / 127.5, offset=-1.0, name="preprocessing")(x)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="dense")(x)

    model = tf.keras.Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model, base_model


def fine_tune(model, base_model, train_ds, val_ds, epochs):
    """Phase 2 : dégèle les dernières couches du backbone (fine-tuning)."""
    base_model.trainable = True
    # On ne dégèle que les ~30 dernières couches pour éviter l'overfitting
    for layer in base_model.layers[:-30]:
        layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model.fit(train_ds, validation_data=val_ds, epochs=epochs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", required=True,
                        help="Dossier du dataset (un sous-dossier par classe)")
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--fine_tune_epochs", type=int, default=5)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--output", default="modele_eco_sort.h5")
    args = parser.parse_args()

    train_ds, val_ds, class_names = build_datasets(args.data_dir, args.batch_size)
    model, base_model = build_model(num_classes=len(class_names))
    model.summary()

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=4, restore_best_weights=True
        ),
        tf.keras.callbacks.ModelCheckpoint(
            "checkpoint_best.h5", monitor="val_accuracy", save_best_only=True
        ),
    ]

    # --- Phase 1 : entraînement de la tête seulement ---
    print("\n=== Phase 1 : entraînement de la tête (backbone gelé) ===")
    model.fit(train_ds, validation_data=val_ds,
              epochs=args.epochs, callbacks=callbacks)

    # --- Phase 2 : fine-tuning léger ---
    if args.fine_tune_epochs > 0:
        print("\n=== Phase 2 : fine-tuning des dernières couches ===")
        fine_tune(model, base_model, train_ds, val_ds, args.fine_tune_epochs)

    # --- Évaluation finale ---
    loss, acc = model.evaluate(val_ds)
    print(f"\nAccuracy validation finale : {acc:.2%}")

    # --- Sauvegarde des livrables ---
    model.save(args.output)
    with open("labels.json", "w", encoding="utf-8") as f:
        json.dump(class_names, f, ensure_ascii=False, indent=2)
    print(f"Modèle sauvegardé : {args.output}")
    print("Labels sauvegardés : labels.json")


if __name__ == "__main__":
    main()
