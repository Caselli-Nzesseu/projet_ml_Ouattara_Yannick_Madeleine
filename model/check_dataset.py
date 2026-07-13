"""check_dataset.py — vérifie la structure du dataset et compte les images.

Usage : python check_dataset.py [chemin_du_dataset]
"""
import os
import sys

DATA_DIR = sys.argv[1] if len(sys.argv) > 1 else "data/garbage_classification"
CLASSES_ATTENDUES = {"cardboard", "glass", "metal", "paper", "plastic", "trash"}

if not os.path.isdir(DATA_DIR):
    print(f"❌ Dossier introuvable : {DATA_DIR}")
    sys.exit(1)

dossiers = {d for d in os.listdir(DATA_DIR)
            if os.path.isdir(os.path.join(DATA_DIR, d))}

manquantes = CLASSES_ATTENDUES - dossiers
if manquantes:
    print(f"❌ Classes manquantes : {sorted(manquantes)}")
    print("   Astuce : le zip Kaggle crée parfois un niveau de dossier en plus")
    print("   (ex: 'Garbage classification/Garbage classification/'). Vérifie le chemin.")
    sys.exit(1)

total = 0
for classe in sorted(CLASSES_ATTENDUES):
    n = len([f for f in os.listdir(os.path.join(DATA_DIR, classe))
             if f.lower().endswith((".jpg", ".jpeg", ".png"))])
    total += n
    print(f"  {classe:<10} : {n} images")

print(f"\n✅ Structure OK — total : {total} images (attendu : ~2 500)")
