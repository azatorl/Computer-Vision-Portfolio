import os
import random
import shutil

random.seed(42)

IMAGE_DIR = "/home/azat/teknofest_yolo/datasets2/rocket/rocket_dataset/images"
LABEL_DIR = "/home/azat/teknofest_yolo/models/rocket_son/labels/train"

OUT = "/home/azat/teknofest_yolo/dataset"

TRAIN_RATIO = 0.9

images = [f for f in os.listdir(IMAGE_DIR)
          if f.lower().endswith((".jpg", ".jpeg", ".png"))]

random.shuffle(images)

split = int(len(images) * TRAIN_RATIO)

train = images[:split]
val = images[split:]


def copy_files(file_list, img_dst, lbl_dst):
    for img in file_list:
        name = os.path.splitext(img)[0]

        img_src = os.path.join(IMAGE_DIR, img)
        lbl_src = os.path.join(LABEL_DIR, name + ".txt")

        shutil.copy2(img_src, os.path.join(img_dst, img))

        if os.path.exists(lbl_src):
            shutil.copy2(lbl_src,
                         os.path.join(lbl_dst, name + ".txt"))


copy_files(
    train,
    os.path.join(OUT, "images/train"),
    os.path.join(OUT, "labels/train")
)

copy_files(
    val,
    os.path.join(OUT, "images/val"),
    os.path.join(OUT, "labels/val")
)

print("Toplam :", len(images))
print("Train  :", len(train))
print("Val    :", len(val))
print("Dataset hazir.")
