from pathlib import Path
import shutil
import random
from collections import Counter

BASE = Path.home() / "teknofest_yolo"

# FINAL dataset
FINAL = Path.home() / "Downloads" / "final"

# Eski Rocket dataset
ROCKET_IMAGES = BASE / "dataset" / "images" / "train"
ROCKET_LABELS = BASE / "models" / "rocket_son" / "labels" / "train"

# Yeni dataset
OUT = BASE / "merged_dataset"

TRAIN_IMG = OUT / "images" / "train"
VAL_IMG = OUT / "images" / "val"
TRAIN_LBL = OUT / "labels" / "train"
VAL_LBL = OUT / "labels" / "val"

for d in [TRAIN_IMG, VAL_IMG, TRAIN_LBL, VAL_LBL]:
    d.mkdir(parents=True, exist_ok=True)


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}


def find_images(root):
    result = {}

    for p in root.rglob("*"):
        if p.is_file() and p.suffix in IMAGE_EXTS:
            result.setdefault(p.stem, []).append(p)

    return result


def find_labels(root):
    result = {}

    for p in root.rglob("*.txt"):
        result.setdefault(p.stem, []).append(p)

    return result


print("\nFINAL görüntüleri aranıyor...")
final_images = find_images(FINAL)

print("FINAL label'ları aranıyor...")
final_labels = find_labels(FINAL / "labels")

print(f"FINAL görüntü stem sayısı : {len(final_images)}")
print(f"FINAL label stem sayısı   : {len(final_labels)}")


print("\nRocket görüntüleri aranıyor...")
rocket_images = find_images(ROCKET_IMAGES)

print("Rocket label'ları aranıyor...")
rocket_labels = find_labels(ROCKET_LABELS)

print(f"Rocket görüntü sayısı : {len(rocket_images)}")
print(f"Rocket label sayısı   : {len(rocket_labels)}")


# ---------------------------------------------------------
# FINAL DATASET
# ---------------------------------------------------------

final_pairs = []

for stem, labels in final_labels.items():

    if stem not in final_images:
        print(f"[UYARI] FINAL görüntü bulunamadı: {stem}")
        continue

    if len(labels) > 1:
        print(f"[UYARI] Birden fazla label bulundu: {stem}")
        continue

    image = final_images[stem][0]
    label = labels[0]

    final_pairs.append((image, label))


# ---------------------------------------------------------
# ROCKET DATASET
# ---------------------------------------------------------

rocket_pairs = []

for stem, labels in rocket_labels.items():

    if stem not in rocket_images:
        print(f"[UYARI] Rocket görüntü bulunamadı: {stem}")
        continue

    if len(labels) > 1:
        print(f"[UYARI] Birden fazla Rocket label bulundu: {stem}")
        continue

    image = rocket_images[stem][0]
    label = labels[0]

    rocket_pairs.append((image, label))


print("\n--------------------------------")
print("EŞLEŞTİRME SONUCU")
print("--------------------------------")

print("FINAL eşleşen       :", len(final_pairs))
print("Rocket eşleşen      :", len(rocket_pairs))


# ---------------------------------------------------------
# TÜM VERİYİ BİRLEŞTİR
# ---------------------------------------------------------

all_pairs = []

# FINAL
for image, label in final_pairs:
    all_pairs.append(("final", image, label))

# Rocket
for image, label in rocket_pairs:
    all_pairs.append(("rocket", image, label))


# Karıştır
random.seed(42)
random.shuffle(all_pairs)


# %90 train / %10 validation
split_index = int(len(all_pairs) * 0.90)

train_data = all_pairs[:split_index]
val_data = all_pairs[split_index:]


def copy_dataset(data, img_dir, lbl_dir):

    class_counter = Counter()
    copied = 0

    for index, (source, image, label) in enumerate(data):

        # Dosya isim çakışmasını önlemek için prefix
        new_name = f"{source}_{index:06d}"

        new_image = img_dir / f"{new_name}{image.suffix.lower()}"
        new_label = lbl_dir / f"{new_name}.txt"

        shutil.copy2(image, new_image)
        shutil.copy2(label, new_label)

        # Class dağılımını hesapla
        try:
            with open(label, "r") as f:
                for line in f:
                    parts = line.strip().split()

                    if parts:
                        class_id = int(parts[0])
                        class_counter[class_id] += 1

        except Exception as e:
            print(f"[UYARI] Label okunamadı: {label} -> {e}")

        copied += 1

    return copied, class_counter


print("\nTrain verileri kopyalanıyor...")
train_count, train_classes = copy_dataset(
    train_data,
    TRAIN_IMG,
    TRAIN_LBL
)

print("Validation verileri kopyalanıyor...")
val_count, val_classes = copy_dataset(
    val_data,
    VAL_IMG,
    VAL_LBL
)


# ---------------------------------------------------------
# DATA.YAML
# ---------------------------------------------------------

yaml_text = f"""path: {OUT}

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
    f.write(yaml_text)


print("\n================================")
print("BİRLEŞTİRME TAMAMLANDI")
print("================================")

print(f"Train görüntü : {train_count}")
print(f"Val görüntü   : {val_count}")
print(f"Toplam        : {train_count + val_count}")

print("\nTRAIN CLASS DAĞILIMI:")
for k in sorted(train_classes):
    print(f"class {k}: {train_classes[k]}")

print("\nVAL CLASS DAĞILIMI:")
for k in sorted(val_classes):
    print(f"class {k}: {val_classes[k]}")

print("\nDataset:")
print(OUT)

print("\ndata.yaml:")
print(OUT / "data.yaml")
