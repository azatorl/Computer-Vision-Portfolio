
from pathlib import Path
import shutil
import random

BASE = Path.home() / "teknofest_yolo"

# FINAL
FINAL_LABELS = Path.home() / "Downloads/final/labels/train"
DATASETS2 = BASE / "datasets2"

# Rocket
ROCKET_IMAGES = BASE / "dataset/images/train"
ROCKET_LABELS = BASE / "models/rocket_son/labels/train"

# Output
OUT = BASE / "merged_dataset"

for split in ["train", "val"]:
    (OUT / "images" / split).mkdir(parents=True, exist_ok=True)
    (OUT / "labels" / split).mkdir(parents=True, exist_ok=True)


def image_map(folder):
    result = {}
    for p in folder.rglob("*"):
        if p.is_file() and p.suffix.lower() in [".jpg", ".jpeg", ".png"]:
            result[p.stem] = p
    return result


# --------------------------------------------------
# IMAGE MAPS
# --------------------------------------------------

f16_images = image_map(DATASETS2 / "f16/foto_f16")
drone_images = image_map(DATASETS2 / "drone/images")
heli_images = image_map(DATASETS2 / "helicopter/images")

rocket_images = image_map(ROCKET_IMAGES)


# --------------------------------------------------
# DATA PAIRS
# --------------------------------------------------

pairs = []


# F16 = *_2.txt
for label in FINAL_LABELS.glob("*_2.txt"):
    stem = label.stem[:-2]  # _2 sil

    if stem in f16_images:
        pairs.append(("f16", f16_images[stem], label))


# Drone = *_1.txt
for label in FINAL_LABELS.glob("*_1.txt"):
    stem = label.stem[:-2]  # _1 sil

    if stem in drone_images:
        pairs.append(("drone", drone_images[stem], label))


# Helicopter = normal .txt
for label in FINAL_LABELS.glob("*.txt"):

    if label.name.endswith("_1.txt"):
        continue

    if label.name.endswith("_2.txt"):
        continue

    stem = label.stem

    if stem in heli_images:
        pairs.append(("helicopter", heli_images[stem], label))


# Rocket
for label in ROCKET_LABELS.glob("*.txt"):
    stem = label.stem

    if stem in rocket_images:
        pairs.append(("rocket", rocket_images[stem], label))


print()
print("=" * 50)
print("EŞLEŞMELER")
print("=" * 50)

from collections import Counter

counts = Counter(x[0] for x in pairs)

for name in ["f16", "drone", "helicopter", "rocket"]:
    print(f"{name:12}: {counts[name]}")


# --------------------------------------------------
# SHUFFLE
# --------------------------------------------------

random.seed(42)
random.shuffle(pairs)


# %90 TRAIN / %10 VAL
split = int(len(pairs) * 0.90)

train_pairs = pairs[:split]
val_pairs = pairs[split:]


# --------------------------------------------------
# COPY
# --------------------------------------------------

def copy_pairs(data, split_name):

    img_dir = OUT / "images" / split_name
    lbl_dir = OUT / "labels" / split_name

    for i, (source, image, label) in enumerate(data):

        new_name = f"{source}_{i:06d}"

        new_image = img_dir / f"{new_name}{image.suffix.lower()}"
        new_label = lbl_dir / f"{new_name}.txt"

        shutil.copy2(image, new_image)
        shutil.copy2(label, new_label)


print()
print("Train kopyalanıyor...")
copy_pairs(train_pairs, "train")

print("Validation kopyalanıyor...")
copy_pairs(val_pairs, "val")


# --------------------------------------------------
# DATA.YAML
# --------------------------------------------------

yaml = f"""path: {OUT}

train: images/train
val: images/val

names:
  0: Rocket
  1: Balon
  2: F16
  3: Dron
  4: Helicopter
"""

with open(OUT / "data.yaml", "w") as f:
    f.write(yaml)


print()
print("=" * 50)
print("MERGE TAMAMLANDI")
print("=" * 50)

print(f"Toplam görüntü : {len(pairs)}")
print(f"Train          : {len(train_pairs)}")
print(f"Val            : {len(val_pairs)}")

print()
print("Dataset:")
print(OUT)

print()
print("Data YAML:")
print(OUT / "data.yaml")
